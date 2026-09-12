# geochat_kernel/__init__.py
from __future__ import annotations

# Must match [project].version in ../pyproject.toml - that file is the
# source of truth for what PyPI publishes, and a mismatch here makes every
# installation report the wrong runtime version to consumers.
__version__ = "1.0.0"

from geochat_kernel.bootstrap import (
    PluginLoadFailure,
    PluginLoader,
    PluginLoadResult,
    load_plugins_from_folder,
)
from geochat_kernel.runtime import (
    ExecutionContext,
    KernelAppContainer,
    QueryPipeline,
    UserLocation,
)

__all__ = [
    "__version__",
    "PluginLoadFailure",
    "PluginLoader",
    "PluginLoadResult",
    "load_plugins_from_folder",
    "ExecutionContext",
    "KernelAppContainer",
    "QueryPipeline",
    "UserLocation",
]
