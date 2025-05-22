import pandas as pd
from sklearn.preprocessing import LabelEncoder
from typing import Tuple, Dict
import re
import numpy as np

def preprocess_dataset(df: pd.DataFrame, dataset_name: str) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    if dataset_name == 'income':
        return preprocess_income(df)
    elif dataset_name == 'credit':
        return preprocess_score(df)
    elif dataset_name == 'lsd':
        return preprocess_lumpy(df)
    elif dataset_name == 'smoking':
        return preprocess_smoking(df)
    else:
        raise ValueError(f"Unknown dataset name: {dataset_name}")

def preprocess_income(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    df = df.copy()
    categorical_cols = df.select_dtypes(include='object').columns
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
    
    x=df.drop(columns=['income_>50K'])
    y=df['income_>50K']

    return x,y

def preprocess_score(df):
    df = df.copy()
    df.drop(['ID', 'Customer_ID', 'SSN', 'Name'], axis=1, inplace=True)

    for col in ['Age', 'Num_of_Loan', 'Num_of_Delayed_Payment']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].mask(df[col] < 0, np.nan)

    money_cols = ['Annual_Income', 'Outstanding_Debt', 'Changed_Credit_Limit', 
                  'Amount_invested_monthly', 'Monthly_Balance']
    for col in money_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    def convert_history_age(s):
        if pd.isna(s):
            return np.nan
        match = re.match(r'(\d+)\s+Years?\s+and\s+(\d+)\s+Months?', s)
        if match:
            return int(match.group(1)) * 12 + int(match.group(2))
        return np.nan
    df['Credit_History_Age'] = df['Credit_History_Age'].apply(convert_history_age)


    for col in df.select_dtypes(include=[np.number]).columns:
        df[col].fillna(df[col].mean(), inplace=True)

    for col in df.select_dtypes(include='object').columns:
        le = LabelEncoder()
        df[col] = df[col].fillna('Unknown')
        df[col] = le.fit_transform(df[col])
    
    x=df.drop(columns=['Credit_Score'])
    y=df['Credit_Score']

    return x,y


def preprocess_lumpy(df):
    df = df.drop(columns=['reportingDate'])
    df = df.drop(columns=['x', 'y'])

    for col in ['region', 'country', 'dominant_land_cover']:
        if df[col].isnull().any():
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)
    
    le_region = LabelEncoder()
    df['region'] = le_region.fit_transform(df['region'])
    
    le_country = LabelEncoder()
    df['country'] = le_country.fit_transform(df['country'])
    
    X = df.drop(columns=['lumpy'])
    y = df['lumpy']
    
    return X, y


def preprocess_smoking(df):
    df = df.drop(columns=['ID'])

    for col in ['gender', 'oral', 'tartar']:
        if df[col].isnull().any():
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)
    
    gender_map = {'F': 0, 'M': 1}
    df['gender'] = df['gender'].map(gender_map)
    
    yes_no_map = {'Y': 1, 'N': 0}
    df['oral'] = df['oral'].map(yes_no_map)
    df['tartar'] = df['tartar'].map(yes_no_map)
    
    if df['smoking'].dtype == 'object':
        le = LabelEncoder()
        df['smoking'] = le.fit_transform(df['smoking'])

    X = df.drop(columns=['smoking'])
    y = df['smoking']
    
    return X, y

if __name__ == "__main__":
    datasets = {
    "income": "data/income.csv",
    "score": "data/score.csv",
    "lumpy_skin": "data/lumpy skin disease data.csv",
    "smoking": "data/smoking.csv"
    }

    for name, path in datasets.items():
        print(f"\n--- Testing {name} dataset ---")
        try:
            df = pd.read_csv(path)
            X, y = preprocess_dataset(df, dataset_name=name)

            print(f"Features shape: {X.shape}")
            print(f"Labels shape: {y.shape}")
            print(f"First 3 labels:\n{y.head(3)}")
            print(f"First 3 rows of features:\n{X.head(3)}")
        except Exception as e:
            print(f"Error while processing {name}: {e}")
