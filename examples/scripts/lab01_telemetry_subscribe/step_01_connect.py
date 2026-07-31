import argparse

from examples.scripts.lab_common import (
    BrokerConfig,
    actual,
    add_broker_arguments,
    announce,
    broker_config,
    connected_client,
    run_cli,
)


def run(config: BrokerConfig) -> bool:
    announce(
        "01",
        "Connect to the broker",
        "Confirm that the configured MQTT endpoint is reachable.",
        f"Open an MQTT connection to {config.host}:{config.port}.",
        "The broker accepts the connection.",
    )
    with connected_client(config):
        actual(f"Connected to {config.host}:{config.port}.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_broker_arguments(parser)
    parser.add_argument("--base-topic", default="homeassistant")
    parser.add_argument("--seconds", type=float, default=10.0)
    args = parser.parse_args()
    return run_cli(lambda: run(broker_config(args)))


if __name__ == "__main__":
    raise SystemExit(main())