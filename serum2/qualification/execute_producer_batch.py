"""
Execute producer episodes for targets that have actual YouTube hypothesis support.

YouTube hypotheses coverage:
  - OSC1.Octave: 16 hypotheses
  - Env1.Attack: 3 hypotheses
  - Env1.Release: 7 hypotheses (already executed in ep_vertical_slice_001)
  - Others: not represented

This execution does NOT create hypotheses for OSC1.Level, OSC1.Detune, Filter.Cutoff
because that would violate the constraint: no new knowledge, no synthetic support.

Therefore: execute only the 2 remaining targets with real YouTube support.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.qualification.execute_vertical_slice import execute_producer_episode

def execute_producer_batch():
    """Execute producer episodes for targets with YouTube hypothesis support."""
    episodes = []
    results = []

    print("\n" + "=" * 80)
    print("PRODUCER EPISODE BATCH: TARGETS WITH YOUTUBE HYPOTHESIS SUPPORT")
    print("=" * 80)

    # Target 1: Env1.Attack (3 hypotheses in YouTube)
    print("\n[1/2] Executing Env1.Attack...")
    ep, err = execute_producer_episode(
        human_intent="make the attack slower",
        semantic_target="Env1.Attack",
        host_param_name="Env 1 Attack",
        mutation_value=0.6,
        measurement_metric="rms_db",
        episode_id="ep_producer_env1_attack_001",
    )
    if ep:
        episodes.append(ep)
        results.append((True, "Env1.Attack", None))
        print("[OK] Env1.Attack episode created")
    else:
        results.append((False, "Env1.Attack", err))
        print(f"[FAILED] Env1.Attack: {err}")

    # Target 2: OSC1.Octave (16 hypotheses in YouTube)
    print("\n[2/2] Executing OSC1.Octave...")
    ep, err = execute_producer_episode(
        human_intent="make the oscillator one octave higher",
        semantic_target="OSC1.Octave",
        host_param_name="A Octave",
        mutation_value=0.625,
        measurement_metric="pitch_shift_semitones",
        episode_id="ep_producer_osc1_octave_001",
    )
    if ep:
        episodes.append(ep)
        results.append((True, "OSC1.Octave", None))
        print("[OK] OSC1.Octave episode created")
    else:
        results.append((False, "OSC1.Octave", err))
        print(f"[FAILED] OSC1.Octave: {err}")

    # Summary
    print("\n" + "=" * 80)
    print("BATCH SUMMARY")
    print("=" * 80)
    for success, target, error in results:
        status = "[OK]" if success else f"[FAILED] {error}"
        print(f"  {target:20} {status}")

    success_count = sum(1 for s, _, _ in results if s)
    print(f"\nTotal: {success_count}/2 episodes completed")

    print("\n" + "=" * 80)
    print("NOTE: OSC1.Level, OSC1.Detune, Filter.Cutoff not executed")
    print("Reason: No YouTube hypotheses support these targets")
    print("Creating synthetic knowledge would violate constraints")
    print("=" * 80)

    return episodes, results


if __name__ == "__main__":
    episodes, results = execute_producer_batch()
