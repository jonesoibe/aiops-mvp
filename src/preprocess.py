import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import yaml, joblib, os

def load_config():
    with open('config/settings.yaml') as f:
        return yaml.safe_load(f)

def engineer_features(df, window_size=60):
    """
    Aggregate raw metric rows into window-level feature vectors.
    Each window produces: mean, max, 95th percentile, rate_of_change
    for every metric column.
    """
    features = []
    for start in range(0, len(df) - window_size, window_size):
        window = df.iloc[start:start + window_size]
        stats = {}
        for col in df.columns:
            stats[f'{col}_mean'] = window[col].mean()
            stats[f'{col}_max']  = window[col].max()
            stats[f'{col}_p95']  = window[col].quantile(0.95)
            # Rate of change: last value minus first value / window size
            stats[f'{col}_roc']  = (window[col].iloc[-1]
                                    - window[col].iloc[0]) / window_size
        features.append(stats)
    return pd.DataFrame(features)

def normalise_features(X_train, X_val, X_test):
    """
    Fit StandardScaler on training data ONLY.
    Apply same scaler to validation and test sets.
    This prevents data leakage.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled   = scaler.transform(X_val)
    X_test_scaled  = scaler.transform(X_test)
    joblib.dump(scaler, 'models/scaler.joblib')
    print('Scaler saved to models/scaler.joblib')
    return X_train_scaled, X_val_scaled, X_test_scaled

def time_based_split(df, val_split=0.15, test_split=0.15):
    """
    Perform time-based train/val/test split on time series data.

    Important: For time series, we must use temporal splits to avoid
    data leakage. We don't shuffle - the order matters!

    Args:
        df: DataFrame with time series data (assumed sorted by time)
        val_split: Fraction of data for validation set
        test_split: Fraction of data for test set

    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    n = len(df)
    train_end = int(n * (1 - val_split - test_split))
    val_end   = int(n * (1 - test_split))

    train_df = df.iloc[:train_end]
    val_df   = df.iloc[train_end:val_end]
    test_df  = df.iloc[val_end:]

    print(f"Time-based split: {len(train_df)} train, {len(val_df)} val, {len(test_df)} test")
    return train_df, val_df, test_df