import tensorflow as tf
from tensorflow import keras
from keras import layers, models
import numpy as np

class BaseClassifier(tf.keras.Model):
    def __init__(self, input_dim: int, output_dim: int):
        super(BaseClassifier, self).__init__()
        self.model=tf.keras.Sequential([
            layers.InputLayer(input_shape=(input_dim,)),
            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),
            layers.Dense(output_dim)
        ])

    def call(self, inputs, training=False):
        return self.model(inputs, training=training)
    
    def get_weights(self):
        return self.model.get_weights()
    
    def set_weights(self, weights):
        self.model.set_weights(weights)

if __name__ == "__main__":
    np.random.seed(42)
    tf.random.set_seed(42)

    input_dim = 20
    output_dim = 3

    model = BaseClassifier(input_dim=input_dim, output_dim=output_dim)
    model.summary()

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    X_train = np.random.randn(100, input_dim)
    y_train = np.random.randint(0, output_dim, size=(100,))

    X_test = np.random.randn(20, input_dim)
    y_test = np.random.randint(0, output_dim, size=(20,))

    model.fit(X_train, y_train, epochs=5, batch_size=16)

    test_loss, test_acc = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_acc:.4f}")