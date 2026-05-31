(function () {
  const toggle = document.getElementById("theme-toggle");
  const stored = localStorage.getItem("site-theme");
  if (stored) document.documentElement.setAttribute("data-theme", stored);

  toggle.addEventListener("click", () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("site-theme", next);
  });

  document.getElementById("year").textContent = new Date().getFullYear();

  function hideIfEmpty(id, hasContent) {
    const el = document.getElementById(id);
    if (!hasContent && el) el.closest(".section")?.classList.add("hidden");
  }

  function render(data) {
    const name = data.name || "Your name";
    document.title = name;
    document.getElementById("nav-name").textContent = name;
    document.getElementById("headline").textContent = name;
    document.getElementById("tagline").textContent = data.tagline || "";
    document.getElementById("location").textContent = data.location_public || "";

    const linksEl = document.getElementById("hero-links");
    linksEl.innerHTML = "";
    (data.links || []).forEach((link) => {
      if (!link.url) return;
      const a = document.createElement("a");
      a.href = link.url;
      a.textContent = link.label || link.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      linksEl.appendChild(a);
    });
    if (data.email_public) {
      const a = document.createElement("a");
      a.href = "mailto:" + data.email_public;
      a.textContent = "Email";
      linksEl.appendChild(a);
    }

    const about = document.getElementById("about");
    about.innerHTML = "";
    const aboutText = (data.about || "").trim();
    if (aboutText) {
      aboutText.split(/\n\n+/).forEach((para) => {
        const p = document.createElement("p");
        p.textContent = para.trim();
        about.appendChild(p);
      });
    }
    hideIfEmpty("about", aboutText);

    function fillPills(id, items) {
      const ul = document.getElementById(id);
      ul.innerHTML = "";
      (items || []).forEach((t) => {
        const li = document.createElement("li");
        li.textContent = t;
        ul.appendChild(li);
      });
      hideIfEmpty(id, (items || []).length);
    }
    fillPills("values", data.values);
    fillPills("interests", data.interests);

    const projects = document.getElementById("projects");
    projects.innerHTML = "";
    (data.projects || []).forEach((proj) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = "<h3></h3><p></p><div class='tags'></div>";
      card.querySelector("h3").textContent = proj.title || "Project";
      card.querySelector("p").textContent = proj.summary || "";
      const tags = card.querySelector(".tags");
      (proj.tags || []).forEach((tag) => {
        const s = document.createElement("span");
        s.textContent = tag;
        tags.appendChild(s);
      });
      projects.appendChild(card);
    });
    hideIfEmpty("projects", (data.projects || []).length);

    const reading = document.getElementById("reading");
    reading.innerHTML = "";
    (data.reading || []).forEach((item) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = "<h3></h3><p></p>";
      card.querySelector("h3").textContent = item.title || "Reading";
      card.querySelector("p").textContent = item.why || "";
      reading.appendChild(card);
    });
    hideIfEmpty("reading", (data.reading || []).length);

    const quotes = document.getElementById("quotes");
    quotes.innerHTML = "";
    (data.quotes || []).forEach((q) => {
      const bq = document.createElement("blockquote");
      bq.textContent = q.text || "";
      if (q.context) {
        const cite = document.createElement("cite");
        cite.textContent = q.context;
        bq.appendChild(cite);
      }
      quotes.appendChild(bq);
    });
    hideIfEmpty("quotes", (data.quotes || []).length);
  }

  fetch("content.json")
    .then((r) => r.json())
    .then(render)
    .catch(() => {
      document.getElementById("tagline").textContent =
        "Run: python main.py site build — then open this folder's index.html";
    });
})();
