# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import pandas as pd


def mock_hash_check(
    self,
    lead_data: pd.Series,
    data_fill_function: callable,
    step_name: str,
    fields_tofill: list[str],
    *args,
    **kwargs,
):
    return data_fill_function(*args, **kwargs)
