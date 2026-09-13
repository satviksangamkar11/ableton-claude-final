"""Claude Code reasoning at the producer decision boundary.

Invokes Claude Code as the reasoning brain for capability selection.

Responsibilities:
  1. Receive admissible candidates from evidence system
  2. Call Claude Code with structured input
  3. Parse Claude's structured output
  4. Validate that Claude's selection is admissible
  5. Return validated decision artifacts

Authority rule:
  Claude reasons and selects.
  Claude does NOT authorize capabilities.
  Admissible candidates are determined by evidence system only.
  Claude's selection must be one of the admissible set.
"""

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass(frozen=True)
class ClaudeCandidate:
    """One candidate capability considered by Claude."""
    target: str
    status: str
    reason: str
    source: str  # "capability" or "episode:<id>"


@dataclass(frozen=True)
class ClaudeDecision:
    """Claude's structured selection decision."""
    candidates: List[ClaudeCandidate]
    selected: int  # index into candidates
    rationale: str
    claude_input: Optional[Dict[str, Any]] = None  # The actual input sent to Claude
    claude_output_raw: Optional[str] = None  # Raw response from Claude CLI


def prepare_claude_request(
    goal_intent: str,
    semantic_target: str,
    admissible_candidates: List[Dict[str, str]],
    retrieved_episodes: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Prepare a structured request for Claude Code decision-making.

    This function prepares the decision input in a format that Claude Code
    can process. In production, this would be sent to Claude via subprocess/MCP.
    For Step 3, this is used directly within the session.

    Args:
        goal_intent: human intent
        semantic_target: semantic target name
        admissible_candidates: list of {target, status, reason, source}
        retrieved_episodes: optional list of retrieved episode data
        context: optional contextual information

    Returns:
        Structured decision request dict
    """
    return {
        "goal_intent": goal_intent,
        "semantic_target": semantic_target,
        "admissible_candidates": admissible_candidates,
        "retrieved_episodes": retrieved_episodes or [],
        "context": context or {},
    }


def invoke_claude_for_selection(
    goal_intent: str,
    semantic_target: str,
    admissible_candidates: List[Dict[str, str]],
    retrieved_episodes: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> ClaudeDecision:
    """Invoke Claude Code to select among admissible capabilities.

    Uses the Claude CLI with structured JSON output.

    Args:
        goal_intent: human intent (e.g., "make the note sustain longer")
        semantic_target: semantic target name (e.g., "Env1.Release")
        admissible_candidates: list of {target, status, reason, source}
                               (all verified by evidence system)
        retrieved_episodes: optional list of retrieved episode data
        context: optional contextual information

    Returns:
        ClaudeDecision with candidates, selected index, and rationale

    Raises:
        ValueError: if Claude's response is invalid or inadmissible
        subprocess.CalledProcessError: if Claude invocation fails
    """
    if not admissible_candidates:
        raise ValueError("No admissible candidates provided to Claude")

    # Build the prompt for Claude
    prompt = _build_claude_prompt(
        goal_intent=goal_intent,
        semantic_target=semantic_target,
        admissible_candidates=admissible_candidates,
        retrieved_episodes=retrieved_episodes,
        context=context,
    )

    # Invoke Claude Code via CLI
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            "claude",
            output=result.stdout,
            stderr=result.stderr,
        )

    # Parse Claude's output
    stdout = result.stdout.strip()
    if not stdout:
        raise ValueError("Claude returned empty output")

    # Claude CLI wraps the response in a JSON object with metadata
    # Extract the actual Claude response from the result field
    try:
        wrapper = json.loads(stdout)
        if isinstance(wrapper, dict) and "result" in wrapper:
            # Extract the actual response from the wrapper
            result_text = wrapper["result"]
            # Claude returns markdown code blocks, extract the JSON
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', result_text, re.DOTALL)
            if json_match:
                decision_data = json.loads(json_match.group(1))
            else:
                # Try direct JSON parse
                decision_data = json.loads(result_text)
        else:
            # Assume it's direct JSON response
            decision_data = wrapper
    except json.JSONDecodeError as e:
        raise ValueError("Claude returned unparseable JSON: {}".format(stdout)) from e

    # Construct the input that was sent for audit
    claude_input = {
        "goal_intent": goal_intent,
        "semantic_target": semantic_target,
        "admissible_candidates": admissible_candidates,
        "retrieved_episodes": retrieved_episodes or [],
        "context": context or {},
    }

    # Validate and construct ClaudeDecision
    decision = _validate_claude_decision(
        decision_data,
        admissible_candidates,
    )

    # Attach input and output for audit trail
    return ClaudeDecision(
        candidates=decision.candidates,
        selected=decision.selected,
        rationale=decision.rationale,
        claude_input=claude_input,
        claude_output_raw=stdout,
    )


def _build_claude_prompt(
    goal_intent: str,
    semantic_target: str,
    admissible_candidates: List[Dict[str, str]],
    retrieved_episodes: Optional[List[Dict[str, Any]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """Build the prompt to send to Claude."""
    prompt = f"""You are selecting among provided admissible production candidates.

IMPORTANT RULES:
1. You may NOT invent capabilities.
2. You may NOT change capability authority.
3. You must return structured JSON.
4. You must choose exactly one candidate.
5. The selected candidate must be one of the provided admissible candidates.
6. You must explain why the selected candidate best addresses the goal.

GOAL:
  Human intent: {goal_intent}
  Semantic target: {semantic_target}

ADMISSIBLE CANDIDATES:
"""
    for i, cand in enumerate(admissible_candidates):
        if "magnitude" in cand:
            prompt += f"""
  [{i}] {cand['target']}, direction={cand.get('direction', '+1')}, magnitude={cand.get('magnitude', '?'):+.2f} (resultant: {cand.get('resultant', '?')})
      Status: {cand['status']}
      Reason: {cand['reason']}
      Source: {cand['source']}
"""
        else:
            prompt += f"""
  [{i}] {cand['target']}
      Status: {cand['status']}
      Reason: {cand['reason']}
      Source: {cand['source']}
"""

    if retrieved_episodes:
        prompt += f"\nRETRIEVED EPISODES:\n"
        for ep in retrieved_episodes:
            ep_id = ep.get("episode_id", "unknown")
            ep_target = ep.get("semantic_target", "unknown")
            ep_outcome = ep.get("decision", {}).get("accepted", False)
            ep_magnitude = ep.get("diagnosis", {}).get("mutation_magnitude")
            ep_delta = ep.get("decision", {}).get("delta")
            ep_metric = ep.get("measurement_metric", "unknown")

            details = f"{ep_target}"
            if ep_magnitude is not None:
                details += f", magnitude={ep_magnitude:+.2f}"
            if ep_delta is not None and ep_metric:
                details += f", {ep_metric}={ep_delta:+.3f}"

            prompt += f"  - {ep_id}: {details} (accepted={ep_outcome})\n"

    if context:
        prompt += f"\nCONTEXT:\n"
        for key, value in context.items():
            prompt += f"  {key}: {value}\n"

    prompt += f"""
YOUR TASK:
Select exactly one candidate by index from the list above.
Do NOT create, remove, or modify candidates.

Return ONLY this JSON object:
{{
  "selected": <int between 0 and {len(admissible_candidates)-1}>,
  "rationale": "<your explanation of why you selected this candidate>"
}}

Do NOT explain outside the JSON.
Do NOT add commentary.
Return only the JSON object.
"""
    return prompt


def _validate_claude_decision(
    decision_data: Dict[str, Any],
    admissible_candidates: List[Dict[str, str]],
) -> ClaudeDecision:
    """Validate Claude's decision against authority rules.

    Claude selects by index from the admissible candidates grid.
    Claude returns: {"selected": <int>, "rationale": "<text>"}

    Raises:
        ValueError: if decision is invalid or inadmissible
    """
    # Validate JSON structure
    if not isinstance(decision_data, dict):
        raise ValueError(f"Claude returned non-dict: {type(decision_data)}")

    if "selected" not in decision_data:
        raise ValueError("Claude response missing 'selected' field")
    if "rationale" not in decision_data:
        raise ValueError("Claude response missing 'rationale' field")

    # Validate selected index
    try:
        selected_idx = int(decision_data["selected"])
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Claude 'selected' is not an integer: {decision_data['selected']}"
        ) from e

    if selected_idx < 0 or selected_idx >= len(admissible_candidates):
        raise ValueError(
            f"Claude selected index {selected_idx} out of range [0, {len(admissible_candidates)-1}]"
        )

    # Selected index is valid; construct ClaudeDecision
    # Convert admissible_candidates to ClaudeCandidate objects for audit trail
    claude_candidates = [
        ClaudeCandidate(
            target=c.get("target", "unknown"),
            status=c.get("status", "unknown"),
            reason=c.get("reason", ""),
            source=c.get("source", "unknown"),
        )
        for c in admissible_candidates
    ]

    return ClaudeDecision(
        candidates=claude_candidates,
        selected=selected_idx,
        rationale=decision_data.get("rationale", ""),
    )
