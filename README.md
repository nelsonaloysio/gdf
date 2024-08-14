# networkx-gdf

Python package to read and write NetworkX graphs as GDF (Graph Data Format).

GDF is a compact file format originally implemented by [GUESS](http://graphexploration.cond.org). Although the software itself is not anymore maintained, the format is still supported by active open-source projects such as [Gephi](https://gephi.org/) (see details [here](https://gephi.org/users/supported-graph-formats/gdf-format/)).

## Requirements

* **Python>=3.7**
* networkx>=2.1
* pandas>=1.1.0

## Install

Package is available to install on [PyPI](https://pypi.org/project/networkx-gdf/):

```bash
$ pip install networkx-gdf
```

## Usage

The following is an example covering the package's functionality:

```python
from networkx_gdf import read_gdf, write_gdf

# Builds NetworkX graph object from file.
G = read_gdf("input_file.gdf")

# Writes NetworkX graph object to file.
write_gdf(G, "output_file.gdf")
```

For detailed information on usage, please refer to its [official documentation](https://networkx-gdf.readthedocs.io).