# Wyckoff assessment: {instrument}

Use this template for a market assessment. Replace braces with observations; omit inapplicable optional sections. Preserve nulls and named limitations in the JSON companion. Do not treat the illustrative field structure as an observed market case.

## Context and data

- Generated at / information cutoff / timezone / last completed bar:
- Instrument / venue / timeframe / currency and scale:
- Sources / visible or supplied history / adjustments / volume type:
- Assessment mode: causal or retrospective; price-volume or price-only.
- Status and reason:
- Prior trend, higher-timeframe context and unassessed inputs:

## Observations and structure

- Range boundaries and the observations establishing them:
- Candidate structure and phase, or unknown:
- Relative strength, if assessed:

| Event | Observed at | Confirmed at | Status | Supporting observations | Contradictions |
|---|---|---|---|---|---|

## Competing scenarios

For each scenario: thesis, evidence for/against, evidence strength with reasons, trigger and timeframe, trigger status, invalidation rule, conditional path, target method and missing confirmation. If no credible scenario can be formed, state why.

## Decision and update

- Decision rationale and the next observation that would change it:
- Prior report and changes attributable to newly available evidence, if applicable:
- Data limitations and research evidence status:
- Methodology sources used:

## JSON companion

Use this field structure. Array contents below describe fields, not required nonempty records: emit empty events/scenarios when evidence is insufficient. Expand scenarios only from actual observations. Use finite numbers or null; never JSON NaN/Infinity. Emit probability only when its model and held-out calibration are documented in `probability_basis`.

```json
{
  "schema_version": "1.0",
  "skill": "Wyckoff",
  "generated_at": null,
  "as_of": null,
  "timezone": null,
  "symbol": null,
  "venue": null,
  "timeframe": null,
  "last_completed_bar": null,
  "assessment_mode": null,
  "data": {
    "sources": [],
    "history_start": null,
    "adjustments": null,
    "volume_type": null,
    "limitations": []
  },
  "status": null,
  "status_reason": null,
  "structure": null,
  "phase": null,
  "range": {"low": null, "high": null, "basis": null},
  "events": [
    {
      "label": null,
      "criteria": null,
      "observed_at": null,
      "confirmed_at": null,
      "failed_at": null,
      "status": null,
      "status_reason": null,
      "supporting_observations": [],
      "contradictions": []
    }
  ],
  "scenarios": [
    {
      "role": null,
      "thesis": null,
      "supporting_observations": [],
      "contradictions": [],
      "evidence_strength": null,
      "evidence_reason": null,
      "trigger": {"rule": null, "level": null, "timeframe": null, "status": null},
      "invalidation": {"rule": null, "level": null},
      "expected_path": null,
      "target": {"level": null, "method": null},
      "missing_confirmation": [],
      "probability": null,
      "probability_basis": null
    }
  ],
  "next_observation": null,
  "previous_report": null,
  "changes_since_previous": [],
  "research_evidence": {"status": "not_tested", "basis": null},
  "methodology_sources": []
}
```

`assessment_mode` is `causal_price_volume`, `causal_price_only`, `retrospective_price_volume` or `retrospective_price_only`; use null if the mode cannot be established. Scenario `role` is `leading` or `alternative`; trigger `status` is `pending`, `observed` or `unknown`. Event and report statuses follow SKILL.md. Observed triggers require observations available at the cutoff. A confirmed event cannot carry a confirmation time later than `as_of`; when that time is unknowable in a replay, keep it a candidate.
