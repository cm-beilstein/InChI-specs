"""giscus comment threads for the generated pages.

One discussion per molecule (row with data-term) and per explain section
(h2 with an id). A 'Comment' button opens that thread in place; only one
is open at a time. Threads live in GitHub Discussions of the repo named
in tools/giscus.json, which must be public, have Discussions on and the
giscus app installed (https://giscus.app). With 'repo' empty the pages
get no buttons.

Discussion titles, e.g.:
  enhanced-stereo · molecule 13
  enhanced-stereo · explain · meso
"""

import json
import os

CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "giscus.json")

SNIPPET = """<style>
.cmt-btn { font: inherit; font-size: .8rem; margin-left: .6rem; padding: .1rem .5rem;
           border: 1px solid #bbb; border-radius: 4px; background: #fff; color: #444;
           cursor: pointer; vertical-align: middle; }
.cmt-btn:hover { background: #f3f3f3; }
.cmt-box { padding: .5rem 0; }
</style>
<script>
(function () {
  const CFG = %(config)s;
  const SPEC = %(spec)s;
  let open = null;

  // Close the open thread; open the one for 'term' after 'anchor'
  function show(term, anchor, inRow) {
    if (open) { open.remove(); }
    const box = document.createElement("div");
    box.className = "cmt-box";
    const s = document.createElement("script");
    s.src = "https://giscus.app/client.js";
    s.async = true;
    s.crossOrigin = "anonymous";
    const attrs = { "repo": CFG.repo, "repo-id": CFG.repoId, "category": CFG.category,
                    "category-id": CFG.categoryId, "mapping": "specific", "term": term,
                    "strict": "1", "reactions-enabled": "1", "emit-metadata": "0",
                    "input-position": "top", "theme": "light", "lang": "en" };
    for (const k in attrs) { s.setAttribute("data-" + k, attrs[k]); }
    box.appendChild(s);

    // Rows get a full-width row below; sections a block below the heading
    if (inRow) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = anchor.children.length;
      td.appendChild(box);
      tr.appendChild(td);
      anchor.after(tr);
      open = tr;
    } else {
      anchor.after(box);
      open = box;
    }
  }

  function button(term, anchor, inRow) {
    const b = document.createElement("button");
    b.className = "cmt-btn";
    b.type = "button";
    b.textContent = "Comment";
    b.title = "Discuss: " + term;
    b.addEventListener("click", () => show(term, anchor, inRow));
    return b;
  }

  // Molecules: rows carrying data-term
  document.querySelectorAll("tr[data-term]").forEach(tr => {
    tr.querySelector("td.pic").appendChild(button(tr.dataset.term, tr, true));
  });

  // Explain sections: h2 with an id, on pages that are not example tables
  if (!document.querySelector("tr[data-term]")) {
    document.querySelectorAll("h2[id]").forEach(h => {
      h.appendChild(button(SPEC + " · explain · " + h.id, h, false));
    });
  }
})();
</script>
"""


def snippet(spec):
    """HTML to insert before </body>; '' when giscus is not configured."""
    cfg = json.load(open(CONFIG)) if os.path.exists(CONFIG) else {}
    if not cfg.get("repo"):
        return ""
    return SNIPPET % dict(config=json.dumps(cfg), spec=json.dumps(spec))
