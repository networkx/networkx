import json


class display_d3js:
    def __init__(self, json_graph, js, html):
        """
        Parameters
        ----------
        json_graph : str
            Path to JSON representation of graph, generated using a
            methods from `nx.json_graph`.
        js : str
            Path to JavaScript to include.  The content of `json`
            is provider as the `graph` variable in JavaScript.
        html : str
            Path to the HTML to render.  The JavaScript segment is
            automatically appended into the document body as a
            ``<script>`` tag.

        """
        with open(json_graph) as f:
            graph = f.read()

        with open(js) as f:
            graph_var = f"var graph = {graph};\n"
            script = graph_var + f.read()

        with open(html) as f:
            html = f.read()
            if "<body>" not in html:
                raise RuntimeError("Require <body> tag inside HTML file")
            html = html.replace("</body>", f"\n<script>\n{script}\n</script>\n</body>")

        self._html = html

    def _repr_html_(self):
        return self._html
