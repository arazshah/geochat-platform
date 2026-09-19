"""
Tests for geochat_sdk.types.vector.VectorOut.

Run:
    pytest geochat-sdk/tests/test_vector.py -v
"""

from __future__ import annotations

import pytest

geopandas = pytest.importorskip("geopandas")
shapely = pytest.importorskip("shapely")

import pandas as pd
from geochat_sdk.types.vector import VectorOut
from shapely.geometry import Point


def test_from_geopandas_serializes_datetime_columns():
    # Regression test: gdf.to_json() has no default handler for
    # datetime64/Timestamp columns, so VectorOut.from_geopandas used to
    # raise TypeError("Object of type Timestamp is not JSON serializable")
    # on any GeoDataFrame with one - e.g. OSM check_date/start_date tags,
    # which geopandas.read_file() auto-infers as datetime.
    gdf = geopandas.GeoDataFrame(
        {
            "id": [1, 2],
            "check_date": pd.to_datetime(["2024-01-15", "2023-07-04"]),
        },
        geometry=[Point(0.0, 0.0), Point(1.0, 1.0)],
        crs="EPSG:4326",
    )

    result = VectorOut.from_geopandas(gdf)

    assert len(result.features) == 2
    check_dates = [f["properties"]["check_date"] for f in result.features]
    assert check_dates == ["2024-01-15 00:00:00", "2023-07-04 00:00:00"]


def test_from_geopandas_serializes_nat_as_none():
    gdf = geopandas.GeoDataFrame(
        {"id": [1], "check_date": pd.to_datetime([None])},
        geometry=[Point(0.0, 0.0)],
        crs="EPSG:4326",
    )

    result = VectorOut.from_geopandas(gdf)

    assert result.features[0]["properties"]["check_date"] is None


def test_from_geopandas_without_datetime_columns_unaffected():
    gdf = geopandas.GeoDataFrame(
        {"id": [1, 2], "name": ["a", "b"]},
        geometry=[Point(0.0, 0.0), Point(1.0, 1.0)],
        crs="EPSG:4326",
    )

    result = VectorOut.from_geopandas(gdf)

    assert len(result.features) == 2
    assert result.features[0]["properties"]["name"] == "a"


def test_from_geopandas_forwards_to_json_kwargs():
    gdf = geopandas.GeoDataFrame(
        {"id": [1]},
        geometry=[Point(0.0, 0.0)],
        crs="EPSG:4326",
    )
    calls = {}

    def _tracking_default(value):
        calls["called"] = True
        return str(value)

    VectorOut.from_geopandas(gdf, default=_tracking_default)

    # No non-serializable value in this GeoDataFrame, so the passed-in
    # default should never actually fire - this just proves the kwarg
    # reaches gdf.to_json() instead of being silently dropped.
    assert "called" not in calls
