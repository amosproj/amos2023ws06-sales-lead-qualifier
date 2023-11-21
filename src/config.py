# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

FACEBOOK_SDK_GRAPH_API_KEY = os.getenv("FACEBOOK_SDK_GRAPH_API_KEY")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
