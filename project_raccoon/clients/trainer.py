import tensorflow as tf
import numpy as np

class ClientTrainer:
    def __init__(self, client_id, model, train_data, val_data, learning_rate=0.01, epochs=5, batch_size=32):
        self.client_id = client_id
        self.model = model
        self.train_data = train_data
        self.val_data = val_data
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = tf.keras.optimizers.Adam(learning_rate)
        self.loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        self.train_acc = tf.keras.metrics.SparseCategoricalAccuracy()
        self.val_acc = tf.keras.metrics.SparseCategoricalAccuracy()

    def train(self):
        x_train, y_train = self.train_data
        x_val, y_val = self.val_data
        history = self.model.fit(
            x_train, y_train,
            validation_data=(x_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=0
        )
        return history.history

    def get_weight_deltas(self, global_weights, noise_std=0.01):
        deltas = []
        local_weights = self.model.get_weights()

        for gw, lw in zip(global_weights, local_weights):
            delta = lw - gw
            noise = np.random.normal(0, noise_std, size=delta.shape)
            delta_noised = delta + noise
            deltas.append(delta_noised.astype(np.float32))
        return deltas

    def evaluate(self):
        x_val, y_val = self.val_data
        loss, acc = self.model.evaluate(x_val, y_val, verbose=0)
        return {'loss': loss, 'accuracy': acc}
