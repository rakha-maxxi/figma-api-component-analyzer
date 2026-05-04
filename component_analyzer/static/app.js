const state = {
  analyses: [],
  currentAnalysis: null,
  candidateFilter: "promotion",
  currentView: "overview",
  findingsFocus: "all",
};

const metricsGrid = document.getElementById("metrics-grid");
const historyList = document.getElementById("history-list");
const emptyState = document.getElementById("empty-state");
const analysisView = document.getElementById("analysis-view");
const metaTitle = document.getElementById("meta-title");
const metaSubtitle = document.getElementById("meta-subtitle");
const recommendationStrip = document.getElementById("recommendation-strip");
const componentSourceList = document.getElementById("component-source-list");
const largeComponents = document.getElementById("large-components");
const candidateList = document.getElementById("candidate-list");
const actionFeed = document.getElementById("action-feed");
const dialog = document.getElementById("analyze-dialog");
const form = document.getElementById("analyze-form");
const formStatus = document.getElementById("form-status");
const submitAnalysis = document.getElementById("submit-analysis");
const openAnalyze = document.getElementById("open-analyze");
const emptyAnalyze = document.getElementById("empty-analyze");
const loadDemo = document.getElementById("load-demo");
const refreshHistory = document.getElementById("refresh-history");
const reloadCurrent = document.getElementById("reload-current");
const findingsFocusSelect = document.getElementById("findings-focus");

openAnalyze.addEventListener("click", () => dialog.showModal());
emptyAnalyze.addEventListener("click", () => dialog.showModal());
document.getElementById("close-dialog").addEventListener("click", () => dialog.close());
document.getElementById("cancel-dialog").addEventListener("click", () => dialog.close());
refreshHistory.addEventListener("click", loadAnalyses);
reloadCurrent.addEventListener("click", () => {
  if (state.currentAnalysis) {
    loadAnalysis(state.currentAnalysis.id);
  }
});
findingsFocusSelect.addEventListener("change", () => {
  state.findingsFocus = findingsFocusSelect.value;
  renderRecommendationStrip();
  renderLargeComponents();
  renderCandidates();
  renderActionFeed();
});
loadDemo.addEventListener("click", () => analyze({
  file_key: "demo",
  project_name: "FS+",
  platform: "Mobile",
}));

document.querySelectorAll("[data-candidate-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    state.candidateFilter = button.dataset.candidateFilter;
    document.querySelectorAll("[data-candidate-filter]").forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    renderCandidates();
  });
});

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    setView(button.dataset.view);
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  analyze(payload, true);
});

loadAnalyses();

async function loadAnalyses() {
  const response = await fetch("/api/analyses");
  const payload = await response.json();
  state.analyses = payload.items || [];
  renderHistory();
  if (!state.currentAnalysis && state.analyses.length) {
    loadAnalysis(state.analyses[0].id);
  }
}

async function loadAnalysis(id) {
  const response = await fetch(`/api/analyses/${id}`);
  if (!response.ok) return;
  state.currentAnalysis = await response.json();
  renderAnalysis();
}

async function analyze(payload, closeDialog = false) {
  setBusy(true, "Analyzing file...");
  formStatus.className = "form-status";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      formStatus.textContent = result.error || "Analysis failed.";
      formStatus.className = "form-status error";
      return;
    }

    state.currentAnalysis = result;
    formStatus.textContent = "Analysis completed.";
    formStatus.className = "form-status success";
    if (closeDialog) {
      setTimeout(() => {
        dialog.close();
        form.reset();
        formStatus.textContent = "";
      }, 250);
    }
    await loadAnalyses();
    renderAnalysis();
  } catch (error) {
    formStatus.textContent = error.message || "Analysis failed.";
    formStatus.className = "form-status error";
  } finally {
    setBusy(false);
  }
}

function renderHistory() {
  historyList.innerHTML = "";
  if (!state.analyses.length) {
    historyList.innerHTML = '<p class="field-help">No analyses saved yet.</p>';
    return;
  }

  state.analyses.forEach((item) => {
    const button = document.createElement("button");
    button.className = "history-item";
    if (state.currentAnalysis?.id === item.id) {
      button.classList.add("is-active");
    }
    button.innerHTML = `
      <strong>${escapeHtml(item.file_name)}</strong>
      <p>${escapeHtml(item.project_name)} • ${escapeHtml(item.platform)}</p>
      <p>Usage ${(item.summary.component_usage_rate * 100).toFixed(0)}% • ${item.summary.refactor_candidate_count} refactor candidates</p>
    `;
    button.addEventListener("click", () => loadAnalysis(item.id));
    historyList.appendChild(button);
  });
}

