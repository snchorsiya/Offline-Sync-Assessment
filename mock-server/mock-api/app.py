from flask import Flask, request, jsonify
from threading import Lock
from uuid import uuid4

app = Flask(__name__)

surveys = {}
lock = Lock()


@app.route("/sync-survey", methods=["POST"])
def sync_survey():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    required_fields = [
        "sync_id",
        "device_id",
        "worker_id",
        "local_id",
        "survey_data"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    sync_id = data["sync_id"]

    with lock:

        # Idempotency check
        if sync_id in surveys:
            existing = surveys[sync_id]

            return jsonify({
                "status": "success",
                "message": "Survey already synchronized",
                "server_id": existing["server_id"],
                "sync_id": existing["sync_id"],
                "local_id": existing["local_id"],
                "device_id": existing["device_id"]
            }), 200

        # Create a new server-side ID
        server_id = f"srv-{uuid4().hex[:8]}"

        record = {
            "server_id": server_id,
            "sync_id": sync_id,
            "device_id": data["device_id"],
            "worker_id": data["worker_id"],
            "local_id": data["local_id"],
            "survey_data": data["survey_data"],
            "updated_at": data.get("updated_at")
        }

        surveys[sync_id] = record

    return jsonify({
        "status": "success",
        "message": "Survey synchronized successfully",
        "server_id": server_id,
        "sync_id": sync_id,
        "local_id": data["local_id"],
        "device_id": data["device_id"]
    }), 201


@app.route("/sync-survey", methods=["GET"])
def get_surveys():

    return jsonify({
        "status": "success",
        "count": len(surveys),
        "surveys": list(surveys.values())
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)