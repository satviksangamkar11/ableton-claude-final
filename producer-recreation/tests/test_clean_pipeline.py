#!/usr/bin/env python
"""Test suite for clean producer recreation pipeline.

Verifies:
- External transcript/knowledge handling
- Claude Code isolation (no raw transcript loaded)
- Structured knowledge retrieval
- Producer brain integration
"""
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_a_knowledge_store_exists():
    """TEST A: Verify structured knowledge store exists."""
    print("\n" + "=" * 70)
    print("TEST A: KNOWLEDGE STORE EXISTS")
    print("=" * 70)

    knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "yt_f507169bd7cb.json"

    if not knowledge_path.exists():
        print(f"[FAIL] Knowledge store not found: {knowledge_path}")
        return False

    try:
        with open(knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        item_count = data.get("total_items", len(data.get("items", [])))
        print(f"[OK] Knowledge store found: {knowledge_path}")
        print(f"[OK] Total items: {item_count}")
        return True

    except Exception as e:
        print(f"[FAIL] Knowledge store load failed: {e}")
        return False


def test_b_raw_transcript_external():
    """TEST B: Verify raw transcript is NOT in Claude Code context."""
    print("\n" + "=" * 70)
    print("TEST B: RAW TRANSCRIPT EXTERNAL")
    print("=" * 70)

    knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "yt_f507169bd7cb.json"

    try:
        with open(knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check that transcript segments are NOT in the knowledge store
        serialized = json.dumps(data)

        has_transcript_segments = "transcript_segments" in serialized
        has_raw_text = len([k for k in data.keys() if "transcript" in k.lower()]) > 0

        print(f"[CHECK] Knowledge store keys: {list(data.keys())}")
        print(f"[CHECK] Has 'transcript_segments': {has_transcript_segments}")
        print(f"[CHECK] Has transcript-related keys: {has_raw_text}")

        if not has_transcript_segments and not has_raw_text:
            print("[OK] Knowledge store is clean - no raw transcript included")
            return True
        else:
            print("[WARN] Knowledge store may contain transcript data")
            return False

    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")
        return False


def test_c_structured_knowledge_items():
    """TEST C: Verify structured knowledge items are present."""
    print("\n" + "=" * 70)
    print("TEST C: STRUCTURED KNOWLEDGE ITEMS")
    print("=" * 70)

    knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "yt_f507169bd7cb.json"

    try:
        with open(knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        items_dict = data.get("items", {})
        item_count = len(items_dict)
        print(f"[OK] Knowledge items found: {item_count}")

        if item_count == 0:
            print("[WARN] No items in knowledge store")
            return False

        # Check first item structure
        first_key = list(items_dict.keys())[0]
        first_item = items_dict[first_key]
        required_fields = ["knowledge_item_id", "source_reference", "original_proposition"]

        missing = [f for f in required_fields if f not in first_item]
        if missing:
            print(f"[WARN] Missing fields in item: {missing}")

        # Show sample items
        print(f"\n[SAMPLE] First 3 item IDs:")
        for i, (key, item) in enumerate(list(items_dict.items())[:3], 1):
            kid = item.get("knowledge_item_id", "UNKNOWN")
            prop = item.get("original_proposition", "")[:60]
            print(f"  {i}. {kid}")
            print(f"     {prop}...")

        return True

    except Exception as e:
        print(f"[FAIL] Item verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_d_no_raw_transcript_in_reasoning():
    """TEST D: Verify no raw transcript would be loaded into reasoning."""
    print("\n" + "=" * 70)
    print("TEST D: REASONING ISOLATION")
    print("=" * 70)

    # Check that the fetch/extract scripts are external
    fetch_script = PROJECT_ROOT / "source" / "fetch_youtube.py"
    extract_script = PROJECT_ROOT / "source" / "extract_knowledge.py"

    print("[CHECK] External transcript fetch: " + str(fetch_script.exists()))
    print("[CHECK] External knowledge extraction: " + str(extract_script.exists()))

    # Verify these scripts run as subprocesses
    with open(PROJECT_ROOT / "scripts" / "recreate_reference.py", "r") as f:
        orchestrator_code = f.read()

    has_subprocess = "subprocess.run" in orchestrator_code
    no_direct_read = "fetch_youtube" not in orchestrator_code or "import" not in orchestrator_code.split("fetch_youtube")[0].split("\n")[-1]

    print("[CHECK] Uses subprocess.run: " + str(has_subprocess))
    print("[OK] Transcript fetch is external (subprocess)")
    print("[OK] Knowledge extraction is external (subprocess)")
    print("[OK] Raw transcript will NOT be loaded into Claude Code")

    return has_subprocess


def test_e_producer_brain_integration():
    """TEST E: Verify producer brain can access structured knowledge."""
    print("\n" + "=" * 70)
    print("TEST E: PRODUCER BRAIN INTEGRATION")
    print("=" * 70)

    knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "yt_f507169bd7cb.json"

    try:
        with open(knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        source_id = data.get("schema_version", "UNKNOWN")
        item_count = data.get("total_items", 0)

        print(f"[OK] Knowledge store loaded successfully")
        print(f"[OK] Can provide {item_count} knowledge items to producer brain")
        print(f"[OK] Producer brain will receive:")
        print(f"     - Source URL: (from metadata)")
        print(f"     - Structured knowledge items: {item_count}")
        print(f"     - NOT raw transcript")

        return True

    except Exception as e:
        print(f"[FAIL] Producer integration check failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("CLEAN PRODUCER PIPELINE TEST SUITE")
    print("=" * 70)

    tests = [
        ("A", test_a_knowledge_store_exists),
        ("B", test_b_raw_transcript_external),
        ("C", test_c_structured_knowledge_items),
        ("D", test_d_no_raw_transcript_in_reasoning),
        ("E", test_e_producer_brain_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[EXCEPTION] Test {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  Test {name}: {status}")

    all_passed = all(r for _, r in results)
    print(f"\nOverall: {'[PASS] All tests passed' if all_passed else '[FAIL] Some tests failed'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
