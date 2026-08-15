"""
Data ingestion module for AIOps MVP.

Handles reading metrics from various sources:
- CSV files from AIOps Challenge 2020
- TXT files from OmniAnomaly/SMD dataset
- Kafka streams (future)
- Elasticsearch (future)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataIngester:
    """Ingests metric data from various sources."""

    def __init__(self, config: dict):
        """Initialize data ingester with configuration."""
        self.config = config
        self.aiops_path = config['data']['aiops_path']
        self.smd_path = config['data']['smd_path']

    def read_smd_data(self, machine_id: str) -> pd.DataFrame:
        """
        Read Server Machine Dataset (SMD) files.

        Args:
            machine_id: Machine identifier (e.g., 'machine-1-1')

        Returns:
            DataFrame with metric values (rows=timestamps, columns=metrics)
        """
        file_path = os.path.join(self.smd_path, f"{machine_id}.txt")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        logger.info(f"Reading SMD data from {file_path}")
        data = np.loadtxt(file_path, delimiter=',')

        # Create DataFrame with generic metric names
        n_metrics = data.shape[1] if len(data.shape) > 1 else 1
        columns = [f"metric_{i}" for i in range(n_metrics)]

        df = pd.DataFrame(data.reshape(-1, n_metrics), columns=columns)
        df['timestamp'] = pd.date_range(start='2020-01-01', periods=len(df), freq='1min')
        df['machine_id'] = machine_id

        logger.info(f"Loaded {len(df)} records with {n_metrics} metrics")
        return df

    def read_aiops_csv(self, filename: str) -> pd.DataFrame:
        """
        Read AIOps Challenge CSV files.

        Args:
            filename: CSV filename in data/raw/aiops/

        Returns:
            DataFrame with AIOps data
        """
        file_path = os.path.join(self.aiops_path, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        logger.info(f"Reading AIOps CSV from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} rows from {filename}")

        return df

    def list_smd_machines(self) -> List[str]:
        """List all available machine IDs in SMD dataset."""
        files = [f[:-4] for f in os.listdir(self.smd_path) if f.endswith('.txt')]
        return sorted(files)

    def list_aiops_files(self) -> List[str]:
        """List all available CSV files in AIOps dataset."""
        files = [f for f in os.listdir(self.aiops_path) if f.endswith('.csv')]
        return sorted(files)
