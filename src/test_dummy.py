# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
def inc(x):
    return x + 1


def test_inc():
    assert inc(2) == 3
