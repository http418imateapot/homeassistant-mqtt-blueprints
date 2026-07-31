import json

from examples.scripts.lab_common import LabError, actual, announce, broker_config, collect_messages, run_cli
from examples.scripts.lab04_retained_metadata.step_01_connect_topics import parser


def run(config, base_topic: str, discovery_prefix: str, seconds: float) -> bool:
    discovery_filter = f"{discovery_prefix}/+/mqtt_bridge/+/config"
    capability_filter = f"{base_topic}/telemetry/capabilities/#"
    announce(
        "02",
        "Read and validate retained metadata",
        "Inspect discovery config and machine-readable read/write contracts.",
        f"Subscribe to both filters for {seconds:g} seconds and parse retained JSON messages.",
        "Discovery has state/availability topics; capability metadata has entity, domain, area, read_contract, and write_contract.",
    )
    messages = collect_messages(config, [discovery_filter, capability_filter], seconds)
    discovery_count = 0
    capability_count = 0
    for message in messages:
        try:
            payload = json.loads(message.payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LabError(f"Invalid JSON on {message.topic}: {exc}") from None
        if message.topic.startswith(f"{base_topic}/telemetry/capabilities/"):
            required = {"entity", "domain", "area", "read_contract", "write_contract"}
            if not required <= payload.keys():
                raise LabError(f"Capability payload on {message.topic} is missing {sorted(required - payload.keys())}")
            if not {"state_topic", "metric", "payload_schema"} <= payload["read_contract"].keys():
                raise LabError(f"read_contract on {message.topic} is incomplete")
            capability_count += 1
            print(f"  capability {payload['entity']}: write schema={payload['write_contract'].get('schema')}")
        else:
            required = {"unique_id", "state_topic", "availability_topic", "value_template", "object_id"}
            if not required <= payload.keys():
                raise LabError(f"Discovery payload on {message.topic} is missing {sorted(required - payload.keys())}")
            discovery_count += 1
            print(f"  discovery {payload['object_id']}: state_topic={payload['state_topic']}")
        if not message.retained:
            raise LabError(f"Metadata delivered on {message.topic} was not marked retained")
    if discovery_count == 0 or capability_count == 0:
        raise LabError(
            "Both metadata types were not received. Enable the uploader, select entities, and wait for a heartbeat run."
        )
    actual(f"Validated {discovery_count} discovery and {capability_count} capability message(s).")
    return True


def main() -> int:
    args = parser().parse_args()
    return run_cli(lambda: run(broker_config(args), args.base_topic, args.discovery_prefix, args.seconds))


if __name__ == "__main__":
    raise SystemExit(main())