const state = {
  payload: null,
  tab: "command",
  workflowId: null,
};

const app = document.querySelector("#app");
const numberFmt = new Intl.NumberFormat("en-US");
const moneyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const tabs = [
  ["command", "Command"],
  ["roadmap", "Roadmap"],
  ["triage", "Triage"],
  ["incidents", "Incidents"],
  ["data", "Data"],
  ["cadence", "Cadence"],
];

function num(value) {
  return Number(value);
}

function percent(value) {
  return `${Math.round(num(value) * 100)}%`;
}

function money(value) {
  return moneyFmt.format(num(value));
}

function scoreClass(value) {
  const score = num(value);
  if (score >= 86) return "good";
  if (score >= 78) return "watch";
  return "risk";
}

function pill(value) {
  return `<span class="pill ${String(value).toLowerCase().replaceAll(" ", "-")}">${value}</span>`;
}

function metric(label, value, detail) {
  return `
    <article class="metric-card">
      <span>${label}</span>
      <strong>${value}</strong>
      <p>${detail}</p>
    </article>
  `;
}

function bar(value, max, label) {
  const width = Math.max(4, Math.min(100, Math.round((num(value) / max) * 100)));
  return `
    <div class="bar-row">
      <span>${label}</span>
      <div class="bar"><i style="width:${width}%"></i></div>
      <strong>${value}</strong>
    </div>
  `;
}

function activeWorkflow() {
  return state.payload.roadmapQueue.find((row) => row.workflow_id === state.workflowId) || state.payload.roadmapQueue[0];
}

function shell(content) {
  const { summary } = state.payload;
  const top = summary.top_workflow;
  app.innerHTML = `
    <main class="shell">
      <section class="hero">
        <div class="hero-copy">
          <p class="eyebrow">AI mental-health access product ops</p>
          <h1>Mental Health Access Product Ops Studio</h1>
          <p>Roadmap sequencing, inbound triage, incident follow-up, Mixpanel instrumentation, and EHR-readiness decisions for a US access product team.</p>
        </div>
        <aside class="decision-panel">
          <span>Recommended next sprint</span>
          <strong>${top.workflow}</strong>
          <p>${top.next_step}</p>
        </aside>
      </section>

      <section class="metrics-grid">
        ${metric("Roadmap candidates", summary.workflow_count, `${summary.commit_next} committed for next sprint`)}
        ${metric("Inbound items", summary.inbound_items, "bugs, CS asks, partner asks, and scope additions")}
        ${metric("Open incidents", summary.open_incidents, "ranked by severity, restore time, and recurrence risk")}
        ${metric("Events with gaps", summary.events_with_gaps, `${percent(summary.avg_instrumentation_coverage)} average coverage`)}
      </section>

      <nav class="tabs" aria-label="Artifact surfaces">
        ${tabs.map(([id, label]) => `<button type="button" class="${state.tab === id ? "active" : ""}" data-tab="${id}">${label}</button>`).join("")}
      </nav>

      ${content}
    </main>
  `;
  bindEvents();
}

function renderCommand() {
  const topRows = state.payload.roadmapQueue.slice(0, 3);
  const incidentMax = Math.max(...Object.values(state.payload.summary.incident_counts));
  const inboundMax = Math.max(...Object.values(state.payload.summary.inbound_counts));
  shell(`
    <section class="surface-grid two">
      <article class="panel">
        <div class="panel-head">
          <span class="eyebrow">Roadmap sequencing</span>
          <h2>Next-highest-value work</h2>
        </div>
        <div class="priority-list">
          ${topRows.map((row) => `
            <button class="priority-card" type="button" data-workflow="${row.workflow_id}">
              <span>${row.product_area}</span>
              <strong>${row.workflow}</strong>
              <em>${row.decision}</em>
              <b class="${scoreClass(row.priority_score)}">${row.priority_score}</b>
            </button>
          `).join("")}
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <span class="eyebrow">Operating pressure</span>
          <h2>What is pulling on the team</h2>
        </div>
        <div class="bar-stack">
          ${Object.entries(state.payload.summary.inbound_counts).map(([label, value]) => bar(value, inboundMax, label)).join("")}
        </div>
        <div class="bar-stack compact">
          ${Object.entries(state.payload.summary.incident_counts).map(([label, value]) => bar(value, incidentMax, label)).join("")}
        </div>
      </article>
    </section>

    <section class="surface-grid three">
      ${state.payload.feedbackSignals.slice(0, 3).map((signal) => `
        <article class="signal-card">
          <span>${signal.source}</span>
          <strong>${signal.theme}</strong>
          <p>${signal.user_need}</p>
          <dl>
            <div><dt>Volume</dt><dd>${signal.volume}</dd></div>
            <div><dt>Severity</dt><dd>${signal.severity}</dd></div>
            <div><dt>Confidence</dt><dd>${percent(signal.confidence)}</dd></div>
          </dl>
        </article>
      `).join("")}
    </section>
  `);
}

