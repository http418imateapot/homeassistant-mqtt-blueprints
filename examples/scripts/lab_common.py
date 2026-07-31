from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
import threading
import time
from typing import Callable, Iterator, Sequence

import paho.mqtt.client as mqtt


class LabError(RuntimeError):
    """An expected lab failure that should be shown without a traceback."""


@dataclass(frozen=True)
class BrokerConfig:
    host: str = "127.0.0.1"
    port: int = 1883
    username: str | None = None
    password: str | None = None


@dataclass(frozen=True)
class ReceivedMessage:
    topic: str
    payload: bytes
    retained: bool


def add_broker_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default=os.getenv("MQTT_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
    parser.add_argument("--username", default=os.getenv("MQTT_USERNAME"))
    parser.add_argument("--password", default=os.getenv("MQTT_PASSWORD"))


def broker_config(args: argparse.Namespace) -> BrokerConfig:
    return BrokerConfig(args.host, args.port, args.username, args.password)


def announce(number: str, title: str, purpose: str, execution: str, expected: str) -> None:
    print(f"\nStep {number}: {title}")
    print(f"Purpose: {purpose}")
    print(f"Execution: {execution}")
    print(f"Expected result: {expected}")


def actual(message: str) -> None:
    print(f"Actual result: {message}")


@contextmanager
def connected_client(
    config: BrokerConfig,
    on_message: Callable[[mqtt.Client, object, mqtt.MQTTMessage], None] | None = None,
    timeout: float = 5.0,
) -> Iterator[mqtt.Client]:
    connected = threading.Event()
    connection_result: list[str] = []
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if config.username:
        client.username_pw_set(config.username, config.password)

    def handle_connect(
        client: mqtt.Client,
        userdata: object,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        connection_result.append(str(reason_code))
        connected.set()

    client.on_connect = handle_connect
    if on_message is not None:
        client.on_message = on_message

    try:
        client.connect(config.host, config.port, keepalive=30)
        client.loop_start()
        if not connected.wait(timeout):
            raise LabError(
                f"MQTT connection to {config.host}:{config.port} timed out. "
                "Start Mosquitto and verify host, port, firewall, and credentials."
            )
        if connection_result != ["Success"]:
            raise LabError(
                f"MQTT broker rejected the connection: {connection_result[0]}. "
                "Verify the username and password."
            )
        yield client
    except (ConnectionError, OSError) as exc:
        raise LabError(
            f"Cannot connect to MQTT broker at {config.host}:{config.port}: {exc}. "
            "Start Mosquitto or pass --host, --port, --username, and --password."
        ) from None
    finally:
        try:
            client.disconnect()
        finally:
            client.loop_stop()


def collect_messages(
    config: BrokerConfig, subscriptions: Sequence[str], seconds: float
) -> list[ReceivedMessage]:
    messages: list[ReceivedMessage] = []

    def handle_message(
        client: mqtt.Client, userdata: object, message: mqtt.MQTTMessage
    ) -> None:
        messages.append(ReceivedMessage(message.topic, message.payload, message.retain))

    with connected_client(config, on_message=handle_message) as client:
        for topic in subscriptions:
            result, _ = client.subscribe(topic, qos=1)
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise LabError(f"Could not subscribe to {topic}; MQTT result={result}.")
        time.sleep(seconds)
    return messages


def publish_json(client: mqtt.Client, topic: str, payload: dict) -> None:
    info = client.publish(topic, json.dumps(payload), qos=1, retain=False)
    info.wait_for_publish(timeout=5.0)
    if not info.is_published():
        raise LabError(f"Publish to {topic} did not complete within 5 seconds.")


def run_cli(action: Callable[[], bool]) -> int:
    try:
        return 0 if action() else 1
    except LabError as exc:
        actual(f"FAILED - {exc}")
        return 1
    except Exception as exc:
        actual(f"FAILED - unexpected {type(exc).__name__}: {exc}")
        return 1


def run_notebook(action: Callable[[], bool]) -> bool:
    try:
        return action()
    except LabError as exc:
        actual(f"SKIPPED - {exc}")
        return False
    except Exception as exc:
        actual(f"SKIPPED - unexpected {type(exc).__name__}: {exc}")
        return False