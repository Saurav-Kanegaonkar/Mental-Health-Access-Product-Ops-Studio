import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"
DOCS = ROOT / "docs" / "images"
RNG = random.Random(5272026)


WORKFLOWS = [
    {
        "workflow_id": "MHA001",
        "product_area": "Access intake",
        "workflow": "Digital self-referral intake routing",
        "persona": "Patient seeking care",
        "problem": "US patients finish an AI-supported access assessment but still need a clear next step into available care.",
        "hypothesis": "A tighter routing handoff will lift completed-to-scheduled conversion while keeping safety review narrow and explicit.",
        "owner_team": "Access PM + Intake Engineering",
        "roadmap_horizon": "Now",
        "strategic_fit": 97,
        "effort": 58,
        "clinical_safety": 91,
        "ehr_dependency": 72,
    },
    {
        "workflow_id": "MHA002",
        "product_area": "Provider supply",
        "workflow": "Therapy referral capacity matching",
        "persona": "Clinic access lead",
        "problem": "Partner clinics need referrals routed toward provider panels that can actually accept the patient within the target window.",
        "hypothesis": "Capacity-aware matching will reduce dead-end referrals and shorten time to first available appointment.",
        "owner_team": "Marketplace Product",
        "roadmap_horizon": "Now",
        "strategic_fit": 94,
        "effort": 63,
        "clinical_safety": 86,
        "ehr_dependency": 66,
    },
    {
        "workflow_id": "MHA003",
        "product_area": "Partner onboarding",
        "workflow": "US clinic launch readiness checklist",
        "persona": "Implementation manager",
        "problem": "US partner launches create repeat questions across consent language, escalation paths, routing rules, and analytics setup.",
        "hypothesis": "A productized launch checklist will compress onboarding time and prevent avoidable post-launch incidents.",
        "owner_team": "Product Ops",
        "roadmap_horizon": "Next",
        "strategic_fit": 86,
        "effort": 44,
        "clinical_safety": 84,
        "ehr_dependency": 50,
    },
    {
        "workflow_id": "MHA004",
        "product_area": "EHR integration",
        "workflow": "Referral status sync into partner EHR",
        "persona": "Clinic operations admin",
        "problem": "Manual status reconciliation makes it hard to know whether a referred patient was accepted, scheduled, or stuck.",
        "hypothesis": "A FHIR-backed status contract will reduce manual follow-up and make access outcomes measurable by partner.",
        "owner_team": "Integrations Engineering",
        "roadmap_horizon": "Now",
        "strategic_fit": 92,
        "effort": 72,
        "clinical_safety": 88,
        "ehr_dependency": 95,
    },
    {
        "workflow_id": "MHA005",
        "product_area": "Safety operations",
        "workflow": "Crisis keyword escalation loop",
        "persona": "Clinical safety reviewer",
        "problem": "High-risk language must move quickly from AI assessment to human review without swamping reviewers with weak signals.",
        "hypothesis": "A tuned escalation loop will preserve safety recall while reducing low-value manual review volume.",
        "owner_team": "Clinical Product + ML",
        "roadmap_horizon": "Now",
        "strategic_fit": 95,
        "effort": 61,
        "clinical_safety": 99,
        "ehr_dependency": 38,
    },
    {
        "workflow_id": "MHA006",
        "product_area": "Partner portal",
        "workflow": "Clinic admin referral queue",
        "persona": "Clinic intake coordinator",
        "problem": "Coordinators need one place to accept, defer, or request more context for a referral.",
        "hypothesis": "A queue with status reasons and SLA prompts will improve acceptance speed and reduce support asks.",
        "owner_team": "Portal Engineering",
        "roadmap_horizon": "Next",
        "strategic_fit": 87,
        "effort": 55,
        "clinical_safety": 76,
        "ehr_dependency": 64,
    },
    {
        "workflow_id": "MHA007",
        "product_area": "Patient activation",
        "workflow": "Assessment completion recovery",
        "persona": "Patient who pauses intake",
        "problem": "Patients who pause during assessment often do not understand whether their progress is saved or how to resume.",
        "hypothesis": "Recovery prompts can lift completion without adding pressure to a sensitive care-seeking moment.",
        "owner_team": "Growth Product",
        "roadmap_horizon": "Next",
        "strategic_fit": 82,
        "effort": 39,
        "clinical_safety": 80,
        "ehr_dependency": 24,
    },
    {
        "workflow_id": "MHA008",
        "product_area": "Product analytics",
        "workflow": "Mixpanel event taxonomy repair",
        "persona": "Product manager",
        "problem": "Event naming drift blocks the team from reading the access funnel without analyst cleanup.",
        "hypothesis": "A governed taxonomy will let PMs and engineers answer funnel, cohort, and incident questions from the data.",
        "owner_team": "Analytics Engineering",
        "roadmap_horizon": "Now",
        "strategic_fit": 90,
        "effort": 36,
        "clinical_safety": 70,
        "ehr_dependency": 28,
    },
    {
        "workflow_id": "MHA009",
        "product_area": "Product operations",
        "workflow": "CS bug and scope intake triage",
        "persona": "Customer success lead",
        "problem": "Bugs, partner asks, implementation gaps, and one-off scope additions compete for the same engineering capacity.",
        "hypothesis": "A triage rubric will protect focus while still giving CS a transparent answer on every inbound item.",
        "owner_team": "Product Ops",
        "roadmap_horizon": "Now",
        "strategic_fit": 89,
        "effort": 33,
        "clinical_safety": 74,
        "ehr_dependency": 42,
    },
]

