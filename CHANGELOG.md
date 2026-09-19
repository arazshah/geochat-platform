# Changelog

Notable changes to `geochat-sdk` and `geochat-kernel`. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each
package is versioned and released independently (see
`.github/workflows/publish-sdk.yml` / `publish-kernel.yml`), so entries
below are grouped and labeled per package.

## [Unreleased]

## geochat-sdk [1.0.1] - 2026-09-19

### Fixed

- **`VectorOut.from_geopandas()` crashed with `TypeError: Object of type
  Timestamp is not JSON serializable`** on any GeoDataFrame with a
  `datetime64` column - e.g. OSM `check_date`/`start_date` tags, which
  `geopandas.read_file()` auto-infers as datetime when every non-null
  value parses as a date. `gdf.to_json()` was called with no `default=`
  handler and no way for a caller to supply one.
  `VectorOut.from_geopandas()` now defaults to `str(...)` for
  non-JSON-native values (so `NaT` becomes `None` and a `Timestamp`
  becomes its ISO-ish string form), matching the equivalent conversion
  `smart_spatial_system`'s own `s3geo._to_geojson_dict()` already does,
  and now accepts `**kwargs` forwarded to `gdf.to_json()` so a caller can
  override `default` (or any other `to_json` keyword) themselves.

History before this file existed (through `geochat-sdk` 1.0.0 /
`geochat-kernel` 1.0.0) is not tracked here; see `git log` and each
package's PyPI release notes.