function renderAnalysis() {
  const analysis = state.currentAnalysis;
  if (!analysis) return;

  emptyState.classList.add("is-hidden");
  analysisView.classList.remove("is-hidden");

  metaTitle.textContent = analysis.meta.file_name;
  const subtitleParts = [
    analysis.meta.project_name,
    analysis.meta.platform,
    `Analyzed ${formatDate(analysis.meta.analyzed_at)}`,
    `Source: ${analysis.meta.source}`,
  ];
  if (analysis.meta.reference_file_name) {
    subtitleParts.push(`Reference: ${analysis.meta.reference_file_name}`);
  }
  metaSubtitle.textContent = subtitleParts.join(" • ");

  renderMetrics();
  renderRecommendationStrip();
  renderComponentSources();
  renderLargeComponents();
  renderCandidates();
  renderActionFeed();
  setView(state.currentView);
}

function renderMetrics() {
  const summary = state.currentAnalysis.summary;
  const metrics = [
    {
      title: "Component Adoption",
      value: `${Math.round(summary.component_usage_rate * 100)}%`,
      foot: `${summary.instance_count} instances across ${summary.native_candidate_count} reusable-looking native structures`,
      tone: summary.component_usage_rate >= 0.7 ? "good" : summary.component_usage_rate >= 0.4 ? "watch" : "risk",
    },
    {
      title: "Master / Library Instances",
      value: `${summary.remote_instance_count + (summary.remote_or_published_instance_count || 0)}`,
      foot: `${summary.local_instance_count || 0} local, ${summary.remote_instance_count || 0} remote, ${summary.unknown_instance_count || 0} unknown source`,
      tone: "info",
    },
    {
      title: "Large Components",
      value: `${summary.large_component_count}`,
      foot: `${summary.section_like_component_count} section-like reusable blocks need decomposition review`,
      tone: summary.large_component_count > 0 ? "risk" : "good",
    },
    {
      title: "Repeated Native Clusters",
      value: `${summary.repeated_native_cluster_count}`,
      foot: `${summary.duplication_burden} duplicated occurrences beyond the first copy`,
      tone: summary.repeated_native_cluster_count > 8 ? "risk" : summary.repeated_native_cluster_count > 0 ? "watch" : "good",
    },
    {
      title: "Refactor Candidates",
      value: `${summary.refactor_candidate_count}`,
      foot: `${summary.promotion_candidate_count} promotion-ready patterns and ${summary.existing_component_not_reused_count || 0} known components rebuilt natively`,
      tone: summary.refactor_candidate_count > 0 ? "watch" : "good",
    },
  ];

  metricsGrid.innerHTML = metrics.map((metric) => `
    <article class="metric-card" data-tone="${escapeHtml(metric.tone)}">
      <h3>${escapeHtml(metric.title)}</h3>
      <div class="metric-value">${escapeHtml(metric.value)}</div>
      <div class="metric-foot">${escapeHtml(metric.foot)}</div>
    </article>
  `).join("");
}

function renderRecommendationStrip() {
  recommendationStrip.innerHTML = "";
  const focus = state.findingsFocus;
  const allRecs = state.currentAnalysis.recommendations;
  const items = allRecs.filter(item => matchesFindingsFocus(item, focus, "recommendation")).slice(0, 4);
  recommendationStrip.classList.toggle("is-empty", !items.length);
  if (!items.length) {
    const msg = focus !== "all" ? "No recommendations match the selected focus." : "No urgent recommendations in this analysis.";
    recommendationStrip.innerHTML = `<p class="field-help">${msg}</p>`;
    return;
  }
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "rec-card";
    article.dataset.priority = item.priority;
    const display = displayTitle(item.layer_path, item.title);
    article.innerHTML = `
      <h3>${escapeHtml(display.title)}</h3>
      ${display.subtitle ? `<p>${escapeHtml(display.subtitle)}</p>` : ""}
      <p>${escapeHtml(item.recommendation)}</p>
      <div class="meta-row">
        <span class="pill ${pillTone(item.priority)}">${escapeHtml(item.priority)} priority</span>
        <span class="pill">${escapeHtml(item.type.replaceAll("_", " "))}</span>
        ${item.page_name ? `<span class="pill">${escapeHtml(item.page_name)}</span>` : ""}
      </div>
    `;
    recommendationStrip.appendChild(article);
  });
}

