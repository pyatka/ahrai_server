import psycopg2
import psycopg2.extras
from flask import g

from settings import DB

class PG_Wrapper(object):
    def __init__(self):
        self.connection = psycopg2.connect(**DB["postgresql"])
        self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    @property
    def count(self):
        return self.cursor.rowcount

    def insert(self, query, params={}, returning_column="id"):
        self.cursor.execute("%s RETURNING %s" % (query, returning_column), params)
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def execute(self, query, params={}):
        self.cursor.execute(query, params)
        self.connection.commit()

    def select(self, query, params={}, auto_one=True):
        self.cursor.execute(query, params)
        if self.cursor.rowcount == 1 and auto_one:
            return self.cursor.fetchone()
        elif self.cursor.rowcount > 1 or (self.cursor.rowcount == 1 and not auto_one):
            return self.cursor.fetchall()
        else:
            return []

    def rollback(self):
        self.connection.rollback()

def get_pg():
    if not hasattr(g, 'pg'):
        g.pg = PG_Wrapper()

    return g.pg