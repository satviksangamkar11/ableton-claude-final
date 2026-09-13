"""Phase 2: Auto-generated scalar operation definitions and compilers.

This module creates SCALAR operation definitions from existing SEMANTIC_TARGETS
and registers compilers for them.

A SCALAR operation is a direct parameter value change that compiles to a
single Mutation using the target_path from the semantic target's contract.

This layer bridges the gap between:
  - human semantic targets (e.g., "LFO0.Rate")
  - existing admission/capability contracts
  - pathmerge mutations
"""

from __future__ import annotations
from typing import Optional, Dict, Any

from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
    OperationResult,
)
from .registry import OperationRegistry, OperationDefinition
from serum2.evidence.spec import Mutation

# Phase 9B/FX-FULL: Direct path mappings for new structural controls (corpus-verified, no contracts yet)
PHASE_9B_STRUCTURAL_PATHS = {
    # Phase 9B original
    "oscillator_field_OSC2-ENABLE": "Oscillator1.plainParams.kParamEnable",
    "oscillator_field_OSC3-ENABLE": "Oscillator2.plainParams.kParamEnable",
    "filter_field_ENABLE": "VoiceFilter0.plainParams.kParamEnable",
    "filter2_field_ENABLE": "VoiceFilter1.plainParams.kParamEnable",
    "oscillator_field_NOISE-FINE": "Oscillator3.plainParams.kParamFine",
    "global_field_pitch_tracking": "Oscillator0.plainParams.kParamPitchTrack",
    "arp_field_ENABLE": "Arp0.plainParams.kParamEnabled",

    # STEP 20A-20B: OSC MIX controls (persistent via plainParams) — parametric pattern
    "osc1_plain_param_pan": "Oscillator0.plainParams.kParamPan",
    "osc1_plain_param_level": "Oscillator0.plainParams.kParamVolume",
    "osc2_plain_param_pan": "Oscillator1.plainParams.kParamPan",
    "osc2_plain_param_level": "Oscillator1.plainParams.kParamVolume",
    "osc3_plain_param_pan": "Oscillator2.plainParams.kParamPan",
    "osc3_plain_param_level": "Oscillator2.plainParams.kParamVolume",
    "sub_plain_param_pan": "Oscillator3.plainParams.kParamPan",
    "sub_plain_param_level": "Oscillator3.plainParams.kParamVolume",
    "noise_plain_param_pan": "Oscillator4.plainParams.kParamPan",
    "noise_plain_param_level": "Oscillator4.plainParams.kParamVolume",

    # STEP 20B PART 3: MIX send levels (per-source send to FX Bus 1/2)
    # RoutingSlot index maps positionally to source channel (proven via real UI +
    # DawDreamer VST3 host-param correlation: RoutingSlot0=OSC A ... RoutingSlot6=Filter 2).
    # Scale: CBOR 0..100 (linear) == VST3 host param 0..1 (e.g. 100.0 -> "A>BUS1"=1.0).
    "routing_slot0_bus1_level": "RoutingSlot0.plainParams.kParamFXBus1Level",
    "routing_slot0_bus2_level": "RoutingSlot0.plainParams.kParamFXBus2Level",
    "routing_slot1_bus1_level": "RoutingSlot1.plainParams.kParamFXBus1Level",
    "routing_slot1_bus2_level": "RoutingSlot1.plainParams.kParamFXBus2Level",
    "routing_slot2_bus1_level": "RoutingSlot2.plainParams.kParamFXBus1Level",
    "routing_slot2_bus2_level": "RoutingSlot2.plainParams.kParamFXBus2Level",
    "routing_slot3_bus1_level": "RoutingSlot3.plainParams.kParamFXBus1Level",
    "routing_slot3_bus2_level": "RoutingSlot3.plainParams.kParamFXBus2Level",
    "routing_slot4_bus1_level": "RoutingSlot4.plainParams.kParamFXBus1Level",
    "routing_slot4_bus2_level": "RoutingSlot4.plainParams.kParamFXBus2Level",
    "routing_slot5_bus1_level": "RoutingSlot5.plainParams.kParamFXBus1Level",
    "routing_slot5_bus2_level": "RoutingSlot5.plainParams.kParamFXBus2Level",
    "routing_slot6_bus1_level": "RoutingSlot6.plainParams.kParamFXBus1Level",
    "routing_slot6_bus2_level": "RoutingSlot6.plainParams.kParamFXBus2Level",

    # STEP 20B PART 3: FX Bus channel's own overall volume (distinct from per-source sends above)
    # Scale: kParamFXBus{N}Vol = 0.5 * 10^(dB/20); default 0.5 == 0dB unity.
    "global_plain_param_fx_bus1_vol": "Global0.plainParams.kParamFXBus1Vol",
    "global_plain_param_fx_bus2_vol": "Global0.plainParams.kParamFXBus2Vol",

    # Phase FX-FULL: Complete FX parameter paths (corpus-verified)
    # BODE parameters
    "fx_field_bode_shift": "FXRack{R}.FX.{N}.FXBode.plainParams.kParamShift",
    "fx_field_bode_range": "FXRack{R}.FX.{N}.FXBode.plainParams.kParamRange",
    "fx_field_bode_direction": "FXRack{R}.FX.{N}.FXBode.plainParams.kParamDirection",
    "fx_field_bode_level_out": "FXRack{R}.FX.{N}.FXBode.plainParams.kParamLevelOut",
    "fx_field_bode_mix_or_gain": "FXRack{R}.FX.{N}.FXBode.plainParams.kParamMixOrGain",

    # CHORUS parameters
    "fx_field_chorus_rate": "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamRate",
    "fx_field_chorus_depth": "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamDepth",
    "fx_field_chorus_feedback": "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamFeedback",
    "fx_field_chorus_phase": "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamPhase",
    "fx_field_chorus_mix_or_gain": "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamMixOrGain",

    # COMPRESSOR parameters
    "fx_field_comp_threshold": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamThreshold",
    "fx_field_comp_ratio": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamRatio",
    "fx_field_comp_attack": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamAttack",
    "fx_field_comp_release": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamRelease",
    "fx_field_comp_gain": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamGain",
    "fx_field_comp_mix_or_gain": "FXRack{R}.FX.{N}.FXComp.plainParams.kParamMixOrGain",

    # CONVOLVE parameters
    "fx_field_convolve_ir_gain": "FXRack{R}.FX.{N}.FXConv.plainParams.kParamIRGain",
    "fx_field_convolve_attack": "FXRack{R}.FX.{N}.FXConv.plainParams.kParamAttack",
    "fx_field_convolve_decay": "FXRack{R}.FX.{N}.FXConv.plainParams.kParamDecay",
    "fx_field_convolve_damping": "FXRack{R}.FX.{N}.FXConv.plainParams.kParamDamping",
    "fx_field_convolve_mix_or_gain": "FXRack{R}.FX.{N}.FXConv.plainParams.kParamMixOrGain",
    "fx_field_convolve_ir_path": "FXRack{R}.FX.{N}.FXConv.relativePathToIR",

    # DELAY parameters
    "fx_field_delay_mode": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamMode",
    "fx_field_delay_time_l": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamTimeL",
    "fx_field_delay_time_r": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamTimeR",
    "fx_field_delay_offset_l": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamOffsetL",
    "fx_field_delay_offset_r": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamOffsetR",
    "fx_field_delay_feedback": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamFeedback",
    "fx_field_delay_mix_or_gain": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamMixOrGain",
    "fx_field_delay_bw": "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamBW",

    # DISTORTION parameters
    "fx_field_dist_mode": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamMode",
    "fx_field_dist_drive": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamDrive",
    "fx_field_dist_freq": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamFreq",
    "fx_field_dist_lphp": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamLPHP",
    "fx_field_dist_prepost": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamPrePost",
    "fx_field_dist_mix_or_gain": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamMixOrGain",
    "fx_field_dist_bw": "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamBW",

    # EQUALIZER parameters
    "fx_field_eq_type1": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamType1",
    "fx_field_eq_freq1": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamFreq1",
    "fx_field_eq_reso1": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamReso1",
    "fx_field_eq_gain1": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamGain1",
    "fx_field_eq_type2": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamType2",
    "fx_field_eq_freq2": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamFreq2",
    "fx_field_eq_reso2": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamReso2",
    "fx_field_eq_gain2": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamGain2",
    "fx_field_eq_level_out": "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamLevelOut",

    # FILTER (as FX) parameters
    "fx_field_filter_type": "FXRack{R}.FX.{N}.FXFilter.plainParams.kParamType",
    "fx_field_filter_cutoff": "FXRack{R}.FX.{N}.FXFilter.plainParams.kParamCutoff",
    "fx_field_filter_resonance": "FXRack{R}.FX.{N}.FXFilter.plainParams.kParamResonance",
    "fx_field_filter_drive": "FXRack{R}.FX.{N}.FXFilter.plainParams.kParamDrive",
    "fx_field_filter_mix_or_gain": "FXRack{R}.FX.{N}.FXFilter.plainParams.kParamMixOrGain",

    # FLANGER parameters
    "fx_field_flanger_rate": "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamRate",
    "fx_field_flanger_depth": "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamDepth",
    "fx_field_flanger_feedback": "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamFeedback",
    "fx_field_flanger_phase": "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamPhase",
    "fx_field_flanger_mix_or_gain": "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamMixOrGain",

    # HYPER/DIMENSION parameters
    "fx_field_hyper_rate": "FXRack{R}.FX.{N}.FXHyperD.plainParams.kParamRate",
    "fx_field_hyper_unison": "FXRack{R}.FX.{N}.FXHyperD.plainParams.kParamUnison",
    "fx_field_hyper_detune": "FXRack{R}.FX.{N}.FXHyperD.plainParams.kParamDetune",
    "fx_field_hyper_mix_or_gain": "FXRack{R}.FX.{N}.FXHyperD.plainParams.kParamMixOrGain",
    "fx_field_hyper_retrigger": "FXRack{R}.FX.{N}.FXHyperD.plainParams.kParamRetrigger",

    # PHASER parameters
    "fx_field_phaser_frequency": "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamFrequency",
    "fx_field_phaser_feedback": "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamFeedback",
    "fx_field_phaser_phase": "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamPhase",
    "fx_field_phaser_mix_or_gain": "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamMixOrGain",

    # REVERB parameters
    "fx_field_reverb_size": "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamSize",
    "fx_field_reverb_damping": "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamDamping",
    "fx_field_reverb_mix_or_gain": "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamMixOrGain",

    # SPLITTER parameters
    "fx_field_splitter_band_count": "FXRack{R}.FX.{N}.FXSplit.plainParams.kParamBandCount",
    "fx_field_splitter_crossover1": "FXRack{R}.FX.{N}.FXSplit.plainParams.kParamCrossover1",
    "fx_field_splitter_crossover2": "FXRack{R}.FX.{N}.FXSplit.plainParams.kParamCrossover2",
    "fx_field_splitter_crossover3": "FXRack{R}.FX.{N}.FXSplit.plainParams.kParamCrossover3",

    # UTILITY parameters
    "fx_field_utility_gain": "FXRack{R}.FX.{N}.FXUtils.plainParams.kParamGain",
    "fx_field_utility_phase": "FXRack{R}.FX.{N}.FXUtils.plainParams.kParamPhase",
    "fx_field_utility_mono": "FXRack{R}.FX.{N}.FXUtils.plainParams.kParamMono",
    "fx_field_utility_mix_or_gain": "FXRack{R}.FX.{N}.FXUtils.plainParams.kParamMixOrGain",
}


