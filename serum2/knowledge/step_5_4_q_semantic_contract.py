"""
STEP 5.4-Q — SEMANTIC CLASSIFICATION CONTRACT

Universal music knowledge semantic function definitions.

This contract defines what each knowledge type MEANS, independent of keyword patterns.

Used for:
    1. Classifier decision logic
    2. Regression tests
    3. Adversarial examples
    4. Universal classification framework
"""

# ========================================================================
# SEMANTIC CLASSIFICATION CONTRACT
# ========================================================================

SEMANTIC_CONTRACT = {
    "CONCEPT": {
        "definition": "A definition or explanation of what something is or means.",
        "semantic_function": "Defines or explains a term, construct, or phenomenon.",
        "examples": [
            "Decay is the amount of time it takes the amplitude to reach sustain.",
            "An LFO is a low-frequency oscillator that modulates other parameters.",
            "A filter is a frequency-selective processor.",
        ],
        "counter_examples": [
            "You can adjust decay by dragging the slider.",  # PROCEDURE, not CONCEPT
            "Decay creates smoother note endings.",  # PRINCIPLE, not CONCEPT
            "I recommend shorter decay for plucks.",  # RECOMMENDATION
        ],
    },

    "PROCEDURE": {
        "definition": "An actionable sequence or instruction intended to achieve an outcome.",
        "semantic_function": "Provides step-by-step, actionable instructions.",
        "marks": [
            "imperative mood",
            "sequential steps",
            "explicit actions to perform",
            "conditions for action",
        ],
        "examples": [
            "Click the oscillator, then select a saw wave.",
            "To create a bass: set the release shorter.",
            "First, open the filter menu. Then drag the cutoff down.",
            "Set the release shorter to make plucks tighter.",
        ],
        "counter_examples": [
            "You can adjust decay.",  # OBSERVATION (capability statement)
            "Shorter decay makes tighter articulation.",  # PRINCIPLE (causal)
            "I recommend short decay.",  # RECOMMENDATION
            "Decay is the sustain transition time.",  # CONCEPT
        ],
    },

    "PRINCIPLE": {
        "definition": "A generalized relationship, mechanism, or organizing rule.",
        "semantic_function": "Explains how/why something works, relationships, causality, or patterns.",
        "marks": [
            "cause-and-effect",
            "generalized behavior",
            "relationships between elements",
            "how things work",
            "system organization",
        ],
        "examples": [
            "Shorter release makes tighter articulation.",
            "The signal passes through generators, then filters, then effects.",
            "Envelopes behave the same way when modulating any parameter.",
            "Filters remove frequencies to shape tone.",
            "LFOs repeat cyclically; envelopes play once per note.",
        ],
        "counter_examples": [
            "Release is the decay-to-silence time.",  # CONCEPT
            "Shorten the release.",  # PROCEDURE
            "Short releases are good for plucks.",  # RECOMMENDATION
            "I notice short releases sound tighter.",  # OBSERVATION
        ],
    },

    "OBSERVATION": {
        "definition": "A statement describing an observed/existing property, feature, or state.",
        "semantic_function": "Describes what exists, what is possible, what was observed.",
        "marks": [
            "descriptive statements",
            "cataloging capabilities",
            "reporting what exists",
            "feature inventory",
            "factual description",
        ],
        "examples": [
            "Serum contains three generators.",
            "The UI has a preset browser on the left.",
            "You can save effects as presets.",
            "There is a delay effect included.",
            "I notice that longer releases sound smoother.",
        ],
        "counter_examples": [
            "Longer releases make smoother bass.",  # PRINCIPLE
            "Use longer releases for smooth bass.",  # PROCEDURE or RECOMMENDATION
            "Releases are envelope tail times.",  # CONCEPT
            "Always use longer releases.",  # RECOMMENDATION
        ],
    },

    "RECOMMENDATION": {
        "definition": "A source-endorsed preference, suggestion, or heuristic.",
        "semantic_function": "Suggests an approach; advises trying something.",
        "marks": [
            "explicit recommendation language",
            "source preference",
            "suggested approach",
            "heuristic for design",
        ],
        "examples": [
            "I recommend starting with saw waves.",
            "Try a shorter release for plucks.",
            "For smooth bass, use longer releases.",
            "Consider using a low-pass filter first.",
            "Good approach: start with the oscillators.",
        ],
        "counter_examples": [
            "Saw waves provide bright tone.",  # PRINCIPLE
            "Shorten the release.",  # PROCEDURE
            "Serum includes saw waves.",  # OBSERVATION
            "Saw waves are oscillator waveforms.",  # CONCEPT
        ],
    },

    "CONDITION": {
        "definition": "A circumstance or constraint specifying when something applies.",
        "semantic_function": "Specifies scope, applicability, or conditional constraints.",
        "marks": [
            "when/if qualifiers",
            "contextual constraints",
            "applicability scope",
            "conditional applicability",
        ],
        "examples": [
            "For plucks, shorter releases work better.",
            "When soloing, increase the cutoff frequency.",
            "If you want a brighter tone, use a saw wave.",
            "Unless the envelope is too short, decay sounds smooth.",
            "In minor keys, the bass needs more body.",
        ],
        "counter_examples": [
            "Shorter releases make tighter plucks.",  # PRINCIPLE
            "Shorten the release for plucks.",  # PROCEDURE or CONTEXT
            "I recommend short releases for plucks.",  # RECOMMENDATION + CONTEXT
            "Plucks have tight articulation.",  # OBSERVATION
        ],
    },

    "EXAMPLE": {
        "definition": "A concrete instance used to illustrate another concept/procedure.",
        "semantic_function": "Provides an illustrative case or specific instance.",
        "marks": [
            "illustrative use",
            "specific case",
            "concrete instance",
            "exemplification",
        ],
        "examples": [
            "For example, a saw wave provides brightness.",
            "Like a string resonator.",
            "For instance, the delay effect can add space.",
            "In the bass, you might shorten the release.",
        ],
        "counter_examples": [
            "Saw waves provide brightness.",  # PRINCIPLE or OBSERVATION
            "Use a saw wave.",  # PROCEDURE
            "I recommend saw waves.",  # RECOMMENDATION
        ],
    },

    "CONTEXT": {
        "definition": "Background, setting, credentials, framing, or situational information.",
        "semantic_function": "Provides context for understanding, not action or definition.",
        "marks": [
            "biographical information",
            "credentials",
            "workflow framing",
            "organizational statements",
            "transitions",
            "introductions",
        ],
        "examples": [
            "After teaching Serum for ten years...",
            "Being one of the sound designers...",
            "We'll cover this in more detail later.",
            "Next, let's look at the filters.",
            "So to summarize...",
            "As we move forward in this course...",
        ],
        "counter_examples": [
            "The teaching method is important.",  # PRINCIPLE
            "Start with the basics.",  # PROCEDURE
            "We recommend a structured approach.",  # RECOMMENDATION
        ],
    },

    "LIMITATION": {
        "definition": "A restriction, exception, boundary, or statement about what does not apply.",
        "semantic_function": "Specifies constraints, exceptions, or negative boundaries.",
        "marks": [
            "negative statements",
            "exceptions",
            "restrictions",
            "boundaries",
            "cautions",
        ],
        "examples": [
            "This does not work well with resonant filters.",
            "Don't use this on vocals.",
            "Avoid extreme settings.",
            "Limited to monophonic playback in this mode.",
            "Can't stack more than eight effects.",
        ],
        "counter_examples": [
            "Resonant filters create peaks.",  # PRINCIPLE
            "Use resonant filters carefully.",  # RECOMMENDATION
            "These filters have boundaries.",  # OBSERVATION
        ],
    },

    "FILLER": {
        "definition": "Content that contributes no reusable musical/production knowledge.",
        "semantic_function": "Provides no actionable, conceptual, or strategic music knowledge.",
        "marks": [
            "promotional language",
            "social media requests",
            "organizational navigation",
            "no knowledge transfer",
        ],
        "examples": [
            "Please subscribe to the channel.",
            "Thanks for watching.",
            "Click the link below.",
            "Follow us on social media.",
        ],
        "counter_examples": [
            "Subscribe to stay updated.",  # RECOMMENDATION
            "The channel covers advanced techniques.",  # OBSERVATION
        ],
    },
}

