from db import get_pg

class PositionGroupModel(object):
    def __init__(self, id):
        self.pg = get_pg()
        self.id = id

    def exists(self):
        self.pg.select("SELECT id FROM position_group WHERE id = %s", (self.id,))
        return self.pg.count > 0

    def get_position_group_data(self):
        return self.pg.select("SELECT * FROM position_group WHERE id = %s", (self.id,))

    def add_new_position_group(self, name):
        if name is not None:
            self.pg.select("SELECT id FROM position_group WHERE name = %s", (name,))
            if self.pg.count == 0:
                return self.pg.insert("INSERT INTO position_group (name) VALUES (%s)", (name,))

        return -1

class PositionModel(object):
    def __init__(self, id):
        self.pg = get_pg()
        self.id = id
        self.settings = None

    def position_settings_update(self, data):
        self.settings = data

    def __str__(self):
        pgroup = self.get_position_group()
        data = self.get_position_data()
        return "%s: %s" % (pgroup["name"], data["name"])

    def exists(self):
        self.pg.select("SELECT id FROM position WHERE id = %s", (self.id,))
        return self.pg.count > 0

    def get_position_group(self):
        data = self.get_position_data()
        position_group = PositionGroupModel(data["position_group_id"])
        return position_group.get_position_group_data()

    def get_position_data(self):
        data = self.pg.select("SELECT * FROM position WHERE id = %s", (self.id,))
        data = dict(data)
        if self.settings is not None:
            data["default_show"] = self.settings["to_show"]
            data["comment"] = self.settings["comment"]

        return data

    def add_position(self, name, capacity, group, default_show, one_position):
        self.pg.select("SELECT id FROM position WHERE name = %s AND position_group_id = %s", (name, group,))
        if self.pg.count == 0:
            return self.pg.insert("""INSERT INTO position 
                                        (name, capacity, position_group_id, default_show, one_position) 
                                        VALUES (%s, %s, %s, %s, %s)""", 
                                        (name, capacity, group, default_show, one_position,))

        return -1

def get_position_groups_models():
    pg = get_pg()
    return [PositionGroupModel(pg["id"]) for pg in pg.select("""SELECT id FROM 
                                                                    position_group 
                                                                    ORDER BY view_order ASC""", auto_one=False)]

def get_positions_models():
    pg = get_pg()
    return [PositionModel(pg["id"]) for pg in pg.select("""SELECT id FROM position 
                                                                ORDER BY view_order ASC""", auto_one=False)]
