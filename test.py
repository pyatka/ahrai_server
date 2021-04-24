import json

import codecs
import psycopg2
import psycopg2.extras

from settings import DB

ds = []

with codecs.open('data.json', encoding='utf-8') as f:
    for l in json.loads(f.read()):
        for v in l.values():
            if v is not None and v not in ds:
                ds.append(v)

connection = psycopg2.connect(**DB["postgresql"])
cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

for d in ds:
    cursor.execute("""INSERT INTO employer (name) VALUES (%s)""", (d,))
connection.commit()

connection.close()