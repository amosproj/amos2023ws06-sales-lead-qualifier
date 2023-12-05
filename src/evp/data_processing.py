# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from logger import get_logger

log = get_logger()


def split_dataset(
    in_path: str,
    out_path: str,
    train_size: float,
    val_size: float,
    test_size: float,
    add_labels: bool = False,
):
    valid_sizes = train_size + val_size + test_size == 1
    if not valid_sizes:
        log.error(
            "Invalid size combination. Training, validation and test size must add to 1"
        )
        return None
    try:
        full_df = pd.read_csv(in_path, index_col=None)
        if add_labels:
            full_df["lead_value"] = np.random.uniform(
                low=1000, high=1000000, size=len(full_df)
            )
    except FileNotFoundError:
        log.error(f"Could not find {in_path} splitting data")
        return
    relative_val_size = val_size / (1 - test_size)
    train_val_df, test_df = train_test_split(
        full_df,
        test_size=test_size,
    )
    train_df, val_df = train_test_split(train_val_df, test_size=relative_val_size)
    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    train_df.to_csv(f"{out_path}_train.csv")
    val_df.to_csv(f"{out_path}_val.csv")
    test_df.to_csv(f"{out_path}_test.csv")
    return train_df, val_df, test_df
