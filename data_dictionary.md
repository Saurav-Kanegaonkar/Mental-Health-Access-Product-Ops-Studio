# Data Dictionary

| File | Grain | Purpose |
| --- | --- | --- |
| `data/product_workflows.csv` | One row per product workflow | Roadmap candidates with persona, problem, hypothesis, effort, safety, and EHR dependency. |
| `data/weekly_operating_metrics.csv` | Workflow-week | Synthetic access funnel, support, manual review, latency, and instrumentation health. |
| `data/customer_feedback.csv` | Feedback signal | Customer, partner, CS, interview, and cohort evidence for roadmap sequencing. |
| `data/inbound_triage.csv` | Inbound item | Bugs, CS asks, partner requests, data debt, and scope additions scored for product triage. |
| `data/incident_log.csv` | Incident | Incident loop inputs: severity, source, impact, root cause, restore time, recurrence risk, and owner. |
| `data/instrumentation_events.csv` | Product event contract | Mixpanel-style event status, required properties, sample rate, schema health, and product question. |
| `data/ehr_integration_readiness.csv` | Integration contract | FHIR and HL7 readiness fields, failure modes, mapping completeness, and next step. |
| `data/ceremony_followups.csv` | Ceremony-week | Operating cadence, action ownership, overdue follow-up, and next artifact. |
| `data/roadmap_briefs.csv` | Project brief | Sprint-ready overview, user story, success metric, acceptance criteria, non-goal, and engineering note. |
| `analysis/outputs/roadmap_priority_queue.csv` | Workflow | Ranked roadmap decision queue. |
| `analysis/outputs/inbound_triage_queue.csv` | Inbound item | Highest-priority triage queue with decision and follow-up. |
| `analysis/outputs/incident_followup_queue.csv` | Incident | Incident closure queue. |
| `analysis/outputs/instrumentation_gap_queue.csv` | Event contract | Event taxonomy and schema gap queue. |
| `analysis/outputs/ehr_readiness_queue.csv` | Integration contract | Lowest-readiness FHIR/HL7 contracts first. |
