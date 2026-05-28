# Executive Findings

## Recommendation

Prioritize **Crisis keyword escalation loop** for the next sprint, with **Therapy referral capacity matching** and **CS bug and scope intake triage** held as the next two sequenced projects. The top queue item combines high access impact, recurring customer signal, incident pressure, and measurement gaps that the team can close without letting one-off scope additions dominate engineering focus.

## What the operating model shows

- **Crisis keyword escalation loop** has the highest priority score at `86.1` and an estimated access impact of `$209,860`.
- The artifact triages `96` inbound items across bugs, CS asks, data debt, partner requests, and scope additions.
- `26` incident loops remain open, with follow-up scored by severity, affected patients, restore time, and recurrence risk.
- Mixpanel-style coverage averages `65.9%` across roadmap candidates, and `7` tracked events still need schema repair or first instrumentation.
- EHR readiness is intentionally separated from roadmap score so FHIR and HL7 dependencies are visible before a project enters sprint planning.

## PM operating decision

Commit the next sprint to the highest-scoring access workflow, run the incident review and instrumentation review as separate ceremonies, and give CS a transparent answer on lower-scoring inbound asks. The product manager should protect engineering focus by merging related asks into existing epics and declining low-signal scope additions with the evidence captured in `inbound_triage_queue.csv`.
