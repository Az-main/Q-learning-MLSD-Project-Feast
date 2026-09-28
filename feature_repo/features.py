"""Feast entity, data source and feature view definitions."""

from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float64, Int64

store_item = Entity(name="store_item", join_keys=["store_item_id"], value_type=ValueType.INT64)

demand_source = FileSource(
    name="demand_source",
    path="data/demand_features.parquet",
    timestamp_field="event_timestamp",
)

demand_features = FeatureView(
    name="demand_features",
    entities=[store_item],
    ttl=timedelta(days=0),
    schema=[
        Field(name="day_of_week", dtype=Int64),
        Field(name="rolling_demand", dtype=Float64),
        Field(name="demand_trend", dtype=Int64),
    ],
    online=True,
    source=demand_source,
)
