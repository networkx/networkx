from flask import Flask, render_template, request
import networkx as nx
import logging

# Import your core functions from contiguous_labeling.py
from contiguous_labeling import (
    contiguous_oriented_labeling,
    verify_contiguous_labeling,
    find_uv_to_make_bridgeless,
)

logging.basicConfig(filename='logs.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

#  Helpers 

def parse_edges(text):
    """
    Reads lines 'u v'. Returns (edges, all_int) where all_int indicates
    whether all node labels could be parsed as integers.
    """
    edges = []
    text = (text or "").strip()
    if not text:
        return edges, False

    all_int = True
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        u, v = parts
        try:
            u = int(u)
        except:
            all_int = False
        try:
            v = int(v)
        except:
            all_int = False
        edges.append((u, v))
    return edges, all_int


def relabel_one_based_if_numeric(G: nx.Graph, all_int: bool) -> nx.Graph:
    """
    If all node labels are integers (maybe starting at 0), relabel nodes to 1..n
    in ascending order for nicer display (1,2,3,...).
    """
    if not all_int or G.number_of_nodes() == 0:
        return G
    nodes_sorted = sorted(G.nodes())
    mapping = {node: i + 1 for i, node in enumerate(nodes_sorted)}
    return nx.relabel_nodes(G, mapping, copy=True)


def build_labeling_and_status(G: nx.Graph):
    """
    Returns (labeling, ordered_edges, status_dict)
    labeling: list of (label_idx, u, v) directed from u(=i⁻) to v(=i⁺)
    ordered_edges: [(u, v), ...] same order/orientation as labeling
    status_dict: fields for UI
    """
    status = {
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "connected": nx.is_connected(G) if G.number_of_nodes() > 0 else False,
        "bridgeless": False,
        "almost_bridgeless": False,
        "contiguous": False,
        "uv_edge": None,
        "error": None,
    }

    if not status["connected"]:
        status["error"] = "הגרף איננו קשיר."
        return None, [], status

    # Bridges & almost-bridgeless (strict definition: exactly one added edge fixes all bridges)
    bridges = list(nx.bridges(G))
    status["bridgeless"] = (len(bridges) == 0)
    uv = find_uv_to_make_bridgeless(G)
    status["uv_edge"] = uv
    status["almost_bridgeless"] = (uv is not None)

    labeling = contiguous_oriented_labeling(G)
    if labeling is None:
        status["error"] = "נכשל ביצירת תיוג רציף לגרף."
        return None, [], status

    status["contiguous"] = verify_contiguous_labeling(G, labeling)
    ordered_edges = [(u, v) for _, u, v in labeling]
    return labeling, ordered_edges, status


# ---------- Routes ----------

@app.route("/", methods=["GET", "POST"])
def index():
    edges_text = ""
    error = None
    status_text = None
    labeling_text = None
    ordered_edges = []  # [(u,v), ...] oriented order for client visualization

    if request.method == "POST":
        try:
            edges_text = request.form.get("edges", "")
            edges, all_int = parse_edges(edges_text)

            G = nx.Graph()
            G.add_edges_from(edges)

            # Remap to 1..n if nodes are all numeric
            G = relabel_one_based_if_numeric(G, all_int)

            labeling, ordered_edges, status = build_labeling_and_status(G)

            # Status text
            status_lines = [
                f"מספר קודקודים: {status['n']}",
                f"מספר קשתות: {status['m']}",
                f"קשיר: {'כן' if status['connected'] else 'לא'}",
                f"ללא-גשרים: {'כן' if status['bridgeless'] else 'לא'}",
                f"כמעט ללא-גשרים (הגדרה מחמירה): {'כן' if status['almost_bridgeless'] else 'לא'}",
                f"תיוג רציף נמצא: {'כן' if status['contiguous'] else 'לא'}",
            ]
            if status["uv_edge"]:
                status_lines.append(f"קשת להוספה שתסיר גשרים: {status['uv_edge']}")
            if status["error"]:
                status_lines.append(f"שגיאה: {status['error']}")
            status_text = "\n".join(status_lines)

            if labeling:
                lab_lines = [f"{i}. {u}⁻ → {v}⁺" for i, (_, u, v) in enumerate(labeling, start=1)]
                labeling_text = "תיוג (סדר וקוטביות הקשתות):\n" + "\n".join(lab_lines)

        except Exception as e:
            error = f"שגיאה: {str(e)}"
            logger.exception("Error during processing")

    return render_template(
        "index.html",
        error=error,
        edges_text=edges_text,
        status_text=status_text,
        labeling_text=labeling_text,
        ordered_edges=ordered_edges,  # used to draw arrow direction + **order numbers only**
    )


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