function renderComponentSources() {
  const items = state.currentAnalysis.component_sources || [];
  componentSourceList.innerHTML = items.length ? "" : '<p class="field-help">No component instances found in this analysis.</p>';
  items.slice(0, 10).forEach((item) => {
    const article = document.createElement("article");
    article.className = "stack-card compact-card";
    article.innerHTML = `
      <h3>${escapeHtml(item.component_name)}</h3>
      <p>${escapeHtml(item.source_label || "Unknown source")}</p>
      <div class="meta-row">
        <span class="pill green">${item.occurrence_count} instances</span>
        <span class="pill ${sourceTone(item.component_source_type)}">${escapeHtml(item.component_source_type.replaceAll("_", " "))}</span>
        ${item.source_file_key ? `<span class="pill">${escapeHtml(item.source_file_key)}</span>` : ""}
      </div>
      ${item.sample_nodes?.[0]?.layer_path ? `<p><strong>Sample:</strong> ${escapeHtml(item.sample_nodes[0].layer_path)}</p>` : ""}
    `;
    componentSourceList.appendChild(article);
  });
}

function renderLargeComponents() {
  const focus = state.findingsFocus;
  const items = state.currentAnalysis.large_components.filter(item => matchesFindingsFocus(item, focus, "large"));
  const emptyMsg = focus !== "all" ? "No large components match the selected focus." : "No oversized components detected in this analysis.";
  largeComponents.innerHTML = items.length ? "" : `<p class="field-help">${emptyMsg}</p>`;
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "stack-card";
    const display = displayTitle(item.layer_path, item.node_name);
    const complexity = item.complexity_breakdown || {};
    const complexityDetail = [
      `children ${complexity.children_score ?? 0}`,
      `text ${complexity.text_score ?? 0}`,
      `regions ${complexity.region_score ?? 0}`,
      `depth ${complexity.depth_score ?? 0}`,
      `width ${complexity.width_bonus ?? 0}`,
      `height ${complexity.height_bonus ?? 0}`,
    ].join(" + ");
    article.innerHTML = `
      <h3>${escapeHtml(display.title)}</h3>
      ${display.subtitle ? `<p>${escapeHtml(display.subtitle)}</p>` : ""}
      <p>${escapeHtml(item.recommendation)}</p>
      <div class="meta-row">
        <span class="pill red">${escapeHtml(item.classification.replaceAll("_", " "))}</span>
        <span class="pill">complexity ${item.complexity_score}</span>
        <span class="pill">${item.child_count} children</span>
        <span class="pill">${item.semantic_regions} regions</span>
        ${item.page_name ? `<span class="pill">${escapeHtml(item.page_name)}</span>` : ""}
      </div>
      <p><strong>Complexity formula:</strong> ${escapeHtml(complexityDetail)}</p>
      <p>${escapeHtml(item.reason)}</p>
    `;
    largeComponents.appendChild(article);
  });
}

function renderCandidates() {
  const analysis = state.currentAnalysis;
  if (!analysis) return;
  const focus = state.findingsFocus;
  let items = [];
  if (state.candidateFilter === "promotion") items = analysis.promotion_candidates;
  if (state.candidateFilter === "existing") items = analysis.existing_component_not_reused || [];
  if (state.candidateFilter === "raw") items = analysis.raw_duplicates;
  if (state.candidateFilter === "low") items = analysis.low_value_repetition;

  items = items.filter(item => matchesFindingsFocus(item, focus, "candidate"));
  const emptyMsg = focus !== "all" ? "No items match the selected focus." : "No items in this bucket.";
  candidateList.innerHTML = items.length ? "" : `<p class="field-help">${emptyMsg}</p>`;
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "stack-card";
    const samplePath = item.sample_nodes?.[0]?.layer_path || "";
    const display = displayTitle(samplePath, item.semantic_name);
    article.innerHTML = `
      <h3>${escapeHtml(display.title)}</h3>
      ${display.subtitle ? `<p>${escapeHtml(display.subtitle)}</p>` : ""}
      <p>${escapeHtml(item.recommendation)}</p>
      <div class="meta-row">
        <span class="pill green">${item.occurrence_count} occurrences</span>
        <span class="pill blue">${escapeHtml(item.level)}</span>
        <span class="pill ${pillTone(item.confidence)}">${escapeHtml(item.confidence)} confidence</span>
        <span class="pill">score ${item.promotion_score}</span>
        ${item.reference_match?.component_name ? `<span class="pill amber">matches ${escapeHtml(item.reference_match.component_name)}</span>` : ""}
        ${item.reference_match?.match_type ? `<span class="pill">${escapeHtml(item.reference_match.match_type)} match</span>` : ""}
        ${item.reference_match?.component_source_type ? `<span class="pill ${sourceTone(item.reference_match.component_source_type)}">${escapeHtml(item.reference_match.component_source_type.replaceAll("_", " "))}</span>` : ""}
        ${item.sample_nodes?.[0]?.page_name ? `<span class="pill">${escapeHtml(item.sample_nodes[0].page_name)}</span>` : ""}
      </div>
      ${item.reference_match?.source_label ? `<p><strong>Known source:</strong> ${escapeHtml(item.reference_match.source_label)}</p>` : ""}
      ${item.reference_match?.layer_path ? `<p><strong>Reference path:</strong> ${escapeHtml(item.reference_match.layer_path)}</p>` : ""}
      <p>${escapeHtml(item.reason)}</p>
    `;
    candidateList.appendChild(article);
  });
}

