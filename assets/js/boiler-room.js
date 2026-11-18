// Boiler Room: episode player (speed, skips, chapters, resume, lock-screen controls) and "copy feed URL".
// Without JS the native <audio controls> element is shown instead.
(function () {
  "use strict";
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var SPEEDS = [1, 1.25, 1.5, 1.75, 2];
  function fmt(s) {
    if (!isFinite(s) || s < 0) return "–:––";
    s = Math.floor(s);
    var r = s % 60;
    return Math.floor(s / 60) + ":" + (r < 10 ? "0" : "") + r;
  }

  document.querySelectorAll("[data-br-player]").forEach(function (box) {
    var audio = box.querySelector("audio");
    var ui = box.querySelector(".br-ui");
    if (!audio || !ui) return;
    var q = function (name) { return box.querySelector('[data-br="' + name + '"]'); };
    var playBtn = q("play"), seek = q("seek"), now = q("now"), total = q("total"), speedBtn = q("speed");
    var key = "br-pos:" + location.pathname;
    var speed = parseFloat(store.get("br-speed")) || 1;
    if (SPEEDS.indexOf(speed) < 0) speed = 1;

    audio.removeAttribute("controls");
    audio.hidden = true;
    ui.hidden = false;
    audio.playbackRate = speed;
    speedBtn.textContent = speed + "×";

    function play() {
      var p = audio.play();
      if (p && p.catch) p.catch(function () {});
    }
    function jump(t, andPlay) {
      var d = audio.duration || 0;
      audio.currentTime = Math.max(0, d ? Math.min(t, d - 0.5) : t);
      if (andPlay) play();
    }
    function paint() {
      var d = audio.duration || 0;
      now.textContent = fmt(audio.currentTime);
      if (d && document.activeElement !== seek) {
        var v = Math.round(audio.currentTime / d * 1000);
        seek.value = v;
        seek.style.setProperty("--pct", v / 10 + "%");
      }
    }

    playBtn.addEventListener("click", function () { audio.paused ? play() : audio.pause(); });
    q("back").addEventListener("click", function () { jump(audio.currentTime - 15); });
    q("fwd").addEventListener("click", function () { jump(audio.currentTime + 30); });
    speedBtn.addEventListener("click", function () {
      speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
      audio.playbackRate = speed;
      speedBtn.textContent = speed + "×";
      store.set("br-speed", String(speed));
    });
    box.querySelectorAll("[data-br-jump]").forEach(function (b) {
      b.addEventListener("click", function () { jump(parseFloat(b.dataset.brJump), true); });
    });
    seek.addEventListener("input", function () {
      var d = audio.duration || 0;
      if (!d) return;
      now.textContent = fmt(seek.value / 1000 * d);
      seek.style.setProperty("--pct", seek.value / 10 + "%");
    });
    seek.addEventListener("change", function () {
      var d = audio.duration || 0;
      if (d) jump(seek.value / 1000 * d);
    });

    audio.addEventListener("loadedmetadata", function () {
      total.textContent = fmt(audio.duration);
      var saved = parseFloat(store.get(key));
      if (saved > 10 && saved < audio.duration - 15) { audio.currentTime = saved; paint(); }
    });
    var last = 0;
    audio.addEventListener("timeupdate", function () {
      paint();
      var t = Date.now();
      if (t - last > 4000) { last = t; store.set(key, String(audio.currentTime)); }
    });
    audio.addEventListener("play", function () {
      box.classList.add("is-playing");
      playBtn.setAttribute("aria-label", "Pause episode");
      if ("mediaSession" in navigator) {
        try {
          navigator.mediaSession.metadata = new MediaMetadata({ title: box.dataset.title || document.title, artist: "Boiler Room" });
          navigator.mediaSession.setActionHandler("seekbackward", function () { jump(audio.currentTime - 15); });
          navigator.mediaSession.setActionHandler("seekforward", function () { jump(audio.currentTime + 30); });
        } catch (e) {}
      }
    });
    audio.addEventListener("pause", function () {
      box.classList.remove("is-playing");
      playBtn.setAttribute("aria-label", "Play episode");
      store.set(key, String(audio.currentTime));
    });
    audio.addEventListener("ended", function () { store.set(key, "0"); });
  });

  document.querySelectorAll("[data-br-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = document.getElementById(b.dataset.brCopy);
      if (!el || !navigator.clipboard) return;
      navigator.clipboard.writeText(el.textContent.trim()).then(function () {
        b.textContent = "copied";
        setTimeout(function () { b.textContent = "copy"; }, 1500);
      }).catch(function () {});
    });
  });
})();
