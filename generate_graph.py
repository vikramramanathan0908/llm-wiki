"""Generate a visual graph from wiki pages on disk."""
import os, json, re

WIKI_DIR = "wiki_pages"

def load_pages():
    pages = {}
    for root, _, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, WIKI_DIR)
                with open(path) as fp:
                    pages[rel] = fp.read()
    return pages

def extract_links(name, content, all_names):
    """Find references to other pages within content."""
    links = []
    for other in all_names:
        if other == name:
            continue
        keyword = os.path.splitext(os.path.basename(other))[0].replace("-", " ")
        if keyword.lower() in content.lower():
            links.append(other)
    return links

pages = load_pages()
names = list(pages.keys())

nodes = []
edges = []
seen_edges = set()

for name, content in pages.items():
    category = name.split("/")[0] if "/" in name else "Other"
    color = "#4f8ef7" if category == "Cognee" else "#e63946" if category == "Redis" else "#2ec4b6"
    nodes.append({"id": name, "label": os.path.splitext(os.path.basename(name))[0], "color": color, "group": category})
    for target in extract_links(name, content, names):
        key = tuple(sorted([name, target]))
        if key not in seen_edges:
            edges.append({"from": name, "to": target})
            seen_edges.add(key)

graph_data = json.dumps({"nodes": nodes, "edges": edges})

html = f"""<!DOCTYPE html>
<html>
<head>
<title>LLM Knowledge Wiki — Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #0e1117; color: white; font-family: sans-serif; }}
  #graph {{ width: 100vw; height: 100vh; }}
  #legend {{ position: fixed; top: 16px; left: 16px; background: rgba(0,0,0,0.7); padding: 12px 16px; border-radius: 8px; }}
  .dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; }}
</style>
</head>
<body>
<div id="legend">
  <b>🧠 LLM Knowledge Wiki</b><br><br>
  <span class="dot" style="background:#4f8ef7"></span>Cognee<br>
  <span class="dot" style="background:#e63946"></span>Redis<br>
  <span class="dot" style="background:#2ec4b6"></span>Other
</div>
<div id="graph"></div>
<script>
const data = {graph_data};
const nodes = new vis.DataSet(data.nodes.map(n => ({{
  id: n.id, label: n.label, color: {{ background: n.color, border: n.color }},
  font: {{ color: '#ffffff', size: 14 }},
  shape: 'dot', size: 18
}})));
const edges = new vis.DataSet(data.edges.map(e => ({{
  from: e.from, to: e.to, color: {{ color: '#555' }}, arrows: 'to'
}})));
const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes, edges }}, {{
  physics: {{ stabilization: true, barnesHut: {{ gravitationalConstant: -3000 }} }},
  interaction: {{ hover: true, tooltipDelay: 100 }},
  edges: {{ smooth: {{ type: 'dynamic' }} }}
}});
</script>
</body>
</html>"""

out = "/Users/vikramramanathan/Desktop/llm-wiki/graph.html"
with open(out, "w") as f:
    f.write(html)

print(f"Graph saved: {len(nodes)} nodes, {len(edges)} edges -> {out}")
