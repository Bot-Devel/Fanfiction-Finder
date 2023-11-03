from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]
OWNER_ID = os.environ["OWNER_ID"]
FICHUB_SITES = os.environ["FICHUB_SITES"].split(",")