EVENT_LIBRARY = {
    "MHA001": [
        ("access_assessment_started", "Can we isolate intake starts by market, partner, and acquisition source?"),
        ("access_assessment_completed", "Which patients complete assessment and reach a care-routing decision?"),
        ("care_route_presented", "What route did the user see and did they continue?"),
    ],
    "MHA002": [
        ("provider_capacity_seen", "Was fresh capacity available when routing was decided?"),
        ("referral_match_ranked", "Which match factors changed the recommended provider panel?"),
        ("referral_accepted", "Did the clinic accept the referral within SLA?"),
    ],
    "MHA003": [
        ("partner_launch_gate_completed", "Which launch gate slowed onboarding?"),
        ("implementation_risk_logged", "What operational risk remains before go-live?"),
        ("go_live_qa_passed", "Did the partner pass the QA checklist?"),
    ],
    "MHA004": [
        ("ehr_status_received", "Which partner status updates are received from the EHR?"),
        ("fhir_mapping_failed", "Which required fields fail mapping or validation?"),
        ("referral_status_synced", "Did product and EHR status stay aligned?"),
    ],
    "MHA005": [
        ("safety_phrase_detected", "Which high-risk phrases triggered review?"),
        ("clinical_review_opened", "How quickly did the safety reviewer open the case?"),
        ("escalation_outcome_recorded", "What outcome closed the loop?"),
    ],
    "MHA006": [
        ("admin_queue_opened", "Which coordinator reviewed the queue?"),
        ("referral_status_changed", "What action did the clinic take on the referral?"),
        ("more_context_requested", "What evidence did the clinic need before acceptance?"),
    ],
    "MHA007": [
        ("assessment_paused", "Where do users pause and which prompt can recover them?"),
        ("resume_link_clicked", "Did recovery outreach bring the user back?"),
        ("assessment_recovered", "Did the recovered user complete intake?"),
    ],
    "MHA008": [
        ("event_contract_reviewed", "Which event contract was approved or rejected?"),
        ("property_schema_validated", "Which event properties are missing or malformed?"),
        ("funnel_query_certified", "Can PMs use the funnel without cleanup?"),
    ],
    "MHA009": [
        ("inbound_item_logged", "What type of inbound request entered triage?"),
        ("scope_decision_recorded", "Was the request accepted, declined, merged, or routed?"),
        ("engineering_focus_check", "Which work was protected from churn?"),
    ],
}

CUSTOMER_ACCOUNTS = [
    "Northeast Behavioral Health",
    "Pacific Youth Counseling",
    "Heartland Therapy Network",
    "Canyon County Mental Health",
    "Evergreen Community Care",
    "Metro Access Clinic",
]

ROOT_CAUSES = [
    "instrumentation gap",
    "partner configuration drift",
    "unclear acceptance criteria",
    "stale capacity signal",
    "EHR mapping mismatch",
    "edge-case prompt behavior",
    "manual handoff break",
]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n")


def clamp(value, low, high):
    return max(low, min(high, value))


def pct(value):
    return f"{round(value * 100, 1)}%"


def money(value):
    return f"${value:,.0f}"


def build_workflows():
    return [
        {
            **workflow,
            "okr": "Improve access conversion, reduce avoidable manual work, and keep safety review measurable.",
            "north_star_metric": "completed_to_scheduled_rate",
            "customer_signal": RNG.randint(62, 96),
        }
        for workflow in WORKFLOWS
    ]


