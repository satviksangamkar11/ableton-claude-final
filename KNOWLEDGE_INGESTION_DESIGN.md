# Knowledge Ingestion from YouTube Transcripts

**Status:** Design document for Step 5 (General knowledge ingestion).

---

## Core Principle

YouTube is a **teacher**, not a pipeline. The system learns how Serum works from transcripts. It does not reproduce the video.

Later, when a human requests a sound, the system uses learned knowledge to plan operations. That is a **separate pipeline** from transcript ingestion.

---

## The Pipeline

```
YouTube URL
    ↓
Transcript ingestion (yt-dlp + MCP transcript server)
    ↓
Claude Code reads the transcript
    ↓
Discriminates:
  • Procedure ("short attack + fast decay → pluck")
  • Concept ("detune creates width")
  • Context ("only works if filter is open")
  • Filler ("Serum is powerful...")
    ↓
Structured KnowledgeItem records
    ↓
Written to knowledge graph as OBSERVATIONS
    ↓
Retrievable in future sessions
```

**Output of this pipeline:** Structured knowledge. Not audio. Not a patch. Knowledge.

---

## Understanding: What It Means

Understanding is **not a module**. It is what Claude Code does when reading a transcript:

- Distinguishes procedural statements from commentary
- Binds tutorial language to existing semantic vocabulary (`Env1.Release`, not `Env 1 Release`)
- Assigns scope (`universal`, `genre:techno`, `artist:skrillex`)
- Records provenance (which tutorial, which timestamp, which sentence)
- Marks confidence and ambiguity

This is the **knowledge acquisition** step. It happens at ingestion time. It consumes tokens once. The result is durable and free to retrieve forever.

**Example:**
```
Input: "Shorten the attack for a faster pluck response."
Output: {
  "type": "procedural",
  "semantic_target": "Env1.Attack",
  "operation": "decrease",
  "effect": "faster onset",
  "scope": "universal",
  "provenance": "tutorial_xyz:12:34",
  "confidence": 0.95
}
```

---

## Recreation: What It Is NOT

**It does not recreate the YouTube video.**

The system does NOT:
- Reproduce the tutorial's exact parameter settings
- Build a "YouTubePresetLoader"
- Map video frames to Serum parameters
- Memorize the artist's style as a fixed patch

The system DOES:
- Learn that "fast attack + fast decay → percussive"
- Learn that "high cutoff → bright"
- Learn the scope where these rules apply
- Apply these rules to new human requests

---

## Recreation: What It IS

**Recreation happens later, from human intent, using the learned knowledge.**

```
Later session:
  Human: "Make me a pluck bass."
    ↓
  Retrieve knowledge acquired from tutorials
  ("short attack + fast decay → pluck")
    ↓
  Plan operations (Env1.Attack, Env1.Decay)
    ↓
  Capability admission
  ("Is Env1.Attack qualified? Is Env1.Decay qualified?")
    ↓
  DawDreamer → Serum VST3
    ↓
  Render → Measure → Diagnose
    ↓
  ONE mutation → re-render → episode
```

The YouTube tutorial contributed the knowledge that short attack + fast decay → pluck. The recreation step is a **separate pipeline** that **uses** that knowledge. They share the knowledge layer. They do not share a pipeline.

---

## Memory: How It Works

Knowledge persists across sessions through **two mechanisms**:

### 1. Knowledge Graph (MCP Memory Server)

A local knowledge graph stores:
- **Entities:** Concepts, controls, relationships (Env1.Attack, "sustain", "filter")
- **Observations:** What was learned from which source (tutorial_xyz learned that decreasing Env1.Attack increases pitch precision)

Claude Code queries it via MCP tools. This is how the system "remembers" what it learned from a tutorial three weeks ago.

**Not required to be complex.** Several local MCP memory servers exist that provide exactly this: persistent, local, cross-session storage through a knowledge graph.

### 2. Episodes (Production Attempts)