# ========================================================================
# DECISION TREE
# ========================================================================

def classify_semantic(text: str, segment_ids: list) -> dict:
    """
    Classify a proposition by semantic function, not keywords.

    Returns:
        {
            "classification": "CONCEPT" | "PROCEDURE" | ... | "FILLER",
            "confidence": 0.0-1.0,
            "rationale": "explanation",
            "ambiguity": None or "description",
            "candidate_classes": ["CLASS1", "CLASS2", ...],
        }
    """

    # Q1: Is this reusable knowledge?
    if _is_filler(text):
        return {
            "classification": "FILLER",
            "confidence": 0.9,
            "rationale": "promotional/organizational content with no knowledge transfer",
            "ambiguity": None,
        }

    # Q2: Is it primarily background/context?
    if _is_context(text):
        return {
            "classification": "CONTEXT",
            "confidence": 0.85,
            "rationale": "biographical, credentialing, or transitional framing",
            "ambiguity": None,
        }

    # Q3: Is it defining what something is? (CHECK EARLY to avoid false LIMITATION/OBSERVATION)
    if _is_concept(text):
        return {
            "classification": "CONCEPT",
            "confidence": 0.8,
            "rationale": "definition or explanation of a term/construct",
            "ambiguity": None,
        }

    # Q4: Is it a concrete illustrative instance? (CHECK BEFORE PRINCIPLE to avoid "Like" examples being caught)
    if _is_example(text):
        return {
            "classification": "EXAMPLE",
            "confidence": 0.75,
            "rationale": "concrete instance illustrating another concept",
            "ambiguity": None,
        }

    # Q5: Is it explaining a generalized mechanism/relationship? (CHECK BEFORE OBSERVATION)
    if _is_principle(text):
        return {
            "classification": "PRINCIPLE",
            "confidence": 0.8,
            "rationale": "generalized relationship, mechanism, or causal explanation",
            "ambiguity": None,
        }

    # Q6: Is it an explicit actionable instruction/sequence?
    if _is_procedure(text):
        return {
            "classification": "PROCEDURE",
            "confidence": 0.85,
            "rationale": "step-by-step actionable instruction",
            "ambiguity": None,
        }

    # Q7: Is it a limitation/exception?
    if _is_limitation(text):
        return {
            "classification": "LIMITATION",
            "confidence": 0.8,
            "rationale": "boundary, exception, or constraint",
            "ambiguity": None,
        }

    # Q8: Is it explicitly recommending?
    if _is_recommendation(text):
        return {
            "classification": "RECOMMENDATION",
            "confidence": 0.8,
            "rationale": "source-endorsed preference or suggestion",
            "ambiguity": None,
        }

    # Q9: Is it specifying when/how a statement applies?
    if _is_condition(text):
        return {
            "classification": "CONDITION",
            "confidence": 0.7,
            "rationale": "scope/applicability constraint",
            "ambiguity": None,
        }

    # Q10: Is it describing an observed/existing property/state?
    if _is_observation(text):
        return {
            "classification": "OBSERVATION",
            "confidence": 0.75,
            "rationale": "descriptive statement about existing capability or feature",
            "ambiguity": None,
        }

    # Uncertain
    return {
        "classification": "UNKNOWN",
        "confidence": 0.5,
        "rationale": "unable to classify with confidence",
        "ambiguity": "semantic function unclear",
        "candidate_classes": ["OBSERVATION", "PRINCIPLE", "PROCEDURE"],
    }


