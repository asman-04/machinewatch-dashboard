import json, os, threading
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template
import paho.mqtt.client as mqtt

HOST = os.environ.get("MQTT_HOST", "127.0.0.1")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
USERNAME = os.environ.get("MQTT_USERNAME", "")
PASSWORD = os.environ.get("MQTT_PASSWORD", "")
TLS = os.environ.get("MQTT_TLS", "false").lower() == "true"
app = Flask(__name__)
lock = threading.Lock()
latest = {"telemetry": None, "alerts": []}

def on_connect(client, userdata, flags, reason_code, properties):
    if not reason_code.is_failure:
        client.subscribe("internship/factory/node01/#")
        print("Factory dashboard connected to MQTT.")
    else:
        print("MQTT connection failed:", reason_code)

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    print(f"MQTT RECEIVED: topic={msg.topic}, payload={payload}", flush=True)
    now = datetime.now(timezone.utc).isoformat()
    try: data = json.loads(payload)
    except Exception: data = {"message": payload}
    with lock:
        if msg.topic.endswith("/alerts"):
            latest["alerts"].insert(0, {"time": now, "message": payload})
            latest["alerts"] = latest["alerts"][:12]
        else:
            latest["telemetry"] = {"time": now, "data": data}

def mqtt_worker():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="factory-dashboard"
    )

    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)

    if TLS:
        client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    client.on_disconnect = lambda client, userdata, disconnect_flags, reason_code, properties: print(
        f"MQTT disconnected: {reason_code}", flush=True
    )

    try:
        print(
            f"Connecting to MQTT broker {HOST}:{PORT}; TLS={TLS}",
            flush=True
        )
        client.connect(HOST, PORT, 45)
        client.loop_forever()
    except Exception as exc:
        print(f"MQTT worker error: {type(exc).__name__}: {exc}", flush=True).0", port=int(os.environ.get("PORT", "5000")), debug=False)
