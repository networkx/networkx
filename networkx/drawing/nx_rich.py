"""
Example:
    from networkx.drawing.nx_rich import *
    from networkx.drawing.nx_rich import demo
    demo()
"""


from typing import Iterator, List, Optional, Tuple
import networkx as nx
from collections import defaultdict
from rich._loop import loop_first, loop_last
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.jupyter import JupyterMixin
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleStack, StyleType
from rich.styled import Styled
from rich.text import Text


def jit_mkinit_import(modname):
    """
    >>> rich = jit_mkinit_import('rich')
    """
    import ubelt as ub
    import mkinit
    module = ub.import_module_from_name(modname)
    text = mkinit.static_init(module.__file__)
    ns = {}
    exec(text, ns, ns)
    module.__dict__.update(ns)


class RichGraph(JupyterMixin):
    """A renderable for a tree structure.


    Args:
        label (RenderableType): The renderable or str for the tree label.
        style (StyleType, optional): Style of this tree. Defaults to "tree".
        guide_style (StyleType, optional): Style of the guide lines. Defaults to "tree.line".
        expanded (bool, optional): Also display children. Defaults to True.
        highlight (bool, optional): Highlight renderable (if str). Defaults to False.

    CommandLine:
        xdoctest -m /home/joncrall/code/networkx/networkx/drawing/nx_rich.py RichGraph

    Example:
        >>> from networkx.drawing.nx_rich import *  # NOQA
        >>> from networkx.drawing.nx_rich import _find_sources
        >>> import rich
        >>> from rich.panel import Panel
        >>> from rich.console import Group
        >>> graph = nx.erdos_renyi_graph(13, 0.15, directed=True)
        >>> panel = Panel.fit("Just a panel", border_style="red")
        >>> graph.nodes[3]['__rich__'] = Group("📄 Panels", panel)
        >>> nx.write_network_text(graph)
        >>> #source = _find_sources(graph)
        >>> #for s in source:
        ... #    nx.write_network_text(graph, sources=[s])
        >>> print('End Target')
        >>> #
        >>> rgraph = RichGraph(graph)
        >>> import rich
        >>> print('Rich Part')
        >>> rich.print(rgraph)
        >>> #for s in sources:
        >>> #    rich.print(s)
        >>> print('End Rich Part')
        >>> #

    """

    def __init__(
        self,
        graph: nx.Graph,
        *,
        root=None,
        style: StyleType = "tree",
        guide_style: StyleType = "tree.line",
        expanded: bool = True,
        highlight: bool = False,
        hide_root: bool = False,
    ) -> None:
        self.graph = graph
        self.style = style
        self.root = root
        self.guide_style = guide_style
        self.expanded = expanded
        self.highlight = highlight
        self.hide_root = hide_root

    def _rich_update(self, node, renderable, **new_data):
        node_data = self.graph.nodes[node]
        node_data['__rich__'] = renderable
        node_data.update(new_data)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        """
        """
        graph = self.graph
        with_labels = 0
        max_depth = None
        sources = None
        ascii_only = options.ascii_only
        is_directed = graph.is_directed()
        if is_directed:
            glyphs = AsciiDirectedGlyphs if ascii_only else UtfDirectedGlyphs
            succ = graph.succ
            pred = graph.pred
        else:
            glyphs = AsciiUndirectedGlyphs if ascii_only else UtfUndirectedGlyphs
            succ = graph.adj
            pred = graph.adj

        # --- Rich parts
        new_line = Segment.line()
        get_style = console.get_style
        null_style = Style.null()
        # guide_style = get_style(self.guide_style, default="") or null_style
        SPACE, CONTINUE, FORK, END = range(4)

        Guides = glyphs
        TREE_GUIDES = (Guides.endof_forest, Guides.within_tree, Guides.mid, Guides.last)

        _Segment = Segment

        def make_guide(index: int, style: Style) -> Segment:
            """Make a Segment for a level of the guide lines."""
            line = TREE_GUIDES[index]
            return _Segment(line, style)

        # levels: List[Segment] = [make_guide(CONTINUE, guide_style)]
        # push(iter(loop_last([self])))

        # guide_style_stack = StyleStack(get_style(self.guide_style))
        style_stack = StyleStack(get_style(self.style))
        remove_guide_styles = Style(bold=False, underline2=False)

        # --- <Rich parts>

        if max_depth == 0:
            yield glyphs.empty + " ..."
            return

        elif len(graph.nodes) == 0:
            yield glyphs.empty
            return

        # If the nodes to traverse are unspecified, find the minimal set of
        # nodes that will reach the entire graph
        if sources is None:
            sources = _find_sources(graph)

        # Populate the stack with each:
        # 1. parent node in the DFS tree (or None for root nodes),
        # 2. the current node in the DFS tree
        # 2. a list of indentations indicating depth
        # 3. a flag indicating if the node is the final one to be written.
        # Reverse the stack so sources are popped in the correct order.
        last_idx = len(sources) - 1
        stack = [
            (None, node, [], (idx == last_idx)) for idx, node in enumerate(sources)
        ][::-1]

        num_skipped_children = defaultdict(lambda: 0)
        seen_nodes = set()
        while stack:
            parent, node, indents, this_islast = stack.pop()

            if node is not Ellipsis:
                skip = node in seen_nodes
                if skip:
                    # Mark that we skipped a parent's child
                    num_skipped_children[parent] += 1

                if this_islast:
                    # If we reached the last child of a parent, and we skipped
                    # any of that parents children, then we should emit an
                    # ellipsis at the end after this.
                    if num_skipped_children[parent] and parent is not None:

                        # Append the ellipsis to be emitted last
                        next_islast = True
                        try_frame = (node, Ellipsis, indents, next_islast)
                        stack.append(try_frame)

                        # Redo this frame, but not as a last object
                        next_islast = False
                        try_frame = (parent, node, indents, next_islast)
                        stack.append(try_frame)
                        continue

                if skip:
                    continue
                seen_nodes.add(node)

            if not indents:
                # Top level items (i.e. trees in the forest) get different
                # glyphs to indicate they are not actually connected
                if this_islast:
                    this_prefix = indents + [glyphs.newtree_last]
                    next_prefix = indents + [glyphs.endof_forest]
                else:
                    this_prefix = indents + [glyphs.newtree_mid]
                    next_prefix = indents + [glyphs.within_forest]

            else:
                # For individual tree edges distinguish between directed and
                # undirected cases
                if this_islast:
                    this_prefix = indents + [glyphs.last]
                    next_prefix = indents + [glyphs.endof_forest]
                else:
                    this_prefix = indents + [glyphs.mid]
                    next_prefix = indents + [glyphs.within_tree]

            if node is Ellipsis:
                label = " ..."
                suffix = ""
                children = []
                node_data = {}
            else:
                node_data = graph.nodes[node]

                if with_labels:
                    label = str(graph.nodes[node].get("label", node))
                else:
                    label = str(node)

                # Determine:
                # (1) children to traverse into after showing this node.
                # (2) parents to immediately show to the right of this node.
                if is_directed:
                    # In the directed case we must show every successor node
                    # note: it may be skipped later, but we don't have that
                    # information here.
                    children = list(succ[node])
                    # In the directed case we must show every predecessor
                    # except for parent we directly traversed from.
                    handled_parents = {parent}
                else:
                    # Showing only the unseen children results in a more
                    # concise representation for the undirected case.
                    children = [
                        child for child in succ[node] if child not in seen_nodes
                    ]

                    # In the undirected case, parents are also children, so we
                    # only need to immediately show the ones we can no longer
                    # traverse
                    handled_parents = {*children, parent}

                if max_depth is not None and len(indents) == max_depth - 1:
                    # Use ellipsis to indicate we have reached maximum depth
                    if children:
                        children = [Ellipsis]
                    handled_parents = {parent}

                # The other parents are other predecessors of this node that
                # are not handled elsewhere.
                other_parents = [p for p in pred[node] if p not in handled_parents]
                if other_parents:
                    if with_labels:
                        other_parents_labels = ", ".join(
                            [str(graph.nodes[p].get("label", p)) for p in other_parents]
                        )
                    else:
                        other_parents_labels = ", ".join(
                            [str(p) for p in other_parents]
                        )
                    suffix = " ".join(["", glyphs.backedge, other_parents_labels])
                else:
                    suffix = ""

            ### Rich parts
            # guide_style = guide_style_stack.current + get_style(node.guide_style)

            node_renderable = node_data.get('__rich__', None)

            guide_style = node_data.get('guide_style', None)
            if guide_style is None:
                guide_style = get_style(self.style) or null_style
            else:
                guide_style = get_style(guide_style) or null_style

            style = get_style(self.style) or null_style
            # node_style = get_style(self.style) or null_style

            prefix = [_Segment(p, guide_style) for p in this_prefix]

            suffix_renderable = Text(suffix)
            if node_renderable is None:
                node_renderable = Text(label)

            # from rich.layout import Layout
            # line_renderable = Layout()
            # line_renderable.split_row(node_renderable, suffix_renderable)
            # line_renderable.split_row("a", "b")
            # from rich.table import Table
            # line_renderable = Table()
            # line_renderable.add_row(node_renderable, suffix_renderable)
            from rich.columns import Columns
            line_renderable = Columns([
                node_renderable, suffix_renderable],
                equal=False,
                expand=False,
                right_to_left=False,
                align='left')
            # TODO: grab a node style likely from graph properties
            # null_style
            # node.style
            style = style_stack.current + get_style(self.style)

            # style = style_stack.current + get_style(node_style)
            # prefix = levels[(2 if self.hide_root else 1) :]
            width = options.max_width - sum(level.cell_length for level in prefix)
            renderable_lines = console.render_lines(
                Styled(line_renderable, style),
                options.update(
                    width=width,
                    highlight=self.highlight,
                    height=None,
                ),
                pad=options.justify is not None,
            )

            # depth = len(indents)
            # if not (depth == 0 and self.hide_root):
            if True:
                for first, line in loop_first(renderable_lines):
                    if prefix:
                        yield from _Segment.apply_style(
                            prefix,
                            style.background_style,
                            post_style=remove_guide_styles,
                        )
                    yield from line
                    yield new_line

                    # if first and prefix:
                    #     prefix[-1] = make_guide(
                    #         SPACE if last else CONTINUE, prefix[-1].style or null_style
                    #     )

            # Emit the line for this node, this will be called for each node
            # exactly once.
            # yield "".join(prefix + [label, suffix])

            # Push children on the stack in reverse order so they are popped in
            # the original order.
            for idx, child in enumerate(children[::-1]):
                next_islast = idx == 0
                try_frame = (node, child, next_prefix, next_islast)
                stack.append(try_frame)

    # def __rich_measure__(
    #     self, console: "Console", options: "ConsoleOptions"
    # ) -> "Measurement":
    #     stack: List[Iterator[RichNode]] = [iter([self])]
    #     pop = stack.pop
    #     push = stack.append
    #     minimum = 0
    #     maximum = 0
    #     measure = Measurement.get
    #     level = 0
    #     while stack:
    #         iter_tree = pop()
    #         try:
    #             tree = next(iter_tree)
    #         except StopIteration:
    #             level -= 1
    #             continue
    #         push(iter_tree)
    #         min_measure, max_measure = measure(console, options, tree.label)
    #         indent = level * 4
    #         minimum = max(min_measure + indent, minimum)
    #         maximum = max(max_measure + indent, maximum)
    #         if tree.expanded and tree.succ:
    #             push(iter(tree.succ))
    #             level += 1
    #     return Measurement(minimum, maximum)


