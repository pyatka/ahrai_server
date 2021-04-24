from db import get_pg
import uuid

class User(object):
    def __init__(self, user_id):
        self.id = user_id

    def generate_token(self):
        pg = get_pg()
        
        user_data = pg.select("""
            SELECT * FROM users WHERE id = %(user_id)s
        """, {
            "user_id": self.id
        })

        token = str(uuid.uuid4())

        return token

def auth_by_token(token=""):
    # r = get_redis()
    # if r.exists("auth:token:%s" % token):
    #     user_id = int(r.hget("auth:token:%s" % token, "id"))
    #     return User(user_id)

    return None