# ========================================================================
# SEMANTIC DECISION FUNCTIONS
# ========================================================================

def _is_filler(text: str) -> bool:
    """Promotional, social media, organizational, or course-scope statements."""
    filler_markers = [
        "subscribe", "comment", "channel",
        "follow us", "click the link", "twitter", "instagram", "discord",
        "support", "patreon", "become a member", "donate", "buy",
        "thanks for watching", "see you", "goodbye", "take care",
    ]

    scope_markers = [
        "dedicated video", "outside of a", "way too much to cover",
        "will be exploring", "in future videos",
    ]

    text_lower = text.lower().strip()

    # Check if it's very short and filler-like
    if len(text_lower) < 20:
        if any(marker in text_lower for marker in filler_markers):
            return True

    # Check for obvious promotional content
    if any(marker in text_lower for marker in filler_markers):
        if len(text_lower.split()) < 10:
            return True

    # Check for course/video scope statements (meta-commentary, not knowledge)
    if any(marker in text_lower for marker in scope_markers):
        if "will be" in text_lower or "dedicated video" in text_lower:
            return True

    return False


def _is_context(text: str) -> bool:
    """Background, credentials, framing, transitions."""

    text_lower = text.lower().strip()

    # STRICT biographical/credentialing language
    if any(phrase in text_lower for phrase in [
        "after teaching", "years now", "having worked", "being one of",
        "i decided", "i've decided", "my experience",
    ]):
        if len(text_lower) < 400:  # Reasonable length for context
            return True

    # STRICT transitional language (course/video structure)
    if text_lower.startswith("so to summarize"):
        return True
    if text_lower.startswith("to summarize"):
        return True
    if text_lower.startswith("so far when"):
        # "So far when adjusting..." = narrative transition
        return True
    if text_lower.startswith("in this section"):
        # Course framing: "In this section, we'll..."
        return True

    # Explicit course framing
    if text_lower.startswith("next, ") or text_lower.startswith("finally, "):
        # But only if it's brief and transitional
        if len(text_lower) < 100:
            return True

    return False


