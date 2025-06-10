from airflow.providers.google.cloud.hooks.gcs import GCSHook
from datetime import datetime, timezone
import pandas as pd
import json
import io


def raw_transformation(**kwargs):
    # Read parameters from DAG
    bronze_bucket = kwargs["dag"].params["bronze_bucket"]
    silver_bucket = kwargs["dag"].params["silver_bucket"]

    gcs_hook = GCSHook()

    # Get the latest file from bronze bucket
    list_of_files = gcs_hook.list(bronze_bucket, prefix="raw/")
    if not list_of_files:
        raise ValueError("No files found in bronze")

    latest_file = sorted(list_of_files)[-1]
    json_data = json.loads(
        gcs_hook.download(bronze_bucket, latest_file).decode("utf-8")
    )

    def flatten_json(data):

        # Flatten using pandas.json_normalize
        df = pd.json_normalize(json_data["network"]["stations"], sep="_")

        # Rename flattened keys to match your schema
        df = df.rename(
            columns={
                "id": "station_id",
                "latitude": "latitude",
                "longitude": "longitude",
                "timestamp": "timestamp",
                "free_bikes": "free_bikes",
                "empty_slots": "empty_slots",
                "extra.uid": "extra_uid",
                "extra.renting": "renting",
                "extra.returning": "returning",
                "extra.has_ebikes": "has_ebikes",
                "extra.ebikes": "ebikes",
            }
        )

        # Add network-level metadata
        df["network_id"] = json_data["network"]["id"]
        df["network_name"] = json_data["network"]["name"]

        return df

    df = flatten_json(json_data)

    # add snapshot time
    snapshot_time = datetime.now(timezone.utc)
    df["snapshot_time"] = snapshot_time

    try:
        if df["timestamp"].dtype.kind in "iuf":
            df["timestamp"] = pd.to_datetime(
                df["timestamp"].astype("int64") / 1000,
                unit="ns",
                utc=True,
            )
        else:
            df["timestamp"] = (
                df["timestamp"]
                .astype(str)
                .str.strip()
                .str.replace("Z", "", regex=False)
                .replace({"": None, "None": None, "nan": None})
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

        df = df[df["timestamp"].between("2000-01-01", "2100-01-01")]
        df["timestamp"] = df["timestamp"].astype("int64") // 1000

    except Exception as e:
        raise ValueError(f"Timestamp conversion failed: {str(e)}")

    numeric_cols = ["free_bikes", "empty_slots", "ebikes", "latitude", "longitude"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    bool_cols = ["has_ebikes", "renting", "returning"]
    df[bool_cols] = df[bool_cols].astype(bool)

    df.fillna(
        {
            "free_bikes": 0,
            "empty_slots": 0,
            "ebikes": 0,
            "latitude": 0.0,
            "longitude": 0.0,
        },
        inplace=True,
    )
    expected_columns = [
        "network_id",
        "network_name",
        "station_id",
        "latitude",
        "longitude",
        "timestamp",
        "free_bikes",
        "empty_slots",
        "extra_uid",
        "renting",
        "returning",
        "has_ebikes",
        "ebikes",
        "snapshot_time",
    ]
    df = df.reindex(columns=expected_columns)
    parquet_buffer = io.BytesIO()
    df.to_parquet(
        parquet_buffer,
        index=False,
        coerce_timestamps="us",
        allow_truncated_timestamps=True,
    )

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Upload to silver bucket
    gcs_hook.upload(
        bucket_name=silver_bucket,
        object_name="citi-bike/latest_data.parquet",
        data=parquet_buffer.getvalue(),
    )

    gcs_hook.upload(
        bucket_name=silver_bucket,
        object_name=f"citi-bike/history/data_{timestamp_str}.parquet",
        data=parquet_buffer.getvalue(),
    )
