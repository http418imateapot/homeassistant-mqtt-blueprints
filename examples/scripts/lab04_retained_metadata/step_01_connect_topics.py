import argparse

from examples.scripts.lab_common import actual, add_broker_arguments, announce, broker_config, connected_client, run_cli


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    add_broker_arguments(result)
    result.add_argument("--base-topic", default="homeassistant")
    result.add_argument("--discovery-prefix", default="homeassistant")
    result.add_argument("--seconds", type=float, default=3.0)
    return result


def run(config, base_topic: str, discovery_prefix: str) -> bool:
    announce(
        "01",
        "Connect and identify retained topics",
        "Confirm broker access and derive the two metadata subscriptions.",
        f"Connect and prepare {discovery_prefix}/+/mqtt_bridge/+/config plus {base_topic}/telemetry/capabilities/#.",
        "The broker accepts the connection and both wildcard filters are displayed.",
    )
    with connected_client(config):
        print(f"  Discovery: {discovery_prefix}/+/mqtt_bridge/+/config")
        print(f"  Capability: {base_topic}/telemetry/capabilities/#")
        actual(f"Connected to {config.host}:{config.port}; topic filters are ready.")
    return True


def main() -> int:
    args = parser().parse_args()
    return run_cli(lambda: run(broker_config(args), args.base_topic, args.discovery_prefix))


if __name__ == "__main__":
    raise SystemExit(main())