function renderActionFeed() {
  actionFeed.innerHTML = "";
  const focus = state.findingsFocus;
  const items = state.currentAnalysis.recommendations.filter(item => matchesFindingsFocus(item, focus, "recommendation"));
  if (!items.length) {
    actionFeed.innerHTML = focus !== "all"
      ? '<p class="field-help">No action items match the selected focus.</p>'
      : '<p class="field-help">No action items in this analysis.</p>';
    return;
  }
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "stack-card";
    const display = displayTitle(item.layer_path, item.title);
    article.innerHTML = `
      <h3>${escapeHtml(display.title)}</h3>
      ${display.subtitle ? `<p>${escapeHtml(display.subtitle)}</p>` : ""}
      <p>${escapeHtml(item.recommendation)}</p>
      <div class="meta-row">
        <span class="pill ${pillTone(item.priority)}">${escapeHtml(item.priority)} priority</span>
        ${item.page_name ? `<span class="pill">${escapeHtml(item.page_name)}</span>` : ""}
      </div>
      <p>${escapeHtml(item.reason)}</p>
    `;
    actionFeed.appendChild(article);
  });
}

function pillTone(kind) {
  if (kind === "high") return "red";
  if (kind === "medium") return "amber";
  if (kind === "low") return "blue";
  return "green";
}

function sourceTone(kind) {
  if (kind === "remote_library_instance" || kind === "remote_or_published_instance") return "blue";
  if (kind === "local_file_instance") return "green";
  return "amber";
}

function displayTitle(layerPath, fallback) {
  if (layerPath) {
    const parts = String(layerPath).split(" / ");
    const shortName = fallback && !String(layerPath).endsWith(String(fallback)) ? fallback : "";
    return {
      title: layerPath,
      subtitle: shortName || parts[parts.length - 1] || "",
    };
  }
  return {
    title: fallback || "Untitled layer",
    subtitle: "",
  };
}

function formatDate(value) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setView(view) {
  state.currentView = view;

  document.querySelectorAll("[data-view]").forEach((item) => {
    const isActive = item.dataset.view === view;
    item.classList.toggle("is-active", isActive);
    item.setAttribute("aria-selected", String(isActive));
  });

  document.querySelectorAll("[data-panel]").forEach((panel) => {
    const isActive = panel.dataset.panel === view;
    panel.classList.toggle("panel-hidden", !isActive);
    panel.setAttribute("aria-hidden", String(!isActive));
  });
}

function setBusy(isBusy, message = "") {
  document.body.classList.toggle("is-busy", isBusy);
  submitAnalysis.disabled = isBusy;
  openAnalyze.disabled = isBusy;
  emptyAnalyze.disabled = isBusy;
  loadDemo.disabled = isBusy;
  refreshHistory.disabled = isBusy;
  reloadCurrent.disabled = isBusy;
  submitAnalysis.textContent = isBusy ? "Analyzing..." : "Start Analysis";
  if (message) {
    formStatus.textContent = message;
  }
}

function matchesFindingsFocus(item, focusValue, context) {
  if (focusValue === "all") return true;

  const name = (item.semantic_name || item.node_name || item.title || "").toLowerCase();
  const level = (item.level || "").toLowerCase();
  const classification = (item.classification || "").toLowerCase();
  const type = (item.type || item.recommendation_type || "").toLowerCase();

  switch (focusValue) {
    case "text_pairing":
      return /metric|pair|label|list\s*item|entity\s*summary|key.?value/i.test(name) ||
             (level === "atomic" && /metric|text|label|value/i.test(name));
    case "component_candidates":
      if (context === "large") return classification.includes("section");
      return true;
    case "scaffold_shell":
      return level === "scaffold" || level === "pattern" ||
             /shell|section\s*(header|shell)|dialog|scaffold|card\s*shell/i.test(name);
    case "large_components":
      if (context === "large") return true;
      if (context === "recommendation") {
        return type.includes("decompose") || type.includes("downgrade") ||
               type.includes("split") || type.includes("review_component");
      }
      return false;
    case "existing_not_reused":
      if (context === "large") return false;
      return !!item.reference_match || type === "existing_component_not_reused";
    case "repeated_patterns":
      if (context === "large") return false;
      return (item.occurrence_count || 0) >= 2;
    default:
      return true;
  }
}
