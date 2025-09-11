from flask import Flask, send_from_directory, jsonify, request
import os

app = Flask(__name__, static_folder="../app", static_url_path="")

@app.route("/")
def serve_index():
    return send_from_directory("../app", "index.html")

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": f"Hello from the back end!! (server/server.py)"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
