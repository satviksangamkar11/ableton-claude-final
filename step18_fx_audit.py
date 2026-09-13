"""Step 18: Structural audit of all 14 FX effect families.

No manual UI testing. Uses existing evidence from:
- fx_resolver_complete.py (authoritative parameter catalog)
- Step 16 validated mechanism (Distortion, Delay)
- Generic bypass implementation (Step 17)

Audit scope:
1. All 14 effect types exist in catalog
2. Parameter sets are represented
3. All use generic plainParams structure
4. No FX-family exceptions to bypass mechanism
5. Structural operations address all effects generically
"""

from serum2.operations.fx_resolver_complete import EffectType, FX_PARAMETER_CATALOG


def audit_fx_families():
    """Audit all 14 FX effect families structurally."""
    print("="*80)
    print("STEP 18: FX COMPLETENESS AUDIT")
    print("="*80)

    # List of all 14 effect types
    all_effects = [e for e in EffectType]

    print(f"\nAudit: {len(all_effects)} FX effect families\n")

    audit_results = {
        "total": len(all_effects),
        "with_parameters": 0,
        "details": [],
        "missing_from_catalog": [],
        "exceptions": [],
    }

    for effect in all_effects:
        effect_name = effect.name  # e.g., "DISTORTION"
        effect_class = effect.value  # e.g., "FXDistortion"

        print(f"[{effect_name}] {effect_class}")

        # Check if effect exists in catalog
        if effect_name not in FX_PARAMETER_CATALOG:
            print(f"  ✗ NOT in parameter catalog")
            audit_results["missing_from_catalog"].append(effect_name)
            continue

        params = FX_PARAMETER_CATALOG[effect_name]
        param_count = len(params)

        print(f"  ✓ In catalog with {param_count} parameters")

        # Verify path structure for each parameter
        path_issues = []
        for param_name, (path_template, ptype, min_val, max_val) in params.items():
            # Check that path contains the effect class name
            if effect_class not in path_template:
                path_issues.append(f"{param_name}: missing {effect_class} in path")

            # Check that path contains plainParams
            if "plainParams" not in path_template:
                path_issues.append(f"{param_name}: missing plainParams in path")

        if path_issues:
            for issue in path_issues:
                print(f"    ⚠ {issue}")
            audit_results["exceptions"].append({
                "effect": effect_name,
                "issue": "path_structure",
                "details": path_issues,
            })
        else:
            print(f"  ✓ All parameter paths use plainParams")

        # Check for bypass mechanism consistency
        # (all FX should have plainParams as a dict that can contain kParamEnable)
        if not any("plainParams" in path for _, (path, _, _, _) in params.items()):
            audit_results["exceptions"].append({
                "effect": effect_name,
                "issue": "no_plainParams",
            })
            print(f"  ✗ No plainParams found")
        else:
            audit_results["with_parameters"] += 1
            print(f"  ✓ Uses generic plainParams structure")

        # Verify no exceptions to generic model
        if effect_name in ["DISTORTION", "DELAY"]:
            print(f"  ✓ VALIDATED in Step 16/17 (bypass mechanism confirmed)")

        print()

    # Summary
    print("="*80)
    print("AUDIT RESULTS")
    print("="*80)

    print(f"\nTotal FX effects: {audit_results['total']}")
    print(f"With parameters in catalog: {audit_results['with_parameters']}")
    print(f"Missing from catalog: {len(audit_results['missing_from_catalog'])}")

    if audit_results["missing_from_catalog"]:
        print(f"\nMissing effects:")
        for fx in audit_results["missing_from_catalog"]:
            print(f"  - {fx}")

    print(f"\nPath structure exceptions: {len(audit_results['exceptions'])}")
    if audit_results["exceptions"]:
        for exc in audit_results["exceptions"]:
            print(f"  - {exc['effect']}: {exc['issue']}")

    # Validated families
    validated = ["DISTORTION", "DELAY"]
    unvalidated = [e.name for e in all_effects if e.name not in validated]

    print(f"\nVALIDATED families (runtime Step 16/17):")
    for fx in validated:
        print(f"  ✓ {fx}")

    print(f"\nUNVALIDATED families (structural audit only):")
    for fx in sorted(unvalidated):
        if fx not in audit_results["missing_from_catalog"]:
            print(f"  - {fx}")

    # Conclusion
    print(f"\n{'='*80}")
    if not audit_results["missing_from_catalog"] and not audit_results["exceptions"]:
        print("✓ AUDIT PASSED: All 14 FX families have consistent structure")
        print("✓ No exceptions to generic bypass mechanism")
        print("✓ All use plainParams for parameter storage")
        return True
    else:
        print("⚠ AUDIT FOUND ISSUES (see above)")
        return False


if __name__ == "__main__":
    success = audit_fx_families()
    exit(0 if success else 1)