def _is_concept(text: str) -> bool:
    """Definition or explanation of what something is."""
    definition_markers = [
        " is a ", " is the ", "is defined as", "refers to",
        "means that", "is essentially", "consists of",
    ]

    functional_def_verbs = [
        " takes ", " sequences ", " creates ", " produces ",
        " converts ", " transforms ", " generates ", " outputs ",
    ]

    text_lower = text.lower()

    # Check for explicit definition language (strict matching)
    # "An LFO is a low-frequency oscillator..." = CONCEPT
    if any(marker in text_lower for marker in definition_markers):
        # But verify it's not describing a procedure or action
        if not any(action in text_lower for action in [
            "click", "drag", "adjust", "change", "set", "open", "load",
            "to do", "to make", "to create",
        ]):
            # Also verify it's not an observation with "provides"
            if not any(word in text_lower for word in ["there is", "there are", "you can"]):
                return True

    # Check for "X [does/creates/sequences] Y" functional definitions
    # "arpeggiator, which takes chords and sequences them" = CONCEPT
    if any(verb in text_lower for verb in functional_def_verbs):
        # Must be defining a term, not describing capability
        if any(term in text_lower for term in [
            "arpeggiator", "oscillator", "filter", "envelope", "lfo", "modulation"
        ]):
            # This is a functional definition
            if not _is_procedure(text) and not _is_observation(text):
                return True

    return False


def _is_limitation(text: str) -> bool:
    """Restrictions, exceptions, boundaries."""
    limitation_markers = [
        "don't", "avoid", "never", "not recommended", "can't", "cannot",
        "won't", "doesn't work", "limited to", "exception",
        "caution", "warning", "be careful", "except", "no more than",
        "only allows", "only ",
    ]

    text_lower = text.lower()

    # Check for explicit limitation language
    if any(marker in text_lower for marker in limitation_markers):
        return True

    # Check for "can/cannot" restrictions
    if "cannot" in text_lower or "can not" in text_lower:
        return True

    return False


def _is_procedure(text: str) -> bool:
    """Explicit step-by-step actionable instruction."""
    procedure_indicators = [
        "click", "drag", "press", "hold", "select", "open", "load",
        "save", "adjust", "turn", "set", "change", "enter",
        "first", "then", "next", "finally", "after that",
    ]

    imperative_verbs = [
        "click", "drag", "select", "open", "load", "press", "set",
        "adjust", "turn", "hold", "save", "enter", "change",
    ]

    text_lower = text.lower()

    # Check for procedural imperative language (starts with verb or "to verb")
    if any(text_lower.startswith(verb) for verb in imperative_verbs):
        return True

    if text_lower.startswith("to "):
        return True

    # Check for sequential indicators (first... then...)
    if "first" in text_lower and any(word in text_lower for word in [
        "then", "next", "after", "finally"
    ]):
        return True

    # Check for "click X, then Y" patterns
    if any(indicator in text_lower for indicator in [
        "click and ", "drag and ", "press and ",
    ]):
        return True

    return False


def _is_recommendation(text: str) -> bool:
    """Source-endorsed preference or suggestion."""
    recommendation_markers = [
        "i recommend", "i suggest", "try", "consider",
        "experiment with", "play with", "you should", "good idea",
        "better to", "best to", "advised to",
    ]

    text_lower = text.lower()

    return any(marker in text_lower for marker in recommendation_markers)


