import requests
import numpy as np
from models.base_model import BaseClassifier
from clients.trainer import ClientTrainer
from utils.partitioning import load_and_partition_dataset
from server.app import serialize_weights, deserialize_weights
from datetime import datetime

group_name = 'smoking'
server_url = 'http://127.0.0.1:5000'
num_clients = 3

client_data, val_data, test_data = load_and_partition_dataset('data/smoking.csv', 'smoking', num_clients=num_clients)
X_val, y_val = val_data
X_test, y_test = test_data
input_dim = client_data[0][0].shape[1]
output_dim = len(np.unique(client_data[0][1]))

for client_id in range(num_clients):
    print(f"\n--- Client {client_id} ---")

    X_train, y_train = client_data[client_id]
    res = requests.post(f'{server_url}/register', json={
        'client_id': client_id,
        'group_name': group_name
    })
    print("Registration:", res.json())

    res = requests.post(f'{server_url}/get_weights', json={'group_name': group_name})
    data = res.json()
    if data['status'] != 'success':
        raise Exception("Failed to get weights from server")
    
    global_weights = deserialize_weights(data['weights'])

    model = BaseClassifier(input_dim=input_dim, output_dim=output_dim)
    model.build(input_shape=(None, input_dim))
    model.set_weights(global_weights)

    trainer = ClientTrainer(
        client_id=client_id,
        model=model,
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        learning_rate=0.01,
        epochs=5,
        batch_size=32
    )
    print("Training locally...")
    trainer.train()
    metrics = trainer.evaluate()
    print(f"Validation: Loss={metrics['loss']:.4f}, Acc={metrics['accuracy']:.4f}")
    requests.post(f'{server_url}/log_metrics', json={
    'group_name': group_name,
    'metrics': {
        'client_id': client_id+1,
        'timestamp': datetime.now().isoformat(),
        'accuracy': metrics['accuracy'],
        'loss': metrics['loss']
    }
})
    delta = trainer.get_weight_deltas(global_weights)
    encoded_delta = serialize_weights(delta)
    res = requests.post(f'{server_url}/submit_update', json={
        'group_name': group_name,
        'delta': encoded_delta
    })
    print("Update submission:", res.json())

print("\n--- Aggregating updates on server ---")
res = requests.post(f'{server_url}/aggregate', json={'group_name': group_name})
print(res.json())
