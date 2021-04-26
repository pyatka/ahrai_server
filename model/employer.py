from db import get_pg
import hashlib
import uuid

class EmployerModel(object):
    def __init__(self, id):
        self.pg = get_pg()
        self.id = id
        self.permissions = None

    def __str__(self):
        data = self.get_employer_data()
        return "%s" % (data["name"])

    def load_permissions(self):
        data = self.get_employer_data()
        self.permissions = [p["code"] for p in self.pg.select("""SELECT p.code FROM employer_group_to_permission egtp
                                LEFT JOIN permission p ON p.id = egtp.permission_id
                                WHERE egtp.employer_group_id = %s""", (data["group_id"],), auto_one=False)]

    def check_permissoins(self, permissions=[]):
        if type(permissions) != list:
            permissions = [permissions]

        if self.permissions is None:
            self.load_permissions()

        return all(p in self.permissions for p in permissions)

    def get_employer_data(self):
        return self.pg.select("SELECT * FROM employer WHERE id = %s LIMIT 1", (self.id,))

    def update_emplyer_data(self, name=None, surname=None):
        self.pg.execute("UPDATE employer SET name = %s, surname = %s WHERE id = %s", (name, surname, self.id,))
        return True

    def get_token(self):
        token = str(uuid.uuid4())
        self.pg.execute("DELETE FROM token WHERE employer_id = %s", (self.id,))
        self.pg.execute("INSERT INTO token (token, employer_id) VALUES (%s, %s)", (token, self.id,))
        return token

def get_employers():
    pg = get_pg()
    return [EmployerModel(e["id"]) for e in pg.select("""
                                SELECT id FROM employer
                                WHERE title_id != 3
                        """, auto_one=False)]

def auth_employer(email, password):
    pg = get_pg()
    e = pg.select("""SELECT id FROM employer 
                    WHERE email = %s 
                        AND password = %s
                    LIMIT 1""", (email.lower(), hashlib.sha256(password.encode()).hexdigest(),))

    if e != []:
        return EmployerModel(e["id"])
    return None

def auth_by_token(token):
    pg = get_pg()
    e = pg.select("""SELECT employer_id FROM token WHERE token = %s""", (token,))
    if e != []:
        return EmployerModel(e["employer_id"])
    return None