def build_weekly_metrics():
    rows = []
    weeks = [f"2026-W{week:02d}" for week in range(7, 19)]
    for workflow in WORKFLOWS:
        base_started = RNG.randint(850, 2400)
        for index, week in enumerate(weeks):
            drift = 1 + (index * RNG.uniform(-0.005, 0.018))
            started = int(base_started * drift * RNG.uniform(0.88, 1.14))
            completion_rate = clamp(RNG.uniform(0.54, 0.78) + workflow["strategic_fit"] / 900 - workflow["effort"] / 1200, 0.42, 0.87)
            routed_rate = clamp(completion_rate * RNG.uniform(0.54, 0.82), 0.25, 0.74)
            rows.append(
                {
                    "week": week,
                    "workflow_id": workflow["workflow_id"],
                    "product_area": workflow["product_area"],
                    "assessment_starts": started,
                    "assessment_completions": int(started * completion_rate),
                    "routed_to_care": int(started * routed_rate),
                    "completed_to_scheduled_rate": round(clamp(routed_rate * RNG.uniform(0.72, 0.96), 0.18, 0.66), 4),
                    "avg_time_to_first_slot_days": round(clamp(RNG.uniform(5.2, 18.4) + workflow["ehr_dependency"] / 24, 4.5, 23.5), 1),
                    "cs_tickets": int(RNG.uniform(7, 44) + workflow["effort"] / 4),
                    "manual_review_rate": round(clamp(RNG.uniform(0.08, 0.29) + workflow["clinical_safety"] / 750, 0.05, 0.42), 4),
                    "instrumentation_coverage": round(clamp(RNG.uniform(0.54, 0.92) - workflow["ehr_dependency"] / 800, 0.38, 0.97), 4),
                    "median_latency_ms": int(clamp(RNG.uniform(280, 1300) + workflow["effort"] * 6, 210, 1900)),
                }
            )
    return rows


def build_feedback():
    themes = [
        ("Referral dead end", "Patient had a route but the clinic could not accept the referral."),
        ("Assessment pause anxiety", "Patient did not know whether answers were saved after pausing intake."),
        ("Crisis escalation clarity", "Reviewer needed sharper reason codes for high-risk language."),
        ("Partner launch confusion", "Implementation team needed one answer on consent, routing, and reporting setup."),
        ("Status reconciliation", "Clinic admin could not tell whether product status matched the EHR."),
        ("Event name drift", "PM could not compare funnel steps across partner launches."),
    ]
    rows = []
    for index in range(72):
        workflow = RNG.choice(WORKFLOWS)
        theme, need = RNG.choice(themes)
        volume = RNG.randint(3, 41)
        severity = RNG.choice([3, 4, 5, 6, 7, 8, 9])
        rows.append(
            {
                "signal_id": f"SIG-{index + 1:03d}",
                "week": f"2026-W{RNG.randint(7, 18):02d}",
                "workflow_id": workflow["workflow_id"],
                "source": RNG.choice(["Customer success note", "Partner QBR", "Support ticket", "User interview", "Mixpanel cohort readout"]),
                "customer_account": RNG.choice(CUSTOMER_ACCOUNTS),
                "theme": theme,
                "user_need": need,
                "volume": volume,
                "severity": severity,
                "confidence": round(RNG.uniform(0.58, 0.94), 2),
                "product_interpretation": f"Treat as {'roadmap input' if severity >= 7 else 'triage evidence'} for {workflow['workflow']}.",
            }
        )
    return rows


def build_inbound():
    rows = []
    item_types = ["Bug", "CS ask", "Scope addition", "Data debt", "Partner request"]
    for index in range(96):
        workflow = RNG.choice(WORKFLOWS)
        item_type = RNG.choice(item_types)
        severity = RNG.choice(["Low", "Medium", "Medium", "High", "High", "Critical"])
        users = RNG.randint(8, 1100)
        urgency = {"Low": 18, "Medium": 42, "High": 72, "Critical": 94}[severity]
        noise_risk = RNG.randint(8, 40) if item_type in ["Scope addition", "Partner request"] else RNG.randint(2, 24)
        focus_cost = RNG.randint(3, 28)
        score = round(urgency * 0.42 + min(users / 14, 40) + workflow["strategic_fit"] * 0.18 - noise_risk * 0.22 - focus_cost * 0.35, 1)
        if severity == "Critical" or score >= 84:
            decision = "Ship next"
        elif item_type == "Scope addition" and score < 58:
            decision = "Say no with rationale"
        elif score < 48:
            decision = "Route to owner"
        else:
            decision = "Merge into epic"
        rows.append(
            {
                "item_id": f"IN-{index + 1:03d}",
                "created_week": f"2026-W{RNG.randint(7, 18):02d}",
                "workflow_id": workflow["workflow_id"],
                "item_type": item_type,
                "severity": severity,
                "customer_account": RNG.choice(CUSTOMER_ACCOUNTS),
                "users_impacted": users,
                "root_cause": RNG.choice(ROOT_CAUSES),
                "engineering_focus_cost": focus_cost,
                "noise_risk": noise_risk,
                "triage_score": score,
                "decision": decision,
                "owner": workflow["owner_team"],
                "follow_up": RNG.choice(
                    [
                        "Add to sprint review decision log",
                        "Pair PM and engineer for 30-minute scope review",
                        "Send CS-facing rationale and workaround",
                        "Convert into acceptance criteria",
                        "Wait for second customer signal",
                    ]
                ),
            }
        )
    return rows


