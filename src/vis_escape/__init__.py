from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("vis_escape")
except PackageNotFoundError:
    __version__ = "0.0.dev"
