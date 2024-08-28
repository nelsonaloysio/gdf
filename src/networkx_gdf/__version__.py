__version__ = ""
try:
    from importlib.metadata import version
    __version__ = version("networkx_gdf")
except ImportError: # <= Python 3.7
    from pkg_resources import get_distribution
    __version__ = get_distribution("networkx_gdf").version