def build_incidents():
    rows = []
    incident_types = [
        ("Delayed referral status update", "Partner status webhook lagged behind product state."),
        ("Assessment completion drop", "A mobile validation bug blocked assessment completion."),
        ("Safety review backlog", "High-risk phrase rule increased reviewer queue volume."),
        ("Clinic capacity stale", "Provider capacity was older than routing SLA."),
        ("Event ingestion delay", "Mixpanel event stream missed one partner cohort."),
    ]
    for index in range(28):
        workflow = RNG.choice(WORKFLOWS)
        incident_type, summary = RNG.choice(incident_types)
        severity = RNG.choice(["SEV3", "SEV3", "SEV2", "SEV2", "SEV1"])
        patients = RNG.randint(12, 950)
        ack = RNG.randint(8, 95)
        restore = round(RNG.uniform(1.5, 31.0), 1)
        recurrence = RNG.randint(24, 92)
        followup_score = round({"SEV1": 36, "SEV2": 24, "SEV3": 12}[severity] + patients / 38 + recurrence * 0.42 + restore * 0.65, 1)
        rows.append(
            {
                "incident_id": f"INC-{index + 1:03d}",
                "detected_week": f"2026-W{RNG.randint(7, 18):02d}",
                "workflow_id": workflow["workflow_id"],
                "incident_type": incident_type,
                "summary": summary,
                "severity": severity,
                "detection_source": RNG.choice(["Sentry alert", "CS escalation", "Mixpanel anomaly", "Partner report", "Clinical reviewer"]),
                "patients_impacted": patients,
                "minutes_to_ack": ack,
                "hours_to_restore": restore,
                "root_cause": RNG.choice(ROOT_CAUSES),
                "recurrence_risk": recurrence,
                "followup_score": followup_score,
                "status": RNG.choice(["Monitoring", "Fix shipped", "RCA drafted", "Needs owner", "Follow-up scheduled"]),
                "followup_owner": workflow["owner_team"],
            }
        )
    return rows


def build_instrumentation():
    rows = []
    statuses = ["Live", "Live", "Needs QA", "Missing", "Schema drift"]
    for workflow in WORKFLOWS:
        for index, (event_name, question) in enumerate(EVENT_LIBRARY[workflow["workflow_id"]], start=1):
            status = RNG.choice(statuses)
            sample_rate = 1 if status == "Live" else round(RNG.uniform(0.14, 0.88), 2)
            property_health = RNG.randint(42, 98) if status != "Missing" else RNG.randint(12, 46)
            gap_score = round((100 - property_health) * 0.62 + (1 - sample_rate) * 30 + (workflow["strategic_fit"] / 10), 1)
            rows.append(
                {
                    "event_id": f"EVT-{workflow['workflow_id']}-{index}",
                    "workflow_id": workflow["workflow_id"],
                    "event_name": event_name,
                    "mixpanel_status": status,
                    "product_question": question,
                    "required_properties": RNG.choice(
                        [
                            "partner_id, market, route, source, cohort_id",
                            "user_id, referral_id, provider_panel, status_reason",
                            "partner_id, ehr_vendor, endpoint, error_code",
                            "session_id, clinical_risk_band, reviewer_queue",
                        ]
                    ),
                    "sample_rate": sample_rate,
                    "property_health": property_health,
                    "last_seen_week": f"2026-W{RNG.randint(7, 18):02d}" if status != "Missing" else "not seen",
                    "gap_score": gap_score,
                    "owner": RNG.choice(["PM", "Analytics Engineering", "Platform Engineering", "Product Ops"]),
                }
            )
    return rows


