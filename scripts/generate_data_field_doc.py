# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
import inspect
import os.path

import pandas as pd

from bdc import steps

if __name__ == "__main__":
    BASE_PATH = os.path.dirname(__file__)

    col_names = []
    for name, obj in inspect.getmembers(steps):
        if inspect.isclass(obj) and obj.added_cols is not None:
            col_names += obj.added_cols

            # TODO: add description and source for each columns

    cols_df = pd.DataFrame({"column_id": col_names})
    out_path = os.path.abspath(
        os.path.join(BASE_PATH, "../Documentation/data_fields.csv")
    )
    cols_df.to_csv(out_path, index=False)
