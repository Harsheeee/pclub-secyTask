import requests
import numpy as np
import base64
import pickle
from models.base_model import BaseClassifier
from clients.trainer import ClientTrainer
from utils.partitioning import load_and_partition_dataset
from datetime import datetime
import tensorflow as tf

class Client:
    def __init__(self, group_name, num_clients):
        self.group_name = group_name
        self.num_clients = num_clients
        self.client_data, self.val_data, self.test_data = load_and_partition_dataset(f'data/{group_name}.csv', f'{group_name}', num_clients=num_clients)
        self.X_val, self.y_val = self.val_data
        self.X_test, self.y_test = self.test_data
        self.input_dim = self.client_data[0][0].shape[1]
        self.output_dim = len(np.unique(self.client_data[0][1]))
        self.server_url = 'http://127.0.0.1:5000'

    def serialize_weights(self,weights):
        return base64.b64encode(pickle.dumps(weights)).decode('utf-8')

    def deserialize_weights(self,encoded):
        return pickle.loads(base64.b64decode(encoded.encode('utf-8')))
    
    def simulate(self):
        for client_id in range(self.num_clients):
            print(f"\n--- Client {client_id} ---")

            X_train, y_train = self.client_data[client_id]

            res = requests.post(f'{self.server_url}/get_weights', json={'group_name': self.group_name})
            data = res.json()
            if data['status'] != 'success':
                raise Exception("Failed to get weights from server")

            global_weights = self.deserialize_weights(data['weights'])

            model = BaseClassifier(input_dim=self.input_dim, output_dim=self.output_dim)
            model.build(input_shape=(None, self.input_dim))
            model.set_weights(global_weights)
            model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
            global_loss, global_accuracy= model.evaluate(self.X_val, self.y_val)


            trainer = ClientTrainer(
                client_id=client_id,
                model=model,
                train_data=(X_train, y_train),
                val_data=(self.X_val, self.y_val),
                learning_rate=0.01,
                epochs=5,
                batch_size=32
            )

            print("Training locally...")
            trainer.train()
            metrics = trainer.evaluate()
            print(f"Validation: Loss={metrics['loss']:.4f}, Acc={metrics['accuracy']:.4f}")
            requests.post(f'{self.server_url}/log_metrics', json={
            'group_name': self.group_name,
            'metrics': {
                'client_id': client_id+1,
                'timestamp': datetime.now().isoformat(),
                'accuracy': metrics['accuracy'],
                'loss': metrics['loss'],
                'global_accuracy': global_accuracy,
                'global_loss': global_loss
            }
        })

            delta = trainer.get_weight_deltas(global_weights)
            encoded_delta = self.serialize_weights(delta)
            res = requests.post(f'{self.server_url}/submit_update', json={
                'group_name': self.group_name,
                'delta': encoded_delta
            })
            print("Update submission:", res.json())

        print("\n--- Aggregating updates on server ---")
        res = requests.post(f'{self.server_url}/aggregate', json={'group_name': self.group_name})
        print(res.json())
    
