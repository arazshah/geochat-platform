# geochat-platform

**A plugin-based kernel for geospatial AI.** A natural-language question goes in; the kernel parses it, routes it to the right spatial capability, plans the work as a DAG, runs it through plugins and returns one structured, map-ready response with a full execution trace.

The kernel has no geospatial or LLM dependencies of its own. Everything domain-specific, from buffering a layer to calling a routing API to asking an LLM for a plan, lives in plugins, so the same core can serve a city-search assistant, a remote-sensing workflow or an enterprise GIS backend.

> Status: v1.0.0, early stage. It grew out of my work on [Mapathon](https://mapathon.ir), a Persian geospatial assistant. MIT licensed.

---

## How a query flows

```text
"pharmacies within 500 m of Vanak Square"
        │
        ▼
 parse ─► enrich ─► route ─► plan ─► optimize ─► execute DAG ─► fuse ─► rank ─► build artifacts ─► compose
            │         │                                │
     semantic types   cascading router          plugins' step handlers
                      (keyword → smarter routers)
        │
        ▼
 GeoResponse: features, map layers, analytics, user message, trace, audit record
```

Every stage is a registry. Plugins register components into it, and the kernel picks the best candidate at run time:

| Stage | Registry | Built into the kernel |
|---|---|---|
| Parse / enrich | `query_parsers`, `parse_stages`, `semantic_enrichers` | contracts only |
| Route | `routers` | `KeywordRouter`, a free, deterministic default layer |
| Plan / optimize | `planners`, `plan_optimizers` | contracts only |
| Execute | `step_handlers`, `tools`, `providers`, `llms` | DAG executor, error boundary, hooks |
| Fuse / rank / compose | `fusions`, `rankers`, `artifact_builders`, `composers` | contracts only |

### The cascading router

Routing is layered so the cheap path runs first and smarter (possibly LLM-based) routers only take over when they are more confident:

- **`KeywordRouter`** is always registered. It scores each capability on keyword overlap, intent match, historical success rate and priority. Capabilities whose required inputs are not available, or that do not support the query language, are dropped before scoring.
- **Additional routers** from plugins declare their own `match_score` and win when they are more relevant.
- **`RouterConfig`** makes the cascade tunable without touching code: at confidence ≥ 0.85 a decision is accepted without an LLM, between 0.50 and 0.85 an LLM is optional, below 0.50 it is required, and a close race (gap < 0.10) calls the LLM even in the high zone. Signal weights and clarification behaviour live here too.

## Repository layout

```text
geochat-platform/
├── geochat-kernel/   # orchestration engine: contracts, models, registries, runtime, plugin loader
└── geochat-sdk/      # decorators and types for writing plugins in a few lines
```

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/arazshah/geochat-platform
cd geochat-platform
python -m venv .venv && source .venv/bin/activate
pip install -e ./geochat-sdk -e ./geochat-kernel
```

### Write a plugin

Any function decorated with `@capability` becomes a routable step. `auto_collect` bundles the module's capabilities into a plugin:

```python
# plugins/hello_geo.py
from geochat_sdk import capability, auto_collect

@capability(
    "distance_hint",
    keywords=["distance", "فاصله"],
    description="Answers distance questions",
)
def distance_hint(context=None) -> dict:
    return {"answer": "distance capability reached", "query": context.raw_text}

PLUGIN = auto_collect(id="hello_geo", description="Minimal example plugin")
```

Typed inputs and outputs (`VectorIn`, `VectorOut`, `RasterIn`, `RasterOut`) are converted to and from kernel artifacts for you; `VectorIn.to_geopandas()` gives you a GeoDataFrame when GeoPandas is installed.

### Run a query

```python
import asyncio
from geochat_kernel.runtime.app_container import KernelAppContainer
from geochat_kernel.bootstrap.plugin_loader import PluginLoader
from geochat_kernel.runtime.query_pipeline import QueryPipeline

async def main():
    container = KernelAppContainer()
    loaded = PluginLoader(container, plugins_folder="plugins").discover_and_register()
    print("plugins:", loaded.loaded_plugin_ids)          # ['hello_geo']

    await container.initialize_plugins()
    response = await QueryPipeline(container).run("distance from Azadi to Vanak")

    print(response.status)                                # success
    print([step.name for step in response.trace.steps])
    # ['parse', 'hook.on_query_parsed', 'route', 'plan', 'execute_plan',
    #  'execute.step_distance_hint', 'fusion.fusion_hello_geo', 'hook.on_response_composed']

asyncio.run(main())
```

## Plugin discovery

`PluginLoader` scans a folder for single-file plugins (`plugins/my_plugin.py`) or packages (`plugins/my_plugin/__init__.py`). A module can expose plugins as `PLUGIN = ...`, `PLUGINS = [...]`, `get_plugin()`, `get_plugins()`, or plain zero-argument `BasePlugin` subclasses. Load failures are collected in the result instead of crashing the kernel, and dependency order between plugins is resolved from each `PluginManifest` during `initialize_plugins()`.

Plugins are trusted Python code in this version. Heavy libraries such as Shapely, Rasterio or NumPy belong in plugins; the kernel never imports them.

## Author

Built by [Araz Shahkarami](https://github.com/arazshah) · [araz.me](https://araz.me)

## License

[MIT](LICENSE)