def build_scalar_operations_from_targets(
    registry: OperationRegistry,
) -> None:
    """Auto-generate SCALAR operations from SEMANTIC_TARGETS.

    For each semantic target in serum2/compiler/targets.SEMANTIC_TARGETS:
    1. Create an OperationDefinition
    2. Register a compiler function
    3. Add to the registry

    This populates the registry with ~100+ scalar operations covering:
    - Envelope parameters (Attack, Decay, Sustain, Release for Env1-N)
    - LFO parameters (Rate, Shape, Mode for LFO0-9)
    - Macro parameters (Value, Name for Macro0-7)
    - Filter parameters (Cutoff, Resonance, Drive, Type)
    - FX parameters (all EQ, Distortion, Delay, Reverb, Compressor params)
    - Oscillator parameters (Volume, Octave, Detune, etc.)
    - Global parameters (Master Volume, etc.)
    - Phase 9B: Module activation (OSC2/3 Enable, Filter Enable, etc.)
    """
    from serum2.compiler.targets import SEMANTIC_TARGETS
    from serum2.evidence.capability_contract import CAUSAL_VERIFIED
    from serum2.evidence import admission as admission_mod

    # For each semantic target in the vocabulary, create a SCALAR operation
    # Deduplicate by capability_key (some targets alias to the same capability)
    seen_keys = set()
    for target_name, target_ref in SEMANTIC_TARGETS.items():
        # Skip if we've already registered this capability_key
        if target_ref.capability_key in seen_keys:
            continue
        seen_keys.add(target_ref.capability_key)

        # Operation identity
        operation_id = f"scalar_{target_ref.capability_key}"
        semantic_name = f"Set {target_name}"

        # Create the operation definition
        definition = OperationDefinition(
            operation_id=operation_id,
            semantic_name=semantic_name,
            kind=OperationKind.SCALAR,
            parameters=[
                OperationParameter(
                    name="value",
                    value=None,  # will be set at runtime by SerumOperation instance
                    required=True,
                    description=f"Value for {target_name}",
                )
            ],
            measurement_metric=None,  # determined by contract
            expected_direction=None,  # determined by contract
            description=f"Direct scalar mutation: {target_name}",
        )

        registry.register(definition)

        # Register the compiler function
        def make_scalar_compiler(tgt_name: str, tgt_ref: Any) -> callable:
            """Closure to capture target for compiler."""
            def scalar_compiler(operation: SerumOperation, ctx: OperationContext) -> OperationResult:
                """Compile a SCALAR operation to a single Mutation."""
                if not operation.parameters:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        compilation_error="MISSING_VALUE",
                        error_detail="SCALAR operation requires value parameter",
                    )

                value = operation.parameters[0].value

                # Look up the semantic target to get the mutation path
                # The path comes from the CapabilityContract associated with this target
                from serum2.compiler.targets import resolve_semantic_target
                from serum2.producer.contract_registry import ContractRegistry

                try:
                    # Get contracts from registry
                    contract_registry = ContractRegistry()
                    contracts_dict = contract_registry.get_contracts_dict()

                    # Resolve the semantic target to get the contract
                    resolution = resolve_semantic_target(tgt_name, contracts_dict)
                    if hasattr(resolution, 'contract') and resolution.contract:
                        # Contract exists; use its scope.mutation_target_path
                        contract = resolution.contract
                        mutation_path = contract.scope.get("mutation_target_path")
                        if not mutation_path:
                            return OperationResult(
                                operation_id=operation.operation_id,
                                success=False,
                                compilation_error="NO_MUTATION_PATH",
                                error_detail=f"Contract for {tgt_name} has no mutation_target_path",
                            )
                    else:
                        # No contract; check Phase 9B structural paths mapping
                        mutation_path = PHASE_9B_STRUCTURAL_PATHS.get(tgt_ref.capability_key)
                        if not mutation_path:
                            # Fallback: use the semantic target name (will fail if path is invalid)
                            mutation_path = tgt_name

                    # Create the mutation
                    mutation = Mutation(
                        target_path=mutation_path,
                        value=value,
                        provenance=f"SerumOperation.{operation.operation_id}",
                    )

                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        compiled_mutations=[mutation],
                        mutation_description=f"Scalar: {mutation_path} = {value}",
                    )

                except Exception as e:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        compilation_error="COMPILATION_ERROR",
                        error_detail=str(e),
                    )

            return scalar_compiler

        registry.register_compiler(operation_id, make_scalar_compiler(target_name, target_ref))


def register_scalar_operations() -> None:
    """Initialize scalar operation registry at module load time."""
    from .registry import get_registry
    registry = get_registry()
    build_scalar_operations_from_targets(registry)
