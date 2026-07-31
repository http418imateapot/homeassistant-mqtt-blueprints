import argparse
from datetime import datetime
import json

from examples.scripts.lab_common import (
    BrokerConfig,
    LabError,
    actual,
    add_broker_arguments,
    announce,
    broker_config,
    collect_messages,
    run_cli,
)


REQUIRED_FIELDS = {"timestamp", "area", "trigger_reason", "sample_type", "telemetries"}
RECORD_FIELDS = {"name", "value", "entity", "friendly_name", "domain", "unit"}


def validate_payload(payload: bytes) -> str:
    try:
        data = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LabError(f"Telemetry is not valid JSON: {exc}") from None
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise LabError(f"Telemetry is missing fields: {sorted(missing)}")
    if data["sample_type"] not in {"event", "heartbeat"}:
        raise LabError("sample_type must be event or heartbeat")
    expected_reason = "heartbeat" if data["sample_type"] == "heartbeat" else "state_changed"
    if data["trigger_reason"] != expected_reason:
        raise LabError(
            f"sample_type={data['sample_type']} requires trigger_reason={expected_reason}"
        )
    if not isinstance(data["telemetries"], list):
        raise LabError("telemetries must be a JSON array")
    for index, record in enumerate(data["telemetries"]):
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            raise LabError(f"telemetries[{index}] does not use the fixed record fields")
    if data["area"] is not None and not isinstance(data["area"], str):
        raise LabError("area must be a string or null")
    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    return data["sample_type"]


def run(config: BrokerConfig, base_topic: str, seconds: float) -> bool:
    topic = f"{base_topic}/telemetry/#"
    announce(
        "02",
        "Subscribe and validate telemetry",
        "Read per-domain telemetry and distinguish event updates from heartbeat snapshots.",
        f"Subscribe to {topic} for {seconds:g} seconds and validate each per-domain JSON payload.",
        "Every telemetry envelope and record has the blueprint fields; sample_type matches trigger_reason.",
    )
    messages = collect_messages(config, [topic], seconds)
    counts = {"event": 0, "heartbeat": 0}
    for message in messages:
        suffix = message.topic.removeprefix(f"{base_topic}/telemetry/")
        if "/" in suffix or suffix in {"availability", "capabilities"}:
            continue
        sample_type = validate_payload(message.payload)
        counts[sample_type] += 1
        print(f"  {message.topic}: valid {sample_type} payload")
    if sum(counts.values()) == 0:
        raise LabError(
            "No per-domain telemetry arrived. Enable the uploader, select entities, change a state, "
            "or wait for its heartbeat interval."
        )
    actual(f"Validated {counts['event']} event and {counts['heartbeat']} heartbeat payload(s).")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_broker_arguments(parser)
    parser.add_argument("--base-topic", default="homeassistant")
    parser.add_argument("--seconds", type=float, default=10.0)
    args = parser.parse_args()
    return run_cli(lambda: run(broker_config(args), args.base_topic, args.seconds))


if __name__ == "__main__":
    raise SystemExit(main())