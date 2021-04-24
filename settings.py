import os
import json

APP_DIR = os.path.dirname(__file__)
DB = None

UNPROTECTED_PATH = []

PAIRED = {
    '22': 34,
    '23': 34,
    '24': 34,
    '25': 34,
    '26': 34,
    '27': 34,
}

with open("db.json", "r") as f:
    DB = json.loads(f.read())