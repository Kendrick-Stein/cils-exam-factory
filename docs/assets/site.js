/* CILS Exam Factory — interazioni leggere, senza dipendenze.
   Tutto è progressive enhancement: la pagina funziona anche senza JS. */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;

  /* ---------- Topbar: restringi allo scroll ---------- */

  var topbar = document.querySelector(".topbar");
  if (topbar) {
    var scrollTick = false;
    var onScroll = function () {
      if (scrollTick) return;
      scrollTick = true;
      window.requestAnimationFrame(function () {
        topbar.classList.toggle("scrolled", window.scrollY > 24);
        scrollTick = false;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Menu mobile ---------- */

  var navToggle = document.querySelector(".nav-toggle");
  var topnav = document.getElementById("topnav");
  if (navToggle && topnav && topbar) {
    var closeNav = function () {
      topbar.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    };
    navToggle.addEventListener("click", function () {
      var open = topbar.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    topnav.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeNav();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeNav();
    });
  }

  /* ---------- Reveal all'ingresso nel viewport ---------- */

  var reveals = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  if (reducedMotion || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ---------- Statistiche: conteggio una sola volta ---------- */

  var counters = Array.prototype.slice.call(document.querySelectorAll("[data-count]"));
  if (counters.length && !reducedMotion && "IntersectionObserver" in window) {
    var animateCount = function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10);
      if (!isFinite(target)) return;
      var start = null;
      var duration = 850;
      var step = function (ts) {
        if (start === null) start = ts;
        var t = Math.min(1, (ts - start) / duration);
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = String(Math.round(target * eased));
        if (t < 1) window.requestAnimationFrame(step);
      };
      el.textContent = "0";
      window.requestAnimationFrame(step);
    };
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { countObserver.observe(el); });
  }

  /* ---------- Hero: parallasse leggera (solo pointer fine) ---------- */

  var stack = document.getElementById("sheet-stack");
  var hero = document.querySelector(".hero");
  if (stack && hero && !reducedMotion) {
    var setVars = function (mx, my) {
      stack.style.setProperty("--mx", mx.toFixed(1) + "px");
      stack.style.setProperty("--my", my.toFixed(1) + "px");
    };
    if (finePointer) {
      var pointerTick = false;
      hero.addEventListener("pointermove", function (event) {
        if (pointerTick) return;
        pointerTick = true;
        window.requestAnimationFrame(function () {
          var rect = hero.getBoundingClientRect();
          var mx = ((event.clientX - rect.left) / rect.width - 0.5) * 10;
          var my = ((event.clientY - rect.top) / rect.height - 0.5) * 8;
          setVars(mx, my);
          pointerTick = false;
        });
      });
      hero.addEventListener("pointerleave", function () { setVars(0, 0); });
    }
    var parallaxTick = false;
    window.addEventListener("scroll", function () {
      if (parallaxTick) return;
      parallaxTick = true;
      window.requestAnimationFrame(function () {
        var sy = Math.max(-14, Math.min(0, -window.scrollY * 0.03));
        stack.style.setProperty("--sy", sy.toFixed(1) + "px");
        parallaxTick = false;
      });
    }, { passive: true });
  }

  /* ---------- Archivio: filtri, ordinamento, stato in URL ---------- */

  var archiveList = document.getElementById("archive-list");
  if (archiveList) {
    var sessions = Array.prototype.slice.call(archiveList.querySelectorAll(".arch-session"));
    var emptyNote = document.getElementById("archive-empty");
    var levelButtons = Array.prototype.slice.call(document.querySelectorAll("[data-level-filter]"));
    var yearSelect = document.getElementById("year-filter");
    var sortToggle = document.getElementById("sort-toggle");
    var LEVELS = ["A1", "A2", "B1", "B2", "C1"];

    var params = new URLSearchParams(window.location.search);
    var state = {
      level: LEVELS.indexOf(params.get("level")) >= 0 ? params.get("level") : "tutti",
      year: params.get("anno") || "tutti",
      sort: params.get("ordine") === "vecchie" ? "vecchie" : "recenti"
    };
    if (yearSelect && state.year !== "tutti") {
      var hasYear = Array.prototype.some.call(yearSelect.options, function (o) { return o.value === state.year; });
      if (!hasYear) state.year = "tutti";
    }

    var syncUrl = function () {
      var qs = new URLSearchParams();
      if (state.level !== "tutti") qs.set("level", state.level);
      if (state.year !== "tutti") qs.set("anno", state.year);
      if (state.sort !== "recenti") qs.set("ordine", state.sort);
      var query = qs.toString();
      var url = window.location.pathname + (query ? "?" + query : "") + window.location.hash;
      window.history.replaceState(null, "", url);
    };

    var apply = function () {
      var visible = 0;
      sessions.forEach(function (session) {
        var levels = (session.getAttribute("data-levels") || "").split(" ");
        var year = session.getAttribute("data-year") || "";
        var okLevel = state.level === "tutti" || levels.indexOf(state.level) >= 0;
        var okYear = state.year === "tutti" || year === state.year;
        var show = okLevel && okYear;
        session.hidden = !show;
        if (show) visible += 1;
        Array.prototype.forEach.call(session.querySelectorAll(".arch-row"), function (row) {
          row.hidden = state.level !== "tutti" && row.getAttribute("data-level") !== state.level;
        });
      });
      if (emptyNote) emptyNote.hidden = visible > 0;

      var ordered = sessions.slice().sort(function (a, b) {
        var da = a.getAttribute("data-session") || "";
        var db = b.getAttribute("data-session") || "";
        return state.sort === "vecchie" ? da.localeCompare(db) : db.localeCompare(da);
      });
      ordered.forEach(function (session) { archiveList.appendChild(session); });

      levelButtons.forEach(function (button) {
        button.setAttribute("aria-pressed", button.getAttribute("data-level-filter") === state.level ? "true" : "false");
      });
      if (yearSelect) yearSelect.value = state.year;
      if (sortToggle) {
        sortToggle.textContent = state.sort === "vecchie" ? "Più vecchie prima" : "Più recenti prima";
        sortToggle.setAttribute("data-sort", state.sort);
      }
    };

    levelButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        state.level = button.getAttribute("data-level-filter") || "tutti";
        apply();
        syncUrl();
      });
    });
    if (yearSelect) {
      yearSelect.addEventListener("change", function () {
        state.year = yearSelect.value;
        apply();
        syncUrl();
      });
    }
    if (sortToggle) {
      sortToggle.addEventListener("click", function () {
        state.sort = state.sort === "recenti" ? "vecchie" : "recenti";
        apply();
        syncUrl();
      });
    }

    /* Le card "Inizia" filtrano l'archivio senza ricaricare la pagina. */
    Array.prototype.forEach.call(document.querySelectorAll("[data-level-link]"), function (link) {
      link.addEventListener("click", function (event) {
        var level = link.getAttribute("data-level-link");
        if (LEVELS.indexOf(level) < 0) return;
        event.preventDefault();
        state.level = level;
        apply();
        window.history.replaceState(null, "", window.location.pathname + "?level=" + level + "#archivio");
        var archive = document.getElementById("archivio");
        if (archive) archive.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
      });
    });

    apply();
  }
})();