class _AsciiBaseGlyphs:
    empty = "+"
    newtree_last = "+-- "
    newtree_mid = "+-- "
    endof_forest = "    "
    within_forest = ":   "
    within_tree = "|   "


class AsciiDirectedGlyphs(_AsciiBaseGlyphs):
    last = "L-> "
    mid = "|-> "
    backedge = "<-"


class AsciiUndirectedGlyphs(_AsciiBaseGlyphs):
    last = "L-- "
    mid = "|-- "
    backedge = "-"


class _UtfBaseGlyphs:
    # Notes on available box and arrow characters
    # https://en.wikipedia.org/wiki/Box-drawing_character
    # https://stackoverflow.com/questions/2701192/triangle-arrow
    empty = "╙"
    newtree_last = "╙── "
    newtree_mid = "╟── "
    endof_forest = "    "
    within_forest = "╎   "
    within_tree = "│   "


class UtfDirectedGlyphs(_UtfBaseGlyphs):
    last = "└─╼ "
    mid = "├─╼ "
    backedge = "╾"


class UtfUndirectedGlyphs(_UtfBaseGlyphs):
    last = "└── "
    mid = "├── "
    backedge = "─"


def _find_sources(graph):
    # For each connected part of the graph, choose at least
    # one node as a starting point, preferably without a parent
    is_directed = graph.is_directed()
    if is_directed:
        # Choose one node from each SCC with minimum in_degree
        sccs = list(nx.strongly_connected_components(graph))
        # condensing the SCCs forms a dag, the nodes in this graph with
        # 0 in-degree correspond to the SCCs from which the minimum set
        # of nodes from which all other nodes can be reached.
        scc_graph = nx.condensation(graph, sccs)
        supernode_to_nodes = {sn: [] for sn in scc_graph.nodes()}
        # Note: the order of mapping differs between pypy and cpython
        # so we have to loop over graph nodes for consistency
        mapping = scc_graph.graph["mapping"]
        for n in graph.nodes:
            sn = mapping[n]
            supernode_to_nodes[sn].append(n)
        sources = []
        for sn in scc_graph.nodes():
            if scc_graph.in_degree[sn] == 0:
                scc = supernode_to_nodes[sn]
                node = min(scc, key=lambda n: graph.in_degree[n])
                sources.append(node)
    else:
        # For undirected graph, the entire graph will be reachable as
        # long as we consider one node from every connected component
        sources = [
            min(cc, key=lambda n: graph.degree[n])
            for cc in nx.connected_components(graph)
        ]
        sources = sorted(sources, key=lambda n: graph.degree[n])
    return sources


