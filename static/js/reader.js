(function () {
  "use strict";

  var PAGE_SIZE = 50;
  var articles = [];
  var filtered = [];
  var currentPage = 1;
  var sortField = "date";
  var sortDir = -1; // -1 = descending

  var elList = document.getElementById("article-list");
  var elStatus = document.getElementById("reader-status");
  var elPagination = document.getElementById("reader-pagination");
  var elSource = document.getElementById("filter-source");
  var elTopic = document.getElementById("filter-topic");
  var elSearch = document.getElementById("filter-search");
  var elSortBtns = document.querySelectorAll("#reader-sort button");

  var axiomLabels = {
    attention_economy: "Attention Economy",
    data_sovereignty: "Data Sovereignty",
    power_consolidation: "Power Consolidation",
    coercion_cooperation: "Coercion vs. Cooperation",
    fear_trust: "Fear vs. Trust",
    democratization: "Democratization",
    systemic_design: "Systemic Design"
  };

  var topicLabels = {
    platform_dynamics: "Platform Dynamics",
    ai_capabilities: "AI Capabilities",
    consolidation: "Consolidation",
    content_moderation: "Content Moderation",
    surveillance: "Surveillance",
    startup_funding: "Startup Funding",
    labor_displacement: "Labor Displacement",
    privacy: "Privacy",
    hardware: "Hardware",
    cybersecurity: "Cybersecurity",
    other: "Other",
    infrastructure: "Infrastructure",
    crypto: "Crypto",
    ai_regulation: "AI Regulation",
    open_source: "Open Source",
    acquisitions: "Acquisitions"
  };

  function formatTopicLabel(topic) {
    return topicLabels[topic] || topic.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function init() {
    fetch("/data/articles.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        articles = data.articles || [];
        populateFilters();
        readURL();
        applyFilters();
      })
      .catch(function () {
        elList.innerHTML = '<li class="muted">Failed to load articles.</li>';
      });

    elSource.addEventListener("change", onFilter);
    elTopic.addEventListener("change", onFilter);
    elSearch.addEventListener("input", debounce(onFilter, 200));

    for (var i = 0; i < elSortBtns.length; i++) {
      elSortBtns[i].addEventListener("click", onSort);
    }
  }

  function populateFilters() {
    var sources = {};
    var topics = {};
    for (var i = 0; i < articles.length; i++) {
      var a = articles[i];
      if (a.source) sources[a.source] = true;
      if (a.topics) {
        for (var j = 0; j < a.topics.length; j++) {
          topics[a.topics[j]] = true;
        }
      }
    }

    var sortedSources = Object.keys(sources).sort();
    for (var i = 0; i < sortedSources.length; i++) {
      var opt = document.createElement("option");
      opt.value = sortedSources[i];
      opt.textContent = sortedSources[i];
      elSource.appendChild(opt);
    }

    var sortedTopics = Object.keys(topics).sort();
    var topicLabel = document.getElementById("topic-filter-label");
    if (sortedTopics.length <= 1 && topicLabel) {
      topicLabel.classList.add("hidden");
    } else {
      for (var i = 0; i < sortedTopics.length; i++) {
        var opt = document.createElement("option");
        opt.value = sortedTopics[i];
        opt.textContent = formatTopicLabel(sortedTopics[i]);
        elTopic.appendChild(opt);
      }
    }
  }

  function onFilter() {
    currentPage = 1;
    applyFilters();
    pushURL();
  }

  function onSort(e) {
    var btn = e.currentTarget;
    var field = btn.getAttribute("data-sort");

    if (field === sortField) {
      sortDir *= -1;
    } else {
      sortField = field;
      sortDir = -1;
    }

    for (var i = 0; i < elSortBtns.length; i++) {
      elSortBtns[i].classList.remove("active");
      elSortBtns[i].textContent = elSortBtns[i].getAttribute("data-sort") === "score" ? "Score" : "Date";
    }
    btn.classList.add("active");
    btn.textContent = (field === "score" ? "Score" : "Date") + (sortDir === -1 ? " ↓" : " ↑");

    currentPage = 1;
    applyFilters();
    pushURL();
  }

  function applyFilters() {
    var src = elSource.value;
    var topic = elTopic.value;
    var search = elSearch.value.toLowerCase();

    filtered = articles.filter(function (a) {
      if (src && a.source !== src) return false;
      if (topic && (!a.topics || a.topics.indexOf(topic) === -1)) return false;
      if (search && a.title.toLowerCase().indexOf(search) === -1) return false;
      return true;
    });

    filtered.sort(function (a, b) {
      var va, vb;
      if (sortField === "score") {
        va = a.overall_score || 0;
        vb = b.overall_score || 0;
      } else {
        va = a.published || "";
        vb = b.published || "";
      }
      if (va < vb) return sortDir;
      if (va > vb) return -sortDir;
      return 0;
    });

    render();
  }

  function render() {
    var total = filtered.length;
    var totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (currentPage > totalPages) currentPage = totalPages;

    var start = (currentPage - 1) * PAGE_SIZE;
    var end = Math.min(start + PAGE_SIZE, total);
    var page = filtered.slice(start, end);

    elStatus.textContent = total + " article" + (total !== 1 ? "s" : "") +
      (total !== articles.length ? " (filtered from " + articles.length + ")" : "") +
      " · Page " + currentPage + " of " + totalPages;

    if (page.length === 0) {
      elList.innerHTML = '<li class="muted">No articles match your filters.</li>';
      elPagination.innerHTML = "";
      return;
    }

    var html = "";
    for (var i = 0; i < page.length; i++) {
      html += renderArticle(page[i]);
    }
    elList.innerHTML = html;

    // Attach expand handlers
    var items = elList.querySelectorAll(".article-item");
    for (var i = 0; i < items.length; i++) {
      (function (item) {
        var titleEl = item.querySelector(".article-title");
        titleEl.style.cursor = "pointer";
        titleEl.addEventListener("click", function (e) {
          e.preventDefault();
          var detail = item.querySelector(".article-detail");
          if (detail) detail.classList.toggle("open");
        });
      })(items[i]);
    }

    renderPagination(totalPages);
  }

  function renderArticle(a) {
    var bars = "";
    if (a.axiom_scores) {
      var keys = ["attention_economy", "data_sovereignty", "power_consolidation",
        "coercion_cooperation", "fear_trust", "democratization", "systemic_design"];
      bars = '<span class="axiom-bars">';
      for (var i = 0; i < keys.length; i++) {
        var v = a.axiom_scores[keys[i]] || 0;
        var h = Math.max(2, (v / 3) * 16);
        bars += '<span class="axiom-bar" style="height:' + h + 'px" title="' +
          axiomLabels[keys[i]] + ': ' + v + '/3"></span>';
      }
      bars += "</span>";
    }

    var summary = "";
    if (a.summary) {
      summary = '<p class="article-summary">' + escapeHtml(a.summary) + "</p>";
    }

    var tags = "";
    if (a.topics && a.topics.length > 0) {
      tags = '<div class="article-tags">';
      for (var i = 0; i < a.topics.length; i++) {
        tags += '<span class="thread-tag">' + escapeHtml(formatTopicLabel(a.topics[i])) + '</span>';
      }
      tags += '</div>';
    }

    var detail = '<div class="article-detail">';
    if (a.axiom_scores) {
      var keys = ["attention_economy", "data_sovereignty", "power_consolidation",
        "coercion_cooperation", "fear_trust", "democratization", "systemic_design"];
      for (var i = 0; i < keys.length; i++) {
        var v = a.axiom_scores[keys[i]] || 0;
        detail += '<div class="axiom-row"><span class="axiom-label">' +
          axiomLabels[keys[i]] + '</span><span class="axiom-value">' + v + '/3</span></div>';
      }
    }
    detail += "</div>";

    return '<li class="article-item">' +
      '<div class="article-title"><a href="#">' + escapeHtml(a.title) + "</a></div>" +
      '<div class="article-meta">' +
      '<span class="article-score">Score: ' + (a.overall_score || 0) + "</span>" +
      bars +
      '<a class="article-source" href="' + escapeHtml(a.url) +
        '" rel="noopener" target="_blank">' + escapeHtml(a.source || "") + "</a>" +
      "<span>" + (a.published || "") + "</span>" +
      "</div>" +
      tags +
      summary +
      detail +
      "</li>";
  }

  function renderPagination(totalPages) {
    if (totalPages <= 1) {
      elPagination.innerHTML = "";
      return;
    }

    var html = "";
    html += '<button ' + (currentPage <= 1 ? "disabled" : "") +
      ' data-page="' + (currentPage - 1) + '">← Prev</button>';

    var start = Math.max(1, currentPage - 3);
    var end = Math.min(totalPages, currentPage + 3);

    if (start > 1) {
      html += '<button data-page="1">1</button>';
      if (start > 2) html += '<button disabled>…</button>';
    }

    for (var p = start; p <= end; p++) {
      html += '<button data-page="' + p + '"' +
        (p === currentPage ? ' class="active"' : "") + ">" + p + "</button>";
    }

    if (end < totalPages) {
      if (end < totalPages - 1) html += '<button disabled>…</button>';
      html += '<button data-page="' + totalPages + '">' + totalPages + "</button>";
    }

    html += '<button ' + (currentPage >= totalPages ? "disabled" : "") +
      ' data-page="' + (currentPage + 1) + '">Next →</button>';

    elPagination.innerHTML = html;

    var btns = elPagination.querySelectorAll("button[data-page]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener("click", function (e) {
        var p = parseInt(e.currentTarget.getAttribute("data-page"));
        if (p >= 1 && p !== currentPage) {
          currentPage = p;
          render();
          pushURL();
          window.scrollTo(0, 0);
        }
      });
    }
  }

  function pushURL() {
    var params = new URLSearchParams();
    if (elSource.value) params.set("source", elSource.value);
    if (elTopic.value) params.set("topic", elTopic.value);
    if (elSearch.value) params.set("q", elSearch.value);
    if (sortField !== "date") params.set("sort", sortField);
    if (sortDir !== -1) params.set("dir", "asc");
    if (currentPage > 1) params.set("page", currentPage);
    var qs = params.toString();
    history.replaceState(null, "", qs ? "?" + qs : window.location.pathname);
  }

  function readURL() {
    var params = new URLSearchParams(window.location.search);
    if (params.get("source")) elSource.value = params.get("source");
    if (params.get("topic")) elTopic.value = params.get("topic");
    if (params.get("q")) elSearch.value = params.get("q");
    if (params.get("sort")) sortField = params.get("sort");
    if (params.get("dir") === "asc") sortDir = 1;
    if (params.get("page")) currentPage = parseInt(params.get("page")) || 1;

    // Update sort button UI
    for (var i = 0; i < elSortBtns.length; i++) {
      var btn = elSortBtns[i];
      var field = btn.getAttribute("data-sort");
      btn.classList.toggle("active", field === sortField);
      if (field === sortField) {
        btn.textContent = (field === "score" ? "Score" : "Date") + (sortDir === -1 ? " ↓" : " ↑");
      }
    }
  }

  function escapeHtml(s) {
    if (!s) return "";
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function debounce(fn, ms) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, ms);
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
