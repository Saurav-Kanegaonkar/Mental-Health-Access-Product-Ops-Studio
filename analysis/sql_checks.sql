-- SQL checks mirror the synthetic CSV outputs in this public portfolio artifact.

-- 1. Roadmap candidates should have one ranked row each.
select workflow_id, count(*) as rows
from roadmap_priority_queue
group by workflow_id
having count(*) <> 1;

-- 2. No committed sprint candidate should lack instrumentation coverage.
select workflow_id, workflow, instrumentation_coverage
from roadmap_priority_queue
where decision = 'Commit next sprint'
  and instrumentation_coverage < 0.60;

-- 3. Critical inbound items should not be left as low-accountability routing.
select item_id, severity, decision
from inbound_triage_queue
where severity = 'Critical'
  and decision in ('Route to owner', 'Say no with rationale');

-- 4. EHR contracts below readiness threshold need an explicit next step.
select contract_id, workflow, readiness_score, next_step
from ehr_readiness_queue
where readiness_score < 70
  and next_step is null;

-- 5. Incident loops with high recurrence risk should have an owner.
select incident_id, severity, recurrence_risk, followup_owner
from incident_followup_queue
where recurrence_risk >= 75
  and followup_owner is null;
