# Analysis Plan

## Goal

Create a repeatable Product Ops artifact for a mental-health access product manager scaling a US access workflow. The artifact connects roadmap sequencing, inbound triage, incident follow-up, product instrumentation, and EHR readiness into one decision surface.

## Inputs

- `data/product_workflows.csv` defines roadmap candidates, personas, hypotheses, strategic fit, effort, clinical safety, and EHR dependency.
- `data/weekly_operating_metrics.csv` captures access funnel, routing, support, manual review, latency, and instrumentation coverage by workflow.
- `data/customer_feedback.csv` converts customer, support, partner, interview, and cohort signals into weighted product evidence.
- `data/inbound_triage.csv` captures bugs, CS asks, scope additions, partner requests, and data debt.
- `data/incident_log.csv` tracks severity, detection source, impact, root cause, restore time, and recurrence risk.
- `data/instrumentation_events.csv` models Mixpanel-style event contracts and schema gaps.
- `data/ehr_integration_readiness.csv` tracks FHIR and HL7 contracts for partner integration readiness.
- `data/ceremony_followups.csv` captures the weekly PM operating cadence and follow-up owners.

## Method

1. Aggregate weekly operating metrics by workflow.
2. Score customer signal by volume, severity, and confidence.
3. Score inbound items by urgency, user impact, engineering focus cost, and noise risk.
4. Score incidents by severity, patients affected, restore time, and recurrence risk.
5. Score instrumentation gaps by event health, sample rate, and strategic importance.
6. Keep EHR readiness visible as a separate queue before launch commitments.
7. Rank roadmap candidates and generate sprint-ready project briefs.

## Decision Rule

Items scoring `86+` are candidates to commit next sprint. Items scoring `78-85.9` should be briefed and sized. Items scoring `70-77.9` remain in discovery. Everything else should be monitored until customer signal or operational risk repeats.