def _is_example(text: str) -> bool:
    """Concrete instance illustrating another concept."""
    example_markers = [
        "for example", "such as", "like", "for instance",
        "let's say", "imagine", "suppose", "here's an example",
    ]

    text_lower = text.lower()

    # Check for explicit example markers
    if any(marker in text_lower for marker in example_markers):
        # "like a string resonator" should still be EXAMPLE even mid-sentence
        return True

    return False


def _is_condition(text: str) -> bool:
    """Scope/applicability constraint."""

    text_lower = text.lower()

    # Check for "unless" conditional (strict)
    if text_lower.startswith("unless "):
        return True

    # Check for scope-specifying patterns that START with the condition
    # "For X, use Y", "When X, do Y", "If X, then Y"
    if text_lower.startswith("for ") and not any(word in text_lower for word in [
        "for example", "such as", "for instance"
    ]):
        return True

    if text_lower.startswith("when "):
        # "When X" at the start is a condition, but "when we use" in middle is explanation
        if not " when we use " in text_lower and not " when modulating " in text_lower:
            return True

    if text_lower.startswith("if "):
        return True

    if text_lower.startswith("in case "):
        return True

    return False


def _is_observation(text: str) -> bool:
    """Descriptive statement about existing capability/feature."""
    observation_markers = [
        "there is", "there are", "there's", "you can", "you could",
        "it has", "contains", "includes", "provides",
        "shows", "displays", "allows", "enables",
        "can be", "is available", "i notice", "i see",
    ]

    text_lower = text.lower()

    # Check for explicit "there is/are/there's" statements
    if text_lower.startswith("there is ") or text_lower.startswith("there are ") or text_lower.startswith("there's "):
        return True

    # Check for capability/feature statements
    if any(marker in text_lower for marker in observation_markers):
        # Verify it's not a procedure or recommendation
        if not _is_procedure(text) and not _is_recommendation(text):
            return True

    return False


def _is_principle(text: str) -> bool:
    """Generalized relationship, mechanism, or causal explanation."""
    principle_indicators = [
        "affects", "controls", "determines", "influences",
        "creates", "produces", "results in", "causes",
        "leads to", "enables", "allows", "prevents",
        "behaves", "works", "functions", "operates",
        "flows", "passes through", "travels", "removes",
        "repeat", "cycles", "cyclical",
    ]

    text_lower = text.lower()

    # Do NOT match if this is a pure definition
    if " is a " in text_lower or " is the " in text_lower:
        # "An LFO is a low-frequency oscillator..." = CONCEPT, not PRINCIPLE
        return False

    # Check for comparative/contrastive principle (X vs Y pattern)
    # Detect "X does Y; Z does W" structural contrast
    if any(word in text_lower for word in ["repeat", "cyclical", "once per"]):
        # Semicolon indicates explicit contrast (e.g., "A repeats; B plays once")
        if ";" in text_lower:
            return True
        # Also detect common contrasting connectors without hardcoding specific terms
        if any(connector in text_lower for connector in [" while ", " whereas ", " but ", " unlike "]):
            if len(text_lower.split()) > 10:  # Ensure substantive comparison
                return True

    # Simple mechanism statements (short sentences about what something does)
    # e.g., "Filters remove frequencies to shape tone."
    if any(word in text_lower for word in ["remove", "filter", "shape"]):
        if "filter" in text_lower and ("remove" in text_lower or "frequency" in text_lower):
            if not _is_procedure(text):
                return True

    # Check for generalized behavior language
    if "behave" in text_lower and "same way" in text_lower:
        return True

    # Check for causal/explanatory language
    if any(word in text_lower for word in principle_indicators):
        # Verify it's not a procedure
        if not _is_procedure(text):
            # Verify it's not just describing capability/feature
            capability_words = [
                "you can", "you could", "there is", "allows you", "provides",
                "has", "contains", "shows", "displays"
            ]
            if not any(word in text_lower for word in capability_words):
                return True

    # Check for architectural/structural explanation
    if any(phrase in text_lower for phrase in [
        "passes through", "travels through", "flows through",
        "consists of", "is made of", "contains",
        "organized", "arranged", "structured",
    ]):
        if not _is_procedure(text) and not _is_observation(text):
            return True

    return False
