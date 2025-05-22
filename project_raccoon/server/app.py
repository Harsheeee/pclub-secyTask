from flask import Flask, request, jsonify
from server.groups import training_groups
import numpy as np
import base64
import pickle
from flask_cors import CORS
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
from server.simulate import Client
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)
bcrypt= Bcrypt(app)
jwt= JWTManager(app)
app.config['SECRET_KEY']= 'no_idea_what_to_put_here'
app.config['JWT_SECRET_KEY'] = 'no_idea_here_either'
users = {}

def serialize_weights(weights):
    """Convert numpy weights to a base64 string."""
    return base64.b64encode(pickle.dumps(weights)).decode('utf-8')

def deserialize_weights(encoded):
    """Convert base64 string back to numpy weights."""
    return pickle.loads(base64.b64decode(encoded.encode('utf-8')))

@app.route('/')
def home():
    return "Welcome to Project Raccoon API! Use /register or other endpoints."

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    group_name = data['group_name']
    num_clients = data['num_clients']
    clientSim = Client(group_name, num_clients)
    clientSim.simulate()

    return jsonify({"status": "success", "message": f"Client added to group {group_name}"})

@app.route('/get_weights', methods=['POST'])
def get_weights():
    data = request.json
    group_name = data['group_name']

    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400

    weights = training_groups[group_name].get_global_weights()
    if weights is None:
        return jsonify({"status": "error", "message": "Model not yet initialized"}), 400

    encoded_weights = serialize_weights(weights)
    return jsonify({"status": "success", "weights": encoded_weights})

@app.route('/submit_update', methods=['POST'])
def submit_update():
    data = request.json
    group_name = data['group_name']
    delta = deserialize_weights(data['delta'])

    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400

    training_groups[group_name].add_delta(delta)
    return jsonify({"status": "success", "message": "Delta received"})

@app.route('/aggregate', methods=['POST'])
def aggregate_updates():
    data = request.json
    group_name = data['group_name']

    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400

    deltas = training_groups[group_name].get_all_deltas()
    if not deltas:
        return jsonify({"status": "error", "message": "No updates to aggregate"}), 400

    avg_delta = [np.mean([d[i] for d in deltas], axis=0) for i in range(len(deltas[0]))]

    global_weights = training_groups[group_name].get_global_weights()
    new_weights = [w + dw for w, dw in zip(global_weights, avg_delta)]

    training_groups[group_name].set_global_weights(new_weights)
    training_groups[group_name].clear_deltas()

    return jsonify({"status": "success", "message": "Global model updated"})

@app.route('/metrics', methods=['GET'])
def get_metrics():
    group_name = request.args.get('group_name')
    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400

    metrics = training_groups[group_name].metrics if hasattr(training_groups[group_name], 'metrics') else []
    return jsonify({"status": "success", "metrics": metrics})


@app.route('/log_metrics', methods=['POST'])
def log_metrics():
    data = request.json
    group_name = data['group_name']
    metrics = data['metrics']

    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400

    training_groups[group_name].add_metric(metrics)
    return jsonify({"status": "success", "message": "Metrics logged"})

@app.route('/exit', methods=['POST'])
def exit():
    data = request.json
    group_name = data.get('group_name')

    if group_name not in training_groups:
        return jsonify({"status": "error", "message": "Invalid group"}), 400
    
    training_groups[group_name].clear_deltas()
    return jsonify({"status": "success", "message": f"Client exited group {group_name}"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    if username in users:
        return jsonify({"status": "error", "message": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users[username] = hashed_password
    return jsonify({"status": "success", "message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    if username not in users:
        return jsonify({"status": "error", "message": "User not found"}), 400

    hashed_password = users[username]
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"status": "error", "message": "Invalid password"}), 400

    access_token = create_access_token(identity=username)
    return jsonify({"status": "success", "access_token": access_token})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"status": "success", "message": f"Welcome {current_user}!"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