function renderRoadmap() {
  const selected = activeWorkflow();
  const brief = state.payload.briefs.find((row) => row.workflow_id === selected.workflow_id);
  shell(`
    <section class="surface-grid roadmap-grid">
      <article class="panel table-panel">
        <div class="panel-head split">
          <div>
            <span class="eyebrow">Prioritized backlog</span>
            <h2>Roadmap queue</h2>
          </div>
          <p>${state.payload.roadmapQueue.length} candidates scored from customer signal, usage, incidents, effort, data readiness, and clinical sensitivity.</p>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Workflow</th>
                <th>Decision</th>
                <th>Score</th>
                <th>Access impact</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              ${state.payload.roadmapQueue.map((row) => `
                <tr class="${row.workflow_id === selected.workflow_id ? "selected" : ""}">
                  <td><button type="button" class="link-button" data-workflow="${row.workflow_id}">${row.workflow}</button><span>${row.product_area}</span></td>
                  <td>${pill(row.decision)}</td>
                  <td><b class="${scoreClass(row.priority_score)}">${row.priority_score}</b></td>
                  <td>${money(row.estimated_access_impact)}</td>
                  <td>${row.owner_team}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </article>

      <aside class="panel detail-panel">
        <div class="panel-head">
          <span class="eyebrow">Project overview</span>
          <h2>${selected.workflow}</h2>
        </div>
        <p>${brief.project_overview}</p>
        <dl class="detail-list">
          <div><dt>Success metric</dt><dd>${brief.success_metric}</dd></div>
          <div><dt>Acceptance criteria</dt><dd>${brief.acceptance_criteria}</dd></div>
          <div><dt>Non-goal</dt><dd>${brief.non_goal}</dd></div>
          <div><dt>Engineering note</dt><dd>${brief.engineering_note}</dd></div>
        </dl>
      </aside>
    </section>
  `);
}

function renderTriage() {
  shell(`
    <section class="surface-grid triage-grid">
      <article class="panel table-panel">
        <div class="panel-head split">
          <div>
            <span class="eyebrow">Inbound triage</span>
            <h2>Protect engineering focus</h2>
          </div>
          <p>Each item gets a decision, owner, and follow-up path.</p>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Users</th>
                <th>Decision</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              ${state.payload.inboundQueue.map((row) => `
                <tr>
                  <td><strong>${row.item_id}</strong><span>${row.root_cause}</span></td>
                  <td>${row.item_type}</td>
                  <td>${pill(row.severity)}</td>
                  <td>${numberFmt.format(num(row.users_impacted))}</td>
                  <td>${row.decision}<span>${row.follow_up}</span></td>
                  <td>${row.owner}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  `);
}

function renderIncidents() {
  shell(`
    <section class="surface-grid two">
      <article class="panel table-panel">
        <div class="panel-head">
          <span class="eyebrow">Incident loop</span>
          <h2>Root cause, fix, follow-up</h2>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Incident</th>
                <th>Severity</th>
                <th>Impact</th>
                <th>RCA</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${state.payload.incidents.map((row) => `
                <tr>
                  <td><strong>${row.incident_type}</strong><span>${row.summary}</span></td>
                  <td>${pill(row.severity)}</td>
                  <td>${numberFmt.format(num(row.patients_impacted))} patients<span>${row.hours_to_restore}h restore</span></td>
                  <td>${row.root_cause}<span>Risk ${row.recurrence_risk}</span></td>
                  <td>${row.status}<span>${row.followup_owner}</span></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <span class="eyebrow">Highest follow-up</span>
          <h2>${state.payload.incidents[0].incident_type}</h2>
        </div>
        <dl class="detail-list">
          <div><dt>Detected by</dt><dd>${state.payload.incidents[0].detection_source}</dd></div>
          <div><dt>Ack time</dt><dd>${state.payload.incidents[0].minutes_to_ack} minutes</dd></div>
          <div><dt>Follow-up score</dt><dd>${state.payload.incidents[0].followup_score}</dd></div>
          <div><dt>Owner</dt><dd>${state.payload.incidents[0].followup_owner}</dd></div>
        </dl>
      </article>
    </section>
  `);
}

function renderData() {
  shell(`
    <section class="surface-grid two">
      <article class="panel table-panel">
        <div class="panel-head">
          <span class="eyebrow">Mixpanel event contracts</span>
          <h2>Instrumentation gaps</h2>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Event</th>
                <th>Status</th>
                <th>Question</th>
                <th>Health</th>
                <th>Owner</th>
              </tr>
            </thead>
            <tbody>
              ${state.payload.instrumentation.slice(0, 18).map((row) => `
                <tr>
                  <td><strong>${row.event_name}</strong><span>${row.required_properties}</span></td>
                  <td>${pill(row.mixpanel_status)}</td>
                  <td>${row.product_question}</td>
                  <td>${row.property_health}<span>Gap ${row.gap_score}</span></td>
                  <td>${row.owner}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </article>

      <article class="panel table-panel">
        <div class="panel-head">
          <span class="eyebrow">EHR readiness</span>
          <h2>FHIR and HL7 contracts</h2>
        </div>
        <div class="contract-list">
          ${state.payload.ehrReadiness.map((row) => `
            <article class="contract-card">
              <span>${row.endpoint}</span>
              <strong>${row.workflow}</strong>
              <p>${row.top_failure_mode}</p>
              <dl>
                <div><dt>Mapping</dt><dd>${row.mapping_completeness}</dd></div>
                <div><dt>Failure</dt><dd>${percent(row.failure_rate)}</dd></div>
                <div><dt>Ready</dt><dd>${row.readiness_score}</dd></div>
              </dl>
            </article>
          `).join("")}
        </div>
      </article>
    </section>
  `);
}

function renderCadence() {
  shell(`
    <section class="surface-grid cadence-grid">
      ${state.payload.ceremonies.slice(-10).map((row) => `
        <article class="ceremony-card">
          <span>${row.week}</span>
          <strong>${row.ceremony}</strong>
          <p>${row.purpose}</p>
          <dl>
            <div><dt>Open</dt><dd>${row.open_actions}</dd></div>
            <div><dt>Overdue</dt><dd>${row.overdue_actions}</dd></div>
            <div><dt>Alignment</dt><dd>${row.alignment_score}</dd></div>
          </dl>
          <em>${row.next_artifact}</em>
        </article>
      `).join("")}
    </section>
  `);
}

function render() {
  if (state.tab === "roadmap") renderRoadmap();
  else if (state.tab === "triage") renderTriage();
  else if (state.tab === "incidents") renderIncidents();
  else if (state.tab === "data") renderData();
  else if (state.tab === "cadence") renderCadence();
  else renderCommand();
}

function bindEvents() {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      state.tab = button.dataset.tab;
      render();
    });
  });
  document.querySelectorAll("[data-workflow]").forEach((button) => {
    button.addEventListener("click", () => {
      state.workflowId = button.dataset.workflow;
      state.tab = "roadmap";
      render();
    });
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  state.workflowId = state.payload.roadmapQueue[0].workflow_id;
  render();
}

init().catch((error) => {
  app.innerHTML = `
    <main class="loading-shell">
      <p>Unable to load generated artifact data.</p>
      <pre>${error.message}</pre>
    </main>
  `;
});
