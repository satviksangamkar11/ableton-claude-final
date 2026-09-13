# Producer Recreation Pipeline — Architecture

## Core Principle

**Raw source data (transcripts) stays completely external to Claude Code reasoning context.**

The pipeline is designed to achieve token-efficient reasoning by separating:
- **External fetching** (no Claude involvement)
- **External extraction** (structured knowledge only)
- **Claude reasoning** (structured knowledge items only)
- **Real execution** (Serum 2 + Ableton MCP)

## Data Flow

```
┌─ EXTERNAL (subprocess, not Claude context) ────────────────┐
│                                                               │
│  YouTube URL                                                 │
│      │                                                        │
│      ├─→ fetch_youtube.py                                   │
│      │     (youtube_transcript_api)                          │
│      │     Downloads transcript                              │
│      │                                                        │
│      ├─→ data/transcripts/<source_id>.json                  │
│      │     (raw transcript artifact on disk)                │
│      │                                                        │
│      ├─→ extract_knowledge.py                               │
│      │     (semantic extraction)                             │
│      │     Converts transcript → structured items            │
│      │                                                        │
│      └─→ data/knowledge/<source_id>.json                    │
│          (structured KnowledgeItems only)                    │
│                                                               │
└────────────────────────────────────────────────────────────┘
                              ↓
┌─ CLAUDE CODE (reasoning with structured knowledge) ────────┐
│                                                               │
│  recreate_reference.py                                       │
│      │                                                        │
│      ├─→ Load only: data/knowledge/<source_id>.json         │
│      │     (343 structured items, ~700KB)                    │
│      │                                                        │
│      ├─→ ProducerBrain.execute(                             │
│      │       source_url=...,                                │
│      │       knowledge_items=[...],  ← structured only      │
│      │       mode=RECREATE_REFERENCE                        │
│      │     )                                                  │
│      │                                                        │
│      │   Determines:                                         │
│      │   - Musical objective                                 │
│      │   - Semantic targets                                  │
│      │   - Capability routes                                 │
│      │   - Human-like operations                             │
│      │                                                        │
│      └─→ Execution plan                                      │
│          (does NOT execute yet)                             │
│                                                               │
└────────────────────────────────────────────────────────────┘
                              ↓
┌─ REAL EXECUTION (external to Claude Code) ─────────────────┐
│                                                               │
│  Route Selection:                                            │
│                                                               │
│  ├─→ SERUM/DAWDREAMER route                                │
│  │     Deep Serum synthesis control                          │
│  │     Uses: DawDreamer + Serum 2.0.21                      │
│  │     Renders: audio                                        │
│  │                                                            │
│  ├─→ ABLETON MCP route                                      │
│  │     Session/MIDI/host control                            │
│  │     Uses: Real Ableton MCP tools                         │
│  │     Produces: MIDI tracks/clips/notes                    │
│  │                                                            │
│  └─→ HYBRID route                                           │
│      Both backends coordinate                               │
│                                                               │
│  Verification:                                               │
│  ├─→ Read back actual state                                 │
│  ├─→ Render                                                  │
│  ├─→ Measure                                                 │
│  └─→ Compare against reference                              │
│                                                               │
│  Episode Persistence:                                        │
│  └─→ Save execution record                                  │
│      for future learning                                    │
│                                                               │
└────────────────────────────────────────────────────────────┘
```

## Token Budget Breakdown

**WITHOUT optimization:**
- Raw YouTube Short transcript: 30K–50K tokens (raw text)
- Semantic extraction analysis: 20K–30K tokens (working memory)
- Reasoning: 50K+ tokens
- **Total: 100K–130K tokens** (too large)

**WITH clean pipeline:**
- Structured KnowledgeItems: 5K–10K tokens (in context)
- Reasoning: 50K–70K tokens
- Execution planning: 10K–20K tokens
- **Total: 65K–100K tokens** (within budget)

**Savings: ~35%** through external processing

## Key Files

### External (Subprocess)
- `source/fetch_youtube.py` — Fetches transcript via youtube_transcript_api
- `source/extract_knowledge.py` — Converts transcript to KnowledgeItems

### Disk Artifacts
- `data/transcripts/<source_id>.json` — Raw transcript (on disk, never loaded into Claude)
- `data/knowledge/<source_id>.json` — Structured KnowledgeItems (Claude reasoning input)

### Claude Reasoning
- `scripts/recreate_reference.py` — Orchestrator (loads only knowledge, not transcript)
- `producer/brain/producer_brain.py` — Core reasoning engine
- `producer/authority/` — Capability authority (evidence, admission, contracts)
- `producer/routing/route_selection.py` — Route advisory (no authority)
- `producer/execution/` — Real Serum/Ableton execution

### Verification
- `tests/test_clean_pipeline.py` — Architecture verification
  - TEST A: Knowledge store exists
  - TEST B: Raw transcript is external
  - TEST C: Structured items accessible
  - TEST D: Claude Code isolation verified
  - TEST E: Producer brain integration ready

## Constraints (Per CLAUDE.md)

1. **Raw transcript never in Claude context** ✓
2. **External fetcher uses youtube_transcript_api** ✓
3. **Knowledge extraction is external subprocess** ✓
4. **Structured items only are reasoned over** ✓
5. **Authority systems are frozen and reused** ✓
6. **Real Serum/Ableton execution only** ✓
7. **Episodes persist for learning** ✓
8. **Measurement-based verification** ✓

## Usage Flow

```bash
# 1. Set up (one-time)
cd producer-recreation
pip install -r requirements.txt

# 2. Fetch & extract (external)
python scripts/recreate_reference.py --url "https://www.youtube.com/watch?v=..."

# 3. Producer brain reasons (Claude Code)
# (Internal to recreate_reference.py)

# 4. Execute (real backends)
# (DawDreamer + Ableton MCP)

# 5. Verify & persist
# (Measurement + episode save)
```

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| External transcript fetch | Keep raw data off-disk in Claude context |
| Subprocess orchestration | Clear process boundary, no token waste |
| Structured KnowledgeItems | Compact, provenance-preserving, reasoning-ready |
| Separate authority layer | Reuse frozen capability contracts exactly |
| Real Serum/Ableton only | No simulation, only measured execution |
| Episode persistence | Enable second-run learning |

## Future Extensions

The clean pipeline is ready to:
1. **Batch multiple references** — Same structure, different URLs
2. **Parallel execution** — Multiple Serum/Ableton backends
3. **Continuous learning** — Episodes drive advisory confidence
4. **A/B testing** — Compare recreation strategies
5. **Domain-specific extraction** — Domain-aware knowledge classifiers

All extensions preserve the core principle: **raw sources external, structured reasoning in Claude Code**.