def demo():
    from rich.console import Group
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    import ubelt as ub

    graph = nx.erdos_renyi_graph(9, 0.7, directed=False)
    rgraph_plain = RichGraph(graph.copy(), root="🌲 [b green]Plain Rich Tree", highlight=True, hide_root=True)

    rgraph_fancy = RichGraph(graph.copy(), root="🌲 [b green]Fancy Rich Tree", highlight=True, hide_root=True)
    table = Table(row_styles=["", "dim"])

    table.add_column("Released", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Box Office", justify="right", style="green")

    table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
    table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
    table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
    table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")

    syntax = Syntax(ub.codeblock(
        '''
        class Segment(NamedTuple):
        text: str = ""
        style: Optional[Style] = None
        is_control: bool = False
        '''),
        "python", theme="monokai", line_numbers=True)
    markdown = Markdown(
        '''
        ### example.md
        > Hello, World!
        >
        > Markdown _all_ the things
        '''
    )
    rgraph_fancy._rich_update(1, ":file_folder: Renderables", guide_style="red")
    rgraph_fancy._rich_update(2, ":file_folder: [bold yellow]Atomic", guide_style="uu green")
    rgraph_fancy._rich_update(3, Group("📄 Syntax", syntax))
    rgraph_fancy._rich_update(4, Group("📄 Markdown", Panel(markdown, border_style="green")))
    rgraph_fancy._rich_update(5, ":file_folder: [bold magenta]Containers", guide_style="bold magenta", expanded=True)
    panel = Panel.fit("Just a panel", border_style="red")
    rgraph_fancy._rich_update(6, Group("📄 Panels", panel))
    rgraph_fancy._rich_update(7, Group("📄 [b magenta]Table", table))

    console = Console()

    console.print('<Plain Network Text>')
    nx.write_network_text(graph, console.print, end='')
    console.print('</Plain Network Text>')

    console.print('<Plain Rich Graph>')
    console.print(rgraph_plain)
    console.print('</Plain Rich Graph>')

    if 1:
        console.print('<Fancy Rich Graph>')
        console.print(rgraph_fancy)
        console.print('</Fancy Rich Graph>')

    #


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/networkx/networkx/drawing/nx_rich.py
    """
    demo()