def build_ehr_readiness():
    endpoints = [
        ("FHIR Appointment", "Appointment.status, Appointment.participant, Schedule.actor"),
        ("FHIR ServiceRequest", "ServiceRequest.status, category, authoredOn, requester"),
        ("FHIR Patient", "Patient.identifier, telecom, address, communication"),
        ("HL7 SIU", "SCH, PID, PV1, AIP segments"),
        ("HL7 ADT", "MSH, EVN, PID, PV1 segments"),
    ]
    rows = []
    for workflow in WORKFLOWS:
        endpoint, fields = RNG.choice(endpoints)
        mapping = clamp(RNG.randint(45, 94) - workflow["ehr_dependency"] // 10, 22, 96)
        sandbox = RNG.choice(["Not started", "Sandbox mapped", "Partner testing", "Pilot ready", "Live"])
        failure_rate = round(clamp(RNG.uniform(0.02, 0.22) + workflow["ehr_dependency"] / 1200, 0.01, 0.32), 3)
        readiness = round(mapping * 0.48 + (100 - failure_rate * 100) * 0.24 + (100 - workflow["effort"]) * 0.12 + workflow["strategic_fit"] * 0.16, 1)
        rows.append(
            {
                "contract_id": f"EHR-{workflow['workflow_id']}",
                "workflow_id": workflow["workflow_id"],
                "workflow": workflow["workflow"],
                "endpoint": endpoint,
                "required_fields": fields,
                "ehr_dependency": workflow["ehr_dependency"],
                "mapping_completeness": mapping,
                "failure_rate": failure_rate,
                "sandbox_status": sandbox,
                "top_failure_mode": RNG.choice(
                    [
                        "status code mismatch",
                        "missing partner identifier",
                        "timezone normalization",
                        "duplicate referral id",
                        "unsupported appointment reason",
                    ]
                ),
                "readiness_score": readiness,
                "next_step": RNG.choice(
                    [
                        "Lock data contract before sprint planning",
                        "Run partner sandbox replay",
                        "Add validation event to Mixpanel",
                        "Confirm owner for error queue",
                    ]
                ),
            }
        )
    return rows


def build_ceremonies():
    rows = []
    ceremonies = [
        ("Monday roadmap sequencing", "Align next-highest-value project and capacity tradeoffs"),
        ("Tuesday inbound triage", "Separate real issues from noise and assign a clear answer"),
        ("Wednesday incident loop", "Review open incidents, RCAs, and follow-up owners"),
        ("Thursday instrumentation review", "Make sure product questions can be answered from data"),
        ("Friday scope guardrail", "Close decisions and protect engineering focus before weekend drift"),
    ]
    for week in range(15, 19):
        for ceremony, purpose in ceremonies:
            open_actions = RNG.randint(2, 9)
            overdue = RNG.randint(0, 3)
            alignment = RNG.randint(71, 96)
            rows.append(
                {
                    "week": f"2026-W{week:02d}",
                    "ceremony": ceremony,
                    "purpose": purpose,
                    "attendees": RNG.choice(["PM, EM, Design, CS", "PM, EM, Clinical, CS", "PM, Analytics, Engineering", "PM, Product Ops, CS"]),
                    "open_actions": open_actions,
                    "overdue_actions": overdue,
                    "alignment_score": alignment,
                    "follow_up_owner": RNG.choice(["Product Manager", "Engineering Manager", "Analytics Lead", "CS Lead"]),
                    "next_artifact": RNG.choice(["Decision log", "Sprint brief", "RCA note", "Metric contract", "CS response template"]),
                }
            )
    return rows


def build_briefs():
    rows = []
    for workflow in WORKFLOWS:
        rows.append(
            {
                "brief_id": f"BRF-{workflow['workflow_id']}",
                "workflow_id": workflow["workflow_id"],
                "project_overview": f"Improve {workflow['workflow'].lower()} for {workflow['persona'].lower()} by converting the current ambiguity into a measured, owned workflow.",
                "user_story": f"As a {workflow['persona'].lower()}, I need {workflow['problem'][0].lower() + workflow['problem'][1:]}",
                "success_metric": RNG.choice(
                    [
                        "completed_to_scheduled_rate",
                        "time_to_first_slot_days",
                        "manual_review_rate",
                        "referral_acceptance_within_sla",
                        "instrumentation_coverage",
                    ]
                ),
                "acceptance_criteria": RNG.choice(
                    [
                        "PM, engineering, CS, and clinical owner agree on launch metric and rollback signal.",
                        "Workflow has event coverage, owner, QA path, and customer-facing rationale.",
                        "Incident and support handoff are documented before production rollout.",
                        "Partner-facing status reason is visible and exportable.",
                    ]
                ),
                "non_goal": RNG.choice(
                    [
                        "Do not build bespoke behavior for a single partner until signal repeats.",
                        "Do not automate clinical judgment beyond the agreed escalation policy.",
                        "Do not add a new analytics surface before fixing the event contract.",
                        "Do not expand EHR scope until the status contract is stable.",
                    ]
                ),
                "engineering_note": RNG.choice(
                    [
                        "Use a narrow interface and preserve a manual override.",
                        "Add fixture-based tests around partner configuration.",
                        "Sequence schema migration before UI work.",
                        "Timebox discovery and keep the sprint goal unchanged.",
                    ]
                ),
            }
        )
    return rows


def rollups(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr):
    metrics_by_workflow = defaultdict(list)
    for row in weekly:
        metrics_by_workflow[row["workflow_id"]].append(row)

    feedback_by_workflow = defaultdict(list)
    for row in feedback:
        feedback_by_workflow[row["workflow_id"]].append(row)

    inbound_by_workflow = defaultdict(list)
    for row in inbound:
        inbound_by_workflow[row["workflow_id"]].append(row)

    incidents_by_workflow = defaultdict(list)
    for row in incidents:
        incidents_by_workflow[row["workflow_id"]].append(row)

    instr_by_workflow = defaultdict(list)
    for row in instrumentation:
        instr_by_workflow[row["workflow_id"]].append(row)

    ehr_by_workflow = {row["workflow_id"]: row for row in ehr}

    queue = []
    for workflow in workflows:
        wf_id = workflow["workflow_id"]
        rows = metrics_by_workflow[wf_id]
        feedback_rows = feedback_by_workflow[wf_id]
        inbound_rows = inbound_by_workflow[wf_id]
        incident_rows = incidents_by_workflow[wf_id]
        instr_rows = instr_by_workflow[wf_id]
        avg_conversion = statistics.mean(float(row["completed_to_scheduled_rate"]) for row in rows)
        avg_slot = statistics.mean(float(row["avg_time_to_first_slot_days"]) for row in rows)
        avg_tickets = statistics.mean(int(row["cs_tickets"]) for row in rows)
        avg_coverage = statistics.mean(float(row["instrumentation_coverage"]) for row in rows)
        signal_score = sum(int(row["volume"]) * int(row["severity"]) * float(row["confidence"]) for row in feedback_rows) / max(1, len(feedback_rows))
        inbound_pressure = statistics.mean(float(row["triage_score"]) for row in inbound_rows) if inbound_rows else 0
        incident_pressure = statistics.mean(float(row["followup_score"]) for row in incident_rows) if incident_rows else 0
        instrumentation_gap = statistics.mean(float(row["gap_score"]) for row in instr_rows)
        ehr_readiness = float(ehr_by_workflow[wf_id]["readiness_score"])
        impact = int((1 - avg_conversion) * 88000 + avg_tickets * 950 + incident_pressure * 1800 + signal_score * 55)
        priority = round(
            workflow["strategic_fit"] * 0.22
            + workflow["clinical_safety"] * 0.13
            + min(signal_score / 10, 25)
            + min(inbound_pressure / 4, 24)
            + min(incident_pressure / 5, 24)
            + instrumentation_gap * 0.11
            + (100 - workflow["effort"]) * 0.08
            + (100 - ehr_readiness) * 0.06,
            1,
        )
        if priority >= 86:
            decision = "Commit next sprint"
        elif priority >= 78:
            decision = "Prepare next brief"
        elif priority >= 70:
            decision = "Keep in discovery"
        else:
            decision = "Monitor"
        queue.append(
            {
                "workflow_id": wf_id,
                "product_area": workflow["product_area"],
                "workflow": workflow["workflow"],
                "owner_team": workflow["owner_team"],
                "roadmap_horizon": workflow["roadmap_horizon"],
                "priority_score": priority,
                "decision": decision,
                "avg_completed_to_scheduled_rate": round(avg_conversion, 4),
                "avg_time_to_first_slot_days": round(avg_slot, 1),
                "avg_weekly_cs_tickets": round(avg_tickets, 1),
                "instrumentation_coverage": round(avg_coverage, 3),
                "open_incidents": len([row for row in incident_rows if row["status"] != "Fix shipped"]),
                "ehr_readiness_score": ehr_readiness,
                "estimated_access_impact": impact,
                "next_step": next(row["follow_up"] for row in sorted(inbound_rows, key=lambda item: float(item["triage_score"]), reverse=True)),
            }
        )
    return sorted(queue, key=lambda row: row["priority_score"], reverse=True)


def write_outputs(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr, ceremonies, briefs, queue):
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUTS / "roadmap_priority_queue.csv",
        queue,
        [
            "workflow_id",
            "product_area",
            "workflow",
            "owner_team",
            "roadmap_horizon",
            "priority_score",
            "decision",
            "avg_completed_to_scheduled_rate",
            "avg_time_to_first_slot_days",
            "avg_weekly_cs_tickets",
            "instrumentation_coverage",
            "open_incidents",
            "ehr_readiness_score",
            "estimated_access_impact",
            "next_step",
        ],
    )
    write_csv(OUTPUTS / "inbound_triage_queue.csv", sorted(inbound, key=lambda row: float(row["triage_score"]), reverse=True)[:40], list(inbound[0].keys()))
    write_csv(OUTPUTS / "incident_followup_queue.csv", sorted(incidents, key=lambda row: float(row["followup_score"]), reverse=True), list(incidents[0].keys()))
    write_csv(OUTPUTS / "instrumentation_gap_queue.csv", sorted(instrumentation, key=lambda row: float(row["gap_score"]), reverse=True), list(instrumentation[0].keys()))
    write_csv(OUTPUTS / "ehr_readiness_queue.csv", sorted(ehr, key=lambda row: float(row["readiness_score"])), list(ehr[0].keys()))
    write_csv(OUTPUTS / "ceremony_followups.csv", ceremonies, list(ceremonies[0].keys()))
    write_csv(OUTPUTS / "project_briefs.csv", briefs, list(briefs[0].keys()))

    top = queue[0]
    inbound_counts = Counter(row["decision"] for row in inbound)
    incident_counts = Counter(row["severity"] for row in incidents)
    missing_events = [row for row in instrumentation if row["mixpanel_status"] in ["Missing", "Schema drift"]]
    summary = {
        "workflow_count": len(workflows),
        "weekly_metric_rows": len(weekly),
        "inbound_items": len(inbound),
        "open_incidents": len([row for row in incidents if row["status"] != "Fix shipped"]),
        "events_with_gaps": len(missing_events),
        "ehr_contracts": len(ehr),
        "top_workflow": top,
        "commit_next": len([row for row in queue if row["decision"] == "Commit next sprint"]),
        "avg_instrumentation_coverage": round(statistics.mean(float(row["instrumentation_coverage"]) for row in queue), 3),
        "inbound_counts": dict(inbound_counts),
        "incident_counts": dict(incident_counts),
    }
    payload = {
        "summary": summary,
        "workflows": workflows,
        "roadmapQueue": queue,
        "weeklyMetrics": weekly,
        "feedbackSignals": sorted(feedback, key=lambda row: int(row["volume"]) * int(row["severity"]), reverse=True)[:18],
        "inboundQueue": sorted(inbound, key=lambda row: float(row["triage_score"]), reverse=True)[:28],
        "incidents": sorted(incidents, key=lambda row: float(row["followup_score"]), reverse=True)[:18],
        "instrumentation": sorted(instrumentation, key=lambda row: float(row["gap_score"]), reverse=True),
        "ehrReadiness": sorted(ehr, key=lambda row: float(row["readiness_score"])),
        "ceremonies": ceremonies,
        "briefs": briefs,
    }
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUTS / "app_payload.json").write_text(json.dumps(payload, indent=2))


