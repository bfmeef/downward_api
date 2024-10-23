from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def get_env_vars():
    pod_name = os.getenv('POD_NAME', 'Unknown POD')
    node_name = os.getenv('NODE_NAME', 'Unknown NODE')
    namespace = os.getenv('POD_NAMESPACE', 'Unknown NAMESPACE')
    return jsonify({
        "pod_name": pod_name,
        "node_name": node_name,
        "namespace": namespace
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

