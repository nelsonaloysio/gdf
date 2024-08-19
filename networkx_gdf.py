from io import BufferedReader, BufferedWriter, BytesIO, StringIO, TextIOWrapper
from typing import Optional, Union

import networkx as nx
import pandas as pd

from __version__ import __version__

TYPES = {
    "VARCHAR": str,
    "INT": int,
    "LONG": int,
    "FLOAT": float,
    "DOUBLE": float,
    "BOOLEAN": bool,
}

QUOTES = {
    "'": "single",
    '"': "double",
}

M = 2**31


class GDF():
    """
    Implements ``read_gdf`` and ``write_gdf`` methods compatible with GDF (Graph Data Format) files.

    GDF is a compact file format originally implemented by `GUESS <http://graphexploration.cond.org/>`__.
    Although the software itself is not anymore maintained, the format is still supported by active
    open-source projects such as `Gephi <https://gephi.org/>`__.
    It is based on a tabular text format, and is defined by the simple following rules:

    * A first line starting with ``nodedef>name VARCHAR`` defines the node table.

    * Each subsequent line contains a node name and its attributes separated by commas.

    * A second line starting with ``edgedef>node1 VARCHAR,node2 VARCHAR`` defines the edge table.

    * Each subsequent line contains an edge and its attributes separated by commas.

    The following object types are supported by the format: ``VARCHAR``, ``INT``, ``LONG``, ``FLOAT``,
    ``DOUBLE``, and ``BOOLEAN``. The format also supports single and double quotes as text delimiters.

    .. rubric:: File example

    The example below displays a simple GDF file with two nodes (:math:`A`, :math:`B`) and one edge.
    Note that nodes here do not have any attributes, so the node table after the first line may be left empty:

    .. code-block:: text

       nodedef>name VARCHAR
       edgedef>node1 VARCHAR,node2 VARCHAR
       A,B

    A special property named ``directed`` can be added to the edge table to specify directed (``True``)
    or undirected (``False``) edges. If not found, the graph will be considered as undirected by default.

    .. seealso::

       The `GDF format <https://gephi.org/users/supported-graph-formats/gdf-format/>`__
       specification in Gephi's documentation for more information and examples.

    .. rubric:: Code example

    The following code creates the graph above, writes it to a GDF file, and reads it afterwards:

    .. code-block:: python

       >>> import networkx as nx
       >>> from networkx_gdf import read_gdf, write_gdf
       >>>
       >>> G = nx.Graph()
       >>> G.add_edge("A", "B")
       >>>
       >>> write_gdf(G, "graph.gdf")
       >>> read_gdf("graph.gdf")

       <networkx.classes.graph.Graph object at 0x7f3b9c7b2a60>

    Both methods are static and do not require instantiation as an object if the class is inherited:

    .. code-block:: python

       >>> from networkx_gdf import GDF
       >>>
       >>> class MyClass(GDF):
       >>>     ...
       >>>
       >>> G = MyClass.read_gdf("graph.gdf")
       >>> MyClass.write_gdf(G, "graph.gdf")

    For details on each method, please refer to their documentation:
    `read_gdf <https://networkx-gdf.readthedocs.io/en/latest/api.html#networkx_gdf.read_gdf>`_
    and
    `write_gdf <https://networkx-gdf.readthedocs.io/en/latest/api.html#networkx_gdf.write_gdf>`_.
    """
    @staticmethod
    def read_gdf(
        file: Union[str, BufferedReader, BytesIO, StringIO, TextIOWrapper],
        directed: Optional[bool] = None,
        multigraph: Optional[bool] = None,
        node_attr: Optional[Union[list, bool]] = True,
        edge_attr: Optional[Union[list, bool]] = True,
        encoding: str = "utf-8",
        errors: str = "strict",
    ) -> nx.Graph:
        """
        Returns a NetworkX graph object from file path or object.

        :param object file: Object or string containing path to GDF file.
        :param directed: Consider edges as directed or undirected. Optional. Default is ``None``.

            * If ``None``, decides based on ``'directed'`` edge attribute in file, if it exists.
              In case it does not exist, the graph will be considered as undirected.

            * If ``True``, returns a `DiGraph
              <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__
              or `MultiDiGraph
              <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__
              object.

            * If ``False``, returns a `Graph
              <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
              or `MultiGraph
              <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
              object.

        :param multigraph: Consider multiple edges among pairs of nodes. Optional. Default
            is ``None``.

            * If ``None``, decides based on number of edges among node pairs.

            * If ``True``, returns a `MultiGraph
              <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
              or `MultiDiGraph
              <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__
              object.

            * If ``False``, **sums edge weights** and returns a `Graph
              <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
              or `DiGraph
              <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__
              object.

        :param node_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

            * If a ``list``, only the specified attributes will be considered.

            * If ``True``, all node attributes will be considered.

            * If ``False``, no node attributes will be considered.

        :param edge_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

            * If a ``list``, only the specified attributes will be considered.

            * If ``True``, all edge attributes will be considered.

            * If ``False``, no edge attributes will be considered.

        :param encoding: The encoding of the file. Default is ``'utf-8'``.
            A list of possible values can be found in the `Python documentation
            <https://docs.python.org/3/library/codecs.html#standard-encodings>`__.
        :param errors: The error handling scheme. Default is ``'strict'``.
            A list of possible values can be found in the `Python documentation
            <https://docs.python.org/3/library/codecs.html#codec-base-classes>`__.
        """
        source, target = "node1", "node2"

        def get_def(content):
            return {
                field[0]:
                    TYPES.get(field[1], str) if len(field) > 1 else str
                for field in [
                    tuple(_.rsplit(" ", 1))
                    for _ in content.split("\n", 1)[0].split(">", 1)[-1].split(",")
                ]
            }

        def get_list(content, **params):
            exception = ""

            for quotechar, name in QUOTES.items():
                try:
                    return pd.read_csv(StringIO(content), quotechar=quotechar, **params)
                except Exception as e:
                    exception = f"{exception}\n  {type(e).__name__}: {str(e).rstrip()} ({name} quotes)"

            raise Exception("unable to read data from file considering both single"
                            f"and double quotes as text delimiter.{exception}")

        def read(file, encoding, errors):
            if hasattr(file, "read"):
                graph = file.read()

                if type(graph) == bytes:
                    graph = graph.decode(encoding=encoding, errors=errors)

            else:
                with open(file, "r") as f:
                    graph = f.read()

            try:
                nodes, edges = graph.split("nodedef>", 1)[-1].split("edgedef>", 1)
            except Exception as e:
                raise RuntimeError("unable to find 'nodedef>' and 'edgedef>' in file.") from e

            return nodes, edges

        # Gather node and edge definitions.
        nodes, edges = read(file, encoding=encoding, errors=errors)

        # Get node and edge definitions.
        nodedef = get_def(nodes)
        edgedef = get_def(edges)

        # Build node and edge list assuming single or double quotes as text delimiters.
        nodes = get_list(nodes, names=list(nodedef.keys()), dtype=nodedef, header=0, index_col="name")
        edges = get_list(edges, names=list(edgedef.keys()), dtype=edgedef, header=0)

        # Read directed attribute from data if found.
        if directed is None and "directed" in edges.columns:
            if len(edges["directed"].unique()) > 1:
                raise NotImplementedError(
                    "Graphs with both directed and undirected edges are not supported.\n"
                    "Please manually set 'directed' to `True` or `False` to supress this error."
                )
            directed = edges["directed"][0]
            edges.drop("directed", axis=1, inplace=True)

        # Allow multiple edges among nodes if found.
        if multigraph is None:
            multigraph = 1 != edges[[source, target]].value_counts(ascending=True).unique()[-1]

        # Node and edge attributes to consider.
        node_attr = nodes.columns.tolist()\
                    if node_attr in (True, None) else (node_attr or [])

        edge_attr = [_ for _ in edges.columns if _ not in (source, target)]\
                    if edge_attr in (True, None) else (edge_attr or [])

        # Initialize graph object with determined type.
        G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()

        # Add nodes and edges to graph.
        G.add_nodes_from(list(
            zip(nodes.index, nodes[node_attr].to_dict(orient="records"))
            if node_attr else nodes.index
        ))

        G.add_edges_from(list(
            zip(edges[source], edges[target], edges[edge_attr].to_dict(orient="records"))
            if edge_attr else zip(edges[source], edges[target])
        ))

        # Assign weight to edges.
        if not multigraph:
            weight = pd\
                .DataFrame({
                    "source": edges[source],
                    "target": edges[target],
                    "weight": edges["weight"] if "weight" in edges.columns else 1
                })\
                .groupby(["source", "target"])\
                .sum("weight")\
                .squeeze("columns")

            if not weight.min() == 1 == weight.max():
                nx.set_edge_attributes(G, weight, "weight")

        return G

    @staticmethod
    def write_gdf(
        G: nx.Graph,
        file: Optional[Union[str, BufferedWriter, BytesIO, StringIO, TextIOWrapper]] = None,
        node_attr: Optional[Union[list, bool]] = True,
        edge_attr: Optional[Union[list, bool]] = True,
        encoding: str = "utf-8",
        errors: str = "strict",
    ) -> None:
        """
        Writes a NetworkX graph object to file path or object.

        :param G: NetworkX graph object.
        :param object file: Object or string containing path to GDF file. Optional. If ``None``
            (default), returns string representation of the file.
        :param node_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

           * If a ``list``, only the specified attributes will be considered.

           * If ``True``, all node attributes will be considered.

           * If ``False``, no node attributes will be considered.

        :param edge_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

           * If a ``list``, only the specified attributes will be considered.

           * If ``True``, all edge attributes will be considered.

           * If ``False``, no edge attributes will be considered.
        :param encoding: The encoding of the file. Default is ``'utf-8'``.
            A list of possible values can be found in the `Python documentation
            <https://docs.python.org/3/library/codecs.html#standard-encodings>`__.
        :param errors: The error handling scheme. Default is ``'strict'``.
            A list of possible values can be found in the `Python documentation
            <https://docs.python.org/3/library/codecs.html#codec-base-classes>`__.
        """
        types = {value.__name__: key for key, value in TYPES.items()}

        def get_type(series):
            """ Add attribute type to column names. """
            dtype = f"{types.get(series.dtype.__str__().lower().rstrip('0123456789'), 'VARCHAR')}"

            if dtype == "LONG" and all(-M <= m < M for m in (series.min(), series.max())):
                return "INT"

            if dtype == "DOUBLE" and series.astype(str).apply(str.__len__).max() <= 8:
                return "FLOAT"

            return dtype

        def get_columns(df):
            """ Add attribute type to column names. """
            return [f"{column} {get_type(df[column])}" for column in df.columns.tolist()]

        def get_nodes(G):
            """ Build node list with attributes. """
            nodes = pd\
                .DataFrame(
                    dict(G.nodes(data=True)).values(),
                    index=G.nodes(),
                )
            nodes.index.name = f"nodedef>name {get_type(nodes.index)}"

            if node_attr not in (True, None):
                nodes = nodes.loc[:, (node_attr if node_attr else [])]

            nodes.columns = get_columns(nodes)
            return nodes

        def get_edges(G):
            """ Build edge list with attributes. """
            edges = nx.to_pandas_edgelist(G)
            edges.columns = ["edgedef>node1", "node2"] + edges.columns[2:].tolist()

            if edge_attr not in (True, None):
                edges = edges.loc[:, edges.columns[:2].tolist() + (edge_attr if edge_attr else [])]

            if "directed" not in edges.columns and G.is_directed():
                edges["directed"] = G.is_directed()

            edges.columns = get_columns(edges)
            return edges

        def write_nodes(G, file):
            """ Write nodes to file. """
            return get_nodes(G).to_csv(file, index=True, encoding=encoding, errors=errors, quotechar="'", mode="w")

        def write_edges(G, file):
            """ Write edges to file. """
            return get_edges(G).to_csv(file, index=False, encoding=encoding, errors=errors, quotechar="'", mode="a")

        if file is None:
            return f"{write_nodes(G, file)}{write_edges(G, file)}"

        write_nodes(G, file)
        write_edges(G, file)

        if type(file) in (BytesIO, StringIO):
            file.seek(0)

        return file


read_gdf = GDF.read_gdf
write_gdf = GDF.write_gdf
