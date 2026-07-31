from examples.scripts.lab_common import actual, announce, broker_config, connected_client, publish_json, run_cli
from examples.scripts.lab03_allowlist_reject.step_01_build_scenarios import parser, scenarios


def run(config, topic: str) -> bool:
    announce(
        "02",
        "Publish and observe rejection",
        "Send the invalid scenarios and identify where rejection evidence appears.",
        f"Publish all scenarios to {topic}; then inspect Home Assistant Settings > System > Logs.",
        "The receiver writes system_log warnings and does not publish an ack or result topic.",
    )
    with connected_client(config) as client:
        for name, _, payload in scenarios():
            publish_json(client, topic, payload)
            print(f"  published scenario: {name}")
    actual("Published 3 scenarios. MQTT silence is expected; inspect Home Assistant system logs.")
    return True


def main() -> int:
    args = parser().parse_args()
    return run_cli(lambda: run(broker_config(args), args.topic))


if __name__ == "__main__":
    raise SystemExit(main())