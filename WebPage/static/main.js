// static/main.js
(function () {
  "use strict";

  /* ---------- helper: turn textarea → edge array ---------- */
  function parseEdgeList() {
    const lines = document
        .getElementById("edge-list")
        .value.split(/\r?\n/)
        .map(l => l.trim())
        .filter(Boolean);

    const uniq = new Set(), edges = [];
    lines.forEach(l => {
      const [a, b] = l.split(/\s+/).map(Number);
      if (!Number.isInteger(a) || !Number.isInteger(b) || a === b) return;
      const u = Math.min(a, b), v = Math.max(a, b);
      const str = `${u} ${v}`;
      if (!uniq.has(str)) { uniq.add(str); edges.push(str); }
    });
    return edges;
  }

  /* ---------- helper: draw (or redraw) the graph ---------- */
  function refreshGraph(weights = []) {
    const edges = parseEdgeList();
    fetch("/plot", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body:   JSON.stringify({edges, weights})
    })
    .then(r => r.json())
    .then(({img}) => {
      document.getElementById("graph-area").innerHTML =
        `<img src="${img}" alt="graph">`;
    });
  }

  /* ---------- existing random-example helper ---------- */
  function randomExample() {
    const n = Math.floor(Math.random() * 5) + 4; // 4–8 vertices
    const edges = [];

    // spanning tree
    for (let v = 1; v < n; v++) {
      const u = Math.floor(Math.random() * v);
      edges.push([u, v]);
    }
    // extra edges
    const extra = Math.floor(Math.random() * (n - 2));
    for (let k = 0; k < extra; k++) {
      let u = Math.floor(Math.random() * n);
      let v = Math.floor(Math.random() * n);
      if (u !== v && !edges.some(([x, y]) => (x === u && y === v) || (x === v && y === u)))
        edges.push([u, v]);
    }
    document.getElementById("edge-list").value =
      edges.map(e => e.join(" ")).join("\n");
    refreshGraph();
  }

  /* ---------- DOM bindings ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    // random
    const btnRand = document.getElementById("btn-random");
    if (btnRand) btnRand.addEventListener("click", randomExample);

    // run algorithm  (NEW)
    const btnRun = document.getElementById("btn-run");
    if (btnRun) btnRun.addEventListener("click", () => {
      const edges = parseEdgeList();
      fetch("/solve", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body:   JSON.stringify({edges})
      })
      .then(r => r.json())
      .then(({weights, log}) => {
        refreshGraph(weights);                     // recolour edges
        document.getElementById("log-area").textContent =
          log || "(no output)";
      });
    });
  });
})();