def write_docs(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr, ceremonies, briefs, queue):
    top = queue[0]
    second = queue[1]
    third = queue[2]
    avg_coverage = statistics.mean(float(row["instrumentation_coverage"]) for row in queue)
    open_incidents = len([row for row in incidents if row["status"] != "Fix shipped"])
    missing_events = len([row for row in instrumentation if row["mixpanel_status"] in ["Missing", "Schema drift"]])

    write_text(
        ANALYSIS / "executive_findings.md",
        f"""
# Executive Findings

## Recommendation

Prioritize **{top['workflow']}** for the next sprint, with **{second['workflow']}** and **{third['workflow']}** held as the next two sequenced projects. The top queue item combines high access impact, recurring customer signal, incident pressure, and measurement gaps that the team can close without letting one-off scope additions dominate engineering focus.

## What the operating model shows

- **{top['workflow']}** has the highest priority score at `{top['priority_score']}` and an estimated access impact of `{money(top['estimated_access_impact'])}`.
- The artifact triages `{len(inbound)}` inbound items across bugs, CS asks, data debt, partner requests, and scope additions.
- `{open_incidents}` incident loops remain open, with follow-up scored by severity, affected patients, restore time, and recurrence risk.
- Mixpanel-style coverage averages `{pct(avg_coverage)}` across roadmap candidates, and `{missing_events}` tracked events still need schema repair or first instrumentation.
- EHR readiness is intentionally separated from roadmap score so FHIR and HL7 dependencies are visible before a project enters sprint planning.

## PM operating decision

Commit the next sprint to the highest-scoring access workflow, run the incident review and instrumentation review as separate ceremonies, and give CS a transparent answer on lower-scoring inbound asks. The product manager should protect engineering focus by merging related asks into existing epics and declining low-signal scope additions with the evidence captured in `inbound_triage_queue.csv`.
""",
    )

    write_text(
        ANALYSIS / "analysis_plan.md",
        """
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
""",
    )

    write_text(
        ANALYSIS / "methodology.md",
        """
# Methodology

The artifact uses deterministic synthetic data shaped like a mental-health access product operation. It does not represent Limbic, partner clinics, patients, or production systems.

Roadmap priority combines strategic fit, clinical safety, customer signal, inbound pressure, incident pressure, instrumentation gaps, effort, and EHR readiness. The score is intentionally explainable so a PM can challenge inputs with engineering, clinical, CS, and implementation stakeholders.

Incident follow-up is separated from roadmap priority because incident loops need accountable closure even when the long-term roadmap bet is different. Instrumentation and EHR readiness are also separated so a team can see when a project is blocked by missing data contracts rather than product ambiguity.
""",
    )

    write_text(
        ANALYSIS / "sql_checks.sql",
        """
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
""",
    )

    write_text(
        ROOT / "data_dictionary.md",
        """
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
""",
    )

    write_text(
        DATA / "README.md",
        """
# Synthetic Data Notes

All rows in this folder are deterministic synthetic data for a public portfolio artifact. They do not represent Limbic, real patients, real clinics, partner EHRs, support tickets, incidents, clinical safety reviews, or customer accounts.

The files are shaped to show how a product manager for an AI-enabled mental-health access product could sequence roadmap work, protect engineering focus, manage incidents, inspect Mixpanel-style instrumentation, and reason about EHR integration readiness.
""",
    )

    write_text(
        ROOT / "README.md",
        f"""
# Mental Health Access Product Ops Studio

An interactive Product Ops portfolio artifact for an AI-powered mental-health access product scaling in the US market. The studio shows how a product manager can run roadmap sequencing, inbound triage, incident follow-up, instrumentation review, and EHR-readiness decisions without turning every customer ask into engineering churn.

![Mental Health Access Product Ops Studio](docs/images/dashboard.png)

## What This Project Demonstrates

- Roadmap prioritization grounded in customer signal, usage behavior, support pressure, incident risk, effort, and clinical-safety sensitivity.
- Product ceremonies with follow-up owners, overdue actions, and decision artifacts.
- Inbound triage that separates bugs, data debt, CS asks, partner requests, and scope additions.
- Incident loops with severity, root cause, restore time, recurrence risk, and follow-up owner.
- Mixpanel-style event instrumentation that makes funnel and product behavior answerable by the team.
- FHIR and HL7 readiness thinking for EHR-adjacent referral status workflows.

## Data Sources

- `data/product_workflows.csv` - `{len(workflows)}` roadmap candidates
- `data/weekly_operating_metrics.csv` - `{len(weekly)}` workflow-week access rows
- `data/customer_feedback.csv` - `{len(feedback)}` customer and partner signal rows
- `data/inbound_triage.csv` - `{len(inbound)}` bug, CS, partner, scope, and data-debt rows
- `data/incident_log.csv` - `{len(incidents)}` incident loop records
- `data/instrumentation_events.csv` - `{len(instrumentation)}` Mixpanel-style event contracts
- `data/ehr_integration_readiness.csv` - `{len(ehr)}` EHR integration readiness contracts
- `data/ceremony_followups.csv` - `{len(ceremonies)}` PM operating ceremony records

## Analysis Outputs

- `analysis/outputs/roadmap_priority_queue.csv`
- `analysis/outputs/inbound_triage_queue.csv`
- `analysis/outputs/incident_followup_queue.csv`
- `analysis/outputs/instrumentation_gap_queue.csv`
- `analysis/outputs/ehr_readiness_queue.csv`
- `analysis/outputs/project_briefs.csv`
- `analysis/outputs/app_payload.json`
- `analysis/executive_findings.md`
- `analysis/analysis_plan.md`
- `analysis/methodology.md`
- `analysis/sql_checks.sql`

## Current Recommendation

Commit next sprint to **{top['workflow']}**. It has the highest priority score (`{top['priority_score']}`), estimated access impact of `{money(top['estimated_access_impact'])}`, and the strongest overlap between access outcomes, incident pressure, and instrumentation gaps.

## Run Locally

```bash
npm run analyze
npm run start
```

Then open `http://localhost:4173`.

## Portfolio Framing

This is a public portfolio artifact with reproducible synthetic data and transparent rules-based scoring. It does not connect to live product analytics, EHRs, support systems, patient records, partner clinics, or production AI models. It demonstrates how a Product Manager can translate customer signal, engineering constraints, incident loops, and instrumentation quality into an actionable operating cadence.
""",
    )

    write_text(
        ROOT / "STATUS.md",
        """
# Status

- Project: Mental Health Access Product Ops Studio
- GitHub: https://github.com/Saurav-Kanegaonkar/Mental-Health-Access-Product-Ops-Studio
- Status: upgraded through the Portfolio Artifact Upgrade Workflow
- Resume Link Ready: Yes, after review and push
- Last update: Tailored for a Limbic-style Product Manager role focused on AI-powered mental-health access, roadmap prioritization, inbound triage, incident loops, Mixpanel instrumentation, and EHR-adjacent readiness.
""",
    )