Every mutation attempt — accepted or rejected — is recorded as an episode:
- Context (baseline state, goal, measurement)
- Action (mutation direction, magnitude)
- Measurement (baseline → treatment)
- Outcome (accepted/rejected)
- Polarity (positive/negative experience)

Episodes influence **future decisions** through retrieval. They are **not** authority. They never promote themselves to capabilities.

### What Memory Is NOT

- **Not authority.** Knowledge retrieval ≠ permission to execute.
- **Not automatic promotion.** Observations stay observations until corroborated and measured.
- **Not the same as learning.** Memory storage is Level 0. Learning requires retrieval to influence a decision.

---

## Two Separate Loops

```
KNOWLEDGE LOOP (from YouTube)
  Source → Proposition → Evidence → Claim → Capability
    ↑                                                    │
    └────────────── observations ────────────────────────┘

PRODUCTION LOOP (from human intent)
  Intent → Plan → Admission → Execution → Render → Measure
       → Diagnosis → Episode → Retrieval → Next decision
```

**YouTube feeds the knowledge loop.** Human intent feeds the **production loop.** They intersect at episodes: a production attempt can also be an observation that supports or undermines a claim.

---

## Teaching vs. Producing

The system will eventually do both, but they are **two products**, not one pipeline:

| Aspect | Producing | Teaching |
|--------|-----------|----------|
| **Input** | Human intent ("make a pluck bass") | Human question ("why does this feel like techno?") |
| **Output** | Audio + episode | Explanation + procedure + citations |
| **Authority** | Capability chain | None — teaching never authorizes execution |
| **Evidence** | Measurement | Provenance to sources |

YouTube is the **raw material for teaching**. It is the **source** for knowledge that later feeds **producing**. Do not collapse these into one system. They share the knowledge layer only.

---

## Minimal Implementation

### What Needs Building

1. **Transcript ingestion tool**
   - Either an existing MCP server (several exist for Claude Code)
   - Or a simple script using `yt-dlp`

2. **Knowledge extraction procedure** (Skill: `/extract-tutorial`)
   - Tells Claude Code how to read a transcript
   - Produces structured `KnowledgeItem` records
   - Binds tutorial language to semantic vocabulary
   - Records provenance and confidence

3. **Knowledge store**
   - Local knowledge graph MCP server
   - SQLite-backed, no cloud, no API key
   - Stores entities and observations

4. **Retrieval function**
   - Minimal mechanism to query the knowledge graph
   - Given: intent + scope
   - Returns: relevant KnowledgeItems

5. **Integration into production loop**
   - Already exists (DawDreamer loop, canonical feedback, episode persistence)
   - Step 5 adds: knowledge retrieval → planner input
   - Planner uses knowledge to influence candidate targets

### What Does Not Change

- **Step 0** is still the next action. Reconcile the repository before building.
- **No serum-mcp.** No Neo4j. No premature abstraction.
- **YouTube is input to knowledge**, not a pipeline of its own.
- **Genre and artist are scope dimensions**, not a taxonomy.
- **Authority is single-source:** evidence → claim → capability → admission.

---

## Entry Point for Step 5

When Step 5 executes:

1. **Input:** User provides YouTube link
2. **Process:** 
   - Fetch transcript
   - Extract structured knowledge
   - Write to local knowledge graph
3. **Output:** Confirmation that knowledge was stored
4. **Not tested at this step:** Whether the knowledge improves future production decisions (that's Step 7 after Ableton integration)

---

## One-Line Summary

**You give a YouTube link; Claude Code reads the transcript, extracts structured Serum knowledge, writes it to a persistent knowledge graph as observations, and later retrieves it when you ask for a sound — but the recreation is from human intent using learned knowledge, not a reproduction of the video, and knowledge never becomes execution authority without measurement evidence.**

---

**Last updated:** 2026-09-12  
**Status:** Design frozen for Step 5 implementation

