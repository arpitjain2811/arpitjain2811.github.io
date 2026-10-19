// Light/dark toggle (remembered per browser), theme filters, abstract/cite toggles, copy BibTeX.
(function () {
  var root = document.documentElement;
  function current() {
    return root.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  });

  document.querySelectorAll("[data-filters]").forEach(function (bar) {
    bar.hidden = false;
    var scope = bar.parentElement;
    // a theme with nothing on this page gets no button
    bar.querySelectorAll("[data-filter]").forEach(function (b) {
      if (b.dataset.filter !== "all" && !scope.querySelector('[data-topic="' + b.dataset.filter + '"]')) b.hidden = true;
    });
    function apply(id) {
      bar.querySelectorAll("[data-filter]").forEach(function (b) { b.classList.toggle("is-on", b.dataset.filter === id); });
      scope.querySelectorAll("[data-topic]").forEach(function (el) {
        if (el.closest("[data-filters]")) return;
        el.hidden = id !== "all" && el.dataset.topic !== id;
      });
    }
    bar.addEventListener("click", function (e) {
      var b = e.target.closest("[data-filter]");
      if (b) apply(b.dataset.filter);
    });
    var hash = location.hash.slice(1);
    if (hash && bar.querySelector('[data-filter="' + hash + '"]')) apply(hash);
  });

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-toggle]");
    if (t) {
      var panel = document.getElementById(t.dataset.toggle);
      panel.hidden = !panel.hidden;
      t.setAttribute("aria-expanded", String(!panel.hidden));
    }
    var c = e.target.closest("[data-copy]");
    if (c && navigator.clipboard) {
      navigator.clipboard.writeText(document.getElementById(c.dataset.copy).querySelector("pre").textContent).then(function () {
        c.textContent = "copied";
        setTimeout(function () { c.textContent = "copy bibtex"; }, 1500);
      });
    }
  });
})();

// Clips: play muted while on screen, pause off screen; never autoplay under "reduce motion".
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var vids = document.querySelectorAll("video[data-autoplay]");
  if (!vids.length) return;
  function label(btn, v) {
    var paused = v.dataset.userPaused === "1" || (reduce && v.paused);
    btn.dataset.state = paused ? "paused" : "playing";
    btn.setAttribute("aria-label", paused ? "Play the clip" : "Pause the clip");
  }
  vids.forEach(function (v) {
    var btn = v.parentElement.querySelector(".media-toggle");
    if (reduce) v.dataset.userPaused = "1";
    if (btn) {
      btn.hidden = false;
      label(btn, v);
      btn.addEventListener("click", function () {
        if (v.paused) { v.dataset.userPaused = "0"; v.play(); } else { v.dataset.userPaused = "1"; v.pause(); }
        label(btn, v);
      });
    }
  });
  if (!("IntersectionObserver" in window)) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting && v.dataset.userPaused !== "1") { v.play().catch(function () {}); }
      else if (!e.isIntersecting) { v.pause(); }
    });
  }, { threshold: 0.4 });
  vids.forEach(function (v) { io.observe(v); });
})();

// External links open in a new tab, marked with an arrow and announced to screen readers.
(function () {
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (a.host === location.host) return;
    a.target = "_blank";
    a.rel = "noopener";
    a.classList.add("ext");
    var sr = document.createElement("span");
    sr.className = "sr-only";
    sr.textContent = " (opens in a new tab)";
    a.appendChild(sr);
  });
})();

// Figures in a post open larger on click; Esc, a click or the close button shuts them.
(function () {
  var imgs = document.querySelectorAll(".prose figure img");
  if (!imgs.length || typeof HTMLDialogElement !== "function") return;
  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.innerHTML = '<button class="lightbox-close" type="button" aria-label="Close the figure">' +
    '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>' +
    '<img alt=""><p class="lightbox-cap"></p>';
  document.body.appendChild(dlg);
  var big = dlg.querySelector("img"), cap = dlg.querySelector(".lightbox-cap");
  dlg.addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("close", function () { big.removeAttribute("src"); });
  imgs.forEach(function (img) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "zoom";
    btn.setAttribute("aria-haspopup", "dialog");
    img.parentNode.insertBefore(btn, img);
    btn.appendChild(img);
    btn.addEventListener("click", function () {
      var fc = img.closest("figure").querySelector("figcaption");
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      big.classList.toggle("is-svg", /\.svg(\?|$)/.test(big.src));
      cap.textContent = fc ? fc.textContent : "";
      cap.hidden = !fc;
      dlg.showModal();
    });
  });
})();
