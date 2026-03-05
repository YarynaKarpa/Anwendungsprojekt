// Modern UI helpers: theme toggle, ripple, poster dropzone
(function(){
  // Theme toggle (dark-only ambiance by default, but include toggle skeleton)
  const KEY = "theme";
  const btn = document.getElementById("theme-toggle");
  const root = document.documentElement;

  function setTheme(mode) {
    // We keep a dark ambient base; here just an example hook if you want light
    localStorage.setItem(KEY, mode);
    if (mode === "light") {
      root.style.setProperty("--bg-card", "rgba(255,255,255,.9)");
      root.style.setProperty("--bg-elev", "#fff");
      root.style.setProperty("--txt", "#0b1020");
      root.style.setProperty("--muted", "#4b5563");
      root.style.setProperty("--border", "rgba(2,6,23,.08)");
      document.body.style.background =
        "radial-gradient(900px 500px at 10% -10%, rgba(99,102,241,.12), transparent 50%)," +
        "radial-gradient(900px 500px at 110% 10%, rgba(14,165,233,.12), transparent 50%)," +
        "linear-gradient(180deg, #f6f7fb, #eef2f7)";
    } else {
      localStorage.removeItem(KEY);
      location.reload(); // easiest reset to original CSS custom props
    }
  }
  if (btn) {
    btn.addEventListener("click", () => {
      const mode = localStorage.getItem(KEY) === "light" ? "dark" : "light";
      setTheme(mode);
      btn.blur();
    });
  }

  // Subtle ripple on buttons
  document.addEventListener("click", function(e){
    const el = e.target.closest(".btn");
    if (!el) return;
    const ripple = document.createElement("span");
    const rect = el.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.position = "absolute";
    ripple.style.left = `${e.clientX - rect.left - size/2}px`;
    ripple.style.top = `${e.clientY - rect.top - size/2}px`;
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.borderRadius = "50%";
    ripple.style.background = "rgba(255,255,255,.25)";
    ripple.style.pointerEvents = "none";
    ripple.style.transform = "scale(0)";
    ripple.style.transition = "transform 300ms ease, opacity 500ms ease";
    el.appendChild(ripple);
    requestAnimationFrame(()=>{ ripple.style.transform = "scale(1)"; ripple.style.opacity = "0"; });
    setTimeout(()=> ripple.remove(), 500);
  }, false);

  // Poster dropzone enhancer (if present)
  const dz = document.querySelector(".dropzone");
  const fileInput = dz ? dz.querySelector('input[type="file"]') : null;
  if (dz && fileInput) {
    ["dragenter","dragover"].forEach(evt =>
      dz.addEventListener(evt, e => { e.preventDefault(); dz.classList.add("dragover"); })
    );
    ["dragleave","drop"].forEach(evt =>
      dz.addEventListener(evt, e => { e.preventDefault(); dz.classList.remove("dragover"); })
    );
    dz.addEventListener("click", () => fileInput.click());
    dz.addEventListener("drop", e => { if (e.dataTransfer.files.length) fileInput.files = e.dataTransfer.files; });
  }
})();
