from examples.scripts.lab_common import actual, announce, broker_config, connected_client, publish_json, run_cli
from examples.scripts.lab02_command_v2.step_01_build_validate import build_commands, entities_from_args, parser


def run(config, topic: str, entities: dict[str, str]) -> bool:
    announce(
        "02",
        "Publish v2 commands",
        "Send the six validated envelopes to the receiver command topic.",
        f"Publish each JSON object to {topic} with QoS 1.",
        "The receiver dispatches only commands that pass schema, domain, target-domain, and area checks.",
    )
    commands = build_commands(entities)
    with connected_client(config) as client:
        for command in commands:
            publish_json(client, topic, command)
            print(f"  published {command['service']} -> {command['target']['entity_id'][0]}")
    actual(f"Published {len(commands)} commands. Check Home Assistant services and system logs.")
    return True


def main() -> int:
    args = parser().parse_args()
    return run_cli(lambda: run(broker_config(args), args.topic, entities_from_args(args)))


if __name__ == "__main__":
    raise SystemExit(main())