def main():
    workflows = build_workflows()
    weekly = build_weekly_metrics()
    feedback = build_feedback()
    inbound = build_inbound()
    incidents = build_incidents()
    instrumentation = build_instrumentation()
    ehr = build_ehr_readiness()
    ceremonies = build_ceremonies()
    briefs = build_briefs()
    queue = rollups(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr)

    write_csv(DATA / "product_workflows.csv", workflows, list(workflows[0].keys()))
    write_csv(DATA / "weekly_operating_metrics.csv", weekly, list(weekly[0].keys()))
    write_csv(DATA / "customer_feedback.csv", feedback, list(feedback[0].keys()))
    write_csv(DATA / "inbound_triage.csv", inbound, list(inbound[0].keys()))
    write_csv(DATA / "incident_log.csv", incidents, list(incidents[0].keys()))
    write_csv(DATA / "instrumentation_events.csv", instrumentation, list(instrumentation[0].keys()))
    write_csv(DATA / "ehr_integration_readiness.csv", ehr, list(ehr[0].keys()))
    write_csv(DATA / "ceremony_followups.csv", ceremonies, list(ceremonies[0].keys()))
    write_csv(DATA / "roadmap_briefs.csv", briefs, list(briefs[0].keys()))
    write_outputs(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr, ceremonies, briefs, queue)
    write_docs(workflows, weekly, feedback, inbound, incidents, instrumentation, ehr, ceremonies, briefs, queue)

    print("Top roadmap priorities")
    for row in queue[:5]:
        print(
            f"{row['workflow_id']} {row['workflow']}: score={row['priority_score']}, "
            f"decision={row['decision']}, impact={money(row['estimated_access_impact'])}"
        )


if __name__ == "__main__":
    main()
