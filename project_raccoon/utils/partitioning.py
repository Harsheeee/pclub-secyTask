import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict
from utils.preprocessing import preprocess_dataset

def split_dataset(
    X: np.ndarray,
    y: np.ndarray,
    train_size: float = 0.6,
    val_size: float = 0.2,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    if not np.isclose(train_size + val_size + test_size, 1.0):
        raise ValueError("train_size + val_size + test_size must sum to 1.")

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, train_size=train_size, stratify=y, random_state=random_state
    )

    val_ratio = val_size / (val_size + test_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, train_size=val_ratio, stratify=y_temp, random_state=random_state
    )

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

def partition_among_clients(
    X: np.ndarray,
    y: np.ndarray,
    num_clients: int,
    shuffle: bool = True,
    random_state: int = 42
) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
    if shuffle:
        rng = np.random.default_rng(seed=random_state)
        indices = np.arange(len(X))
        rng.shuffle(indices)
        X, y = X[indices], y[indices]

    client_data = {}
    total_samples = len(X)
    samples_per_client = total_samples // num_clients

    for client_id in range(num_clients):
        start = client_id * samples_per_client
        end = start + samples_per_client if client_id != num_clients - 1 else total_samples
        client_data[client_id] = (X[start:end], y[start:end])

    return client_data

def load_and_partition_dataset(
    file_path: str,
    dataset_name: str,
    num_clients: int,
    train_size: float = 0.6,
    val_size: float = 0.2,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[Dict[int, Tuple[np.ndarray, np.ndarray]], Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    df = pd.read_csv(file_path)
    X, y = preprocess_dataset(df, dataset_name)

    X = X.values
    y = y.values

    (X_train, y_train), val_data, test_data = split_dataset(
        X, y,
        train_size=train_size,
        val_size=val_size,
        test_size=test_size,
        random_state=random_state
    )

    client_data = partition_among_clients(X_train, y_train, num_clients=num_clients, random_state=random_state)

    return client_data, val_data, test_data

if __name__ == "__main__":
    client_data, val_data, test_data = load_and_partition_dataset(
        "data/score.csv", "score", num_clients=4
    )

    print("\n--- Partitioning Summary ---")
    for cid, (X_c, y_c) in client_data.items():
        print(f"Client {cid}: {X_c.shape[0]} samples")

    print(f"\nValidation set: {val_data[0].shape}")
    print(f"Test set: {test_data[0].shape}")
