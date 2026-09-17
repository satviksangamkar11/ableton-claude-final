#!/usr/bin/env python3
"""V4 population pass: exact-match the 117 NOT_YET_DERIVED HOST_PARAMETER
semantic rows against the live VST3 parameter list. Same rigor as V3's
FX_PARAMETER pass: EXACT string match only (after normalization), no
fuzzy/guessed matches. Module-name substitutions (e.g. "Env {N}", "LFO
{N}", "A"/"B"/"C" for Osc1/2/3) are not invented here -- they are the
SAME conventions already proven live in this session's 144 currently-
bound HOST_PARAMETER rows (e.g. "Env 1 Attack", "LFO 1 Delay", "A Octave").
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw
from serum2.evidence import epoch as epoch_mod
from serum2.coverage.canonicalize import canonicalize_host_parameter, compute_capability_id

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
SEMANTIC_PATH = REPO_ROOT / "serum2" / "reconciliation" / "SERUM2_SEMANTIC_NORMALIZED.json"
OUT_PATH = REPO_ROOT / "serum2" / "reconciliation" / "HOST_PARAMETER_V4_MATCH.json"

# Module-number-to-real-name substitutions -- each already proven live by
# an EXISTING bound HOST_PARAMETER row in this registry (not invented here).
OSC_LETTER = {"OSC1": "A", "OSC2": "B", "OSC3": "C"}  # proven: "A Octave" etc. already live-verified
ENV_PREFIX = {f"ENV{n}": f"Env {n}" for n in range(1, 5)}       # proven: "Env 1 Attack" already live-verified
LFO_PREFIX = {f"LFO{n}": f"LFO {n}" for n in range(1, 7)}       # proven: "LFO 1 Delay" already live-verified
FILTER_PREFIX = {"FILTER1": "Filter 1", "FILTER2": "Filter 2"}  # proven: "Filter 1 Var" already live-verified


def get_live_params():
    VST3 = epoch_mod.SERUM_VST3
    engine = daw.RenderEngine(44100, 512)
    synth = engine.make_plugin_processor("serum", VST3)
    return synth.get_parameters_description()


def clean_label(label: str) -> str:
    """Strip parenthetical/dash annotations to the core UI name, e.g.
    'A>BUS1 -- send amount to Bus 1' -> 'A>BUS1', 'Sub Osc Enable -- ...' -> 'Sub Osc Enable'."""
    core = re.split(r"\s*--\s*|\s*\(", label)[0].strip()
    return core


# Direct evidence-backed exceptions where the cleaned-label heuristic
# above would miss or mismatch the real name (checked individually
# against the live parameter list, not guessed):
#   FILTER{1,2}.CUTOFF -> a3_modulation_route.py's own documented mapping
#     (VoiceFilter kParamFreq) + confirmed live name "Filter {N} Freq".
#   VOICE.VOICING.MONO -> only one live param containing "Mono" exists
#     ("Mono Toggle"); confirmed unambiguous.
#   GLOBAL.TUNING.GLOBAL_TUNING is explicitly NOT overridden: the only
#     live candidate ("Main Tuning", default=0.5, normalized 0..1) does
#     not match the semantic definition ("reference frequency in Hz") --
#     different concepts, left unmatched rather than guessed.
DIRECT_OVERRIDES = {
    "FILTER1.CUTOFF": "Filter 1 Freq",
    "FILTER2.CUTOFF": "Filter 2 Freq",
    "FILTER1.RESONANCE": "Filter 1 Res",
    "FILTER2.RESONANCE": "Filter 2 Res",
    "VOICE.VOICING.MONO": "Mono Toggle",
    # Real live names drop "OSC"/use abbreviations the cleaned-label
    # heuristic can't predict -- each confirmed individually against the
    # live parameter list this run, not guessed:
    "NOISE_OSC.LEVEL": "Noise Level",
    "NOISE_OSC.PAN": "Noise Pan",
    "NOISE_OSC.FINE": "Noise Fine",
    "SUB_OSC.LEVEL": "Sub Level",
    "SUB_OSC.PAN": "Sub Pan",
    "SUB_OSC.OCTAVE": "Sub Octave",
    "MIXER.SUB.ENABLE": "Sub Enable",
    "MIXER.FILTER1.ENABLE": "Filter 1 On",
    "MIXER.FILTER2.ENABLE": "Filter 2 On",
    "MIXER.BUS1.LEVEL": "Bus 1 Vol",
    "MIXER.BUS2.LEVEL": "Bus 2 Vol",
}


def candidate_names(semantic_id: str, label: str) -> list:
    if semantic_id in DIRECT_OVERRIDES:
        return [DIRECT_OVERRIDES[semantic_id]]
    """Generate candidate real-parameter-name strings from the semantic_id's
    module prefix + the cleaned label -- exact strings to check, not patterns."""
    core = clean_label(label)
    module = semantic_id.split(".")[0]
    candidates = [core]

    if module in OSC_LETTER:
        letter = OSC_LETTER[module]
        # "Octave" -> "A Octave"; already-bare-letter labels left as-is
        candidates.append(f"{letter} {core}")
    if module in ENV_PREFIX:
        prefix = ENV_PREFIX[module]
        candidates.append(f"{prefix} {core}")
    if module.startswith("LFO") and module in LFO_PREFIX:
        prefix = LFO_PREFIX[module]
        candidates.append(f"{prefix} {core}")
    if module in FILTER_PREFIX:
        prefix = FILTER_PREFIX[module]
        candidates.append(f"{prefix} {core}")
        # some Filter labels already start with "Filter 1 ..." themselves
    # MIXER.<CHANNEL>.<FIELD>: core is already the full expected UI string
    # (e.g. "A>BUS1", "Sub Osc Enable", "Filter 1 Level") -- try as-is only.

    # de-dup while preserving order
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def main():
    registry = json.load(open(REGISTRY_PATH, "r", encoding="utf-8"))
    semantic_defs = {r["semantic_id"]: r for r in json.load(open(SEMANTIC_PATH, "r", encoding="utf-8"))["records"]}
    live_params = get_live_params()
    live_by_name = {p["name"]: p for p in live_params}

    rows = [r for r in registry["semantic_resolutions"]
            if r.get("capability_binding") and r["capability_binding"]["execution_family"] == "HOST_PARAMETER"
            and r["capability_binding"]["binding_status"] == "NOT_YET_DERIVED"]

    matched = []
    unmatched = []
    for row in rows:
        sid = row["semantic_id"]
        sem = semantic_defs.get(sid)
        if sem is None:
            unmatched.append({"semantic_id": sid, "reason": "no frozen semantic definition"})
            continue
        label = sem["canonical_label"]
        candidates = candidate_names(sid, label)
        hit = next((c for c in candidates if c in live_by_name), None)
        if hit is None:
            unmatched.append({"semantic_id": sid, "label": label, "candidates_tried": candidates})
            continue
        matched.append({"semantic_id": sid, "label": label, "matched_param_name": hit})

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"matched_count": len(matched), "unmatched_count": len(unmatched),
                    "matched": matched, "unmatched": unmatched}, f, indent=2)

    print(f"HOST_PARAMETER V4 match: {len(rows)} candidate rows")
    print(f"  MATCHED:   {len(matched)}")
    print(f"  UNMATCHED: {len(unmatched)}")
    print(f"\nWrote: {OUT_PATH}")
    return matched, unmatched


if __name__ == "__main__":
    main()
