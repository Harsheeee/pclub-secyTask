from models.base_model import BaseClassifier
from datetime import datetime
class TrainingGroup:
    def __init__(self, group_name):
        self.group_name = group_name
        self.clients = set()
        self.global_weights = None
        self.deltas_buffer = []
        self.metrics = []

    def add_client(self, client_id):
        self.clients.add(client_id)

    def set_global_weights(self, weights):
        self.global_weights = weights

    def get_global_weights(self):
        return self.global_weights
    
    def set_global_metric(self, accuracy: float, loss: float):
        self.global_metric = {
            "accuracy": accuracy,
            "loss": loss,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_global_metric(self):
        return self.global_metric if hasattr(self, 'global_metric') else None

    def add_delta(self, delta):
        self.deltas_buffer.append(delta)

    def clear_deltas(self):
        self.deltas_buffer = []

    def get_all_deltas(self):
        return self.deltas_buffer
    
    def add_metric(self, metric):
        self.metrics.append(metric)


training_groups = {
    "income": TrainingGroup("income"),
    "credit": TrainingGroup("credit"),
    "lsd": TrainingGroup("lsd"),
    "smoking": TrainingGroup("smoking")
}
group_dims = {
    "income": (14, 2),
    "credit": (23, 3),
    "lsd": (16, 2),
    "smoking": (25, 2)
}

training_groups = {}
for group_name, (input_dim, output_dim) in group_dims.items():
    group = TrainingGroup(group_name)
    model = BaseClassifier(input_dim=input_dim, output_dim=output_dim)
    model.build(input_shape=(None, input_dim))
    group.set_global_weights(model.get_weights())
    training_groups[group_name] = group

if __name__ == "__main__":
    print(training_groups)

