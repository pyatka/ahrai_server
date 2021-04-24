from db import get_pg
from datetime import date, timedelta

from model.position import get_positions_models, PositionModel, get_position_groups_models
from model.employer import EmployerModel
from middlewares import position_edit

from settings import PAIRED

class DayModel(object):
    def __init__(self, year=None, month=None, day=None, day_id=None):
        self.pg = get_pg()
        
        self.date = None
        if year is not None and month is not None and day is not None:
            self.date = date(year, month, day)

        self.day_id = day_id

        if not self.exists():
            self.init_day()

    def __str__(self):
        return self.get_view("%d/%m/%Y")

    def get_view(self, pattern):
        if self.date is None:
            self.get_day_data()

        return self.date.strftime(pattern)

    def get_tomorrow(self):
        self.get_day_data()
        tomorrow = self.date + timedelta(days=1)
        tm = DayModel(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
        tm.get_day_data()
        return tm

    def get_yesterday(self):
        self.get_day_data()
        yesterday = self.date - timedelta(days=1)
        tm = DayModel(year=yesterday.year, month=yesterday.month, day=yesterday.day)
        tm.get_day_data()
        return tm

    def exists(self):
        if self.date is None:
            self.pg.select("SELECT * FROM day WHERE id = %s", (self.day_id,))
        else:
            self.pg.select("SELECT * FROM day WHERE date = %s LIMIT 1", (self.date,))
        return self.pg.count > 0

    def switch_position_employer_order(self, position_id, first_id, second_id):
        fo = self.pg.select("""SELECT view_order FROM day_position_to_employer 
                                                WHERE day_id = %s 
                                                    AND position_id = %s 
                                                    AND employer_id = %s""", (self.day_id, position_id, first_id,))["view_order"]
        so = self.pg.select("""SELECT view_order FROM day_position_to_employer 
                                                WHERE day_id = %s 
                                                    AND position_id = %s 
                                                    AND employer_id = %s""", (self.day_id, position_id, second_id,))["view_order"]

        self.pg.execute("""UPDATE day_position_to_employer SET view_order = %s
                                WHERE day_id = %s
                                    AND position_id = %s 
                                    AND employer_id = %s""", (so, self.day_id, position_id, first_id,))

        self.pg.execute("""UPDATE day_position_to_employer SET view_order = %s
                                WHERE day_id = %s
                                    AND position_id = %s 
                                    AND employer_id = %s""", (fo, self.day_id, position_id, second_id,))

        return True

    @position_edit("ADD")
    def add_position_employer(self, position_id, employer_id, view_order):
        try:
            self.pg.execute("""INSERT INTO day_position_to_employer 
                                (day_id, position_id, employer_id, view_order)
                                VALUES (%s, %s, %s, %s)""", (self.day_id, position_id, employer_id, view_order,))
        except:
            self.pg.rollback()

        return []

    @position_edit("DELETE")
    def delete_position_employer(self, position_id, employer_id):
        return self.force_delete_position_employer(position_id, employer_id)

    def force_delete_position_employer(self, position_id, employer_id):
        self.pg.execute("""DELETE FROM day_position_to_employer 
                            WHERE day_id = %s 
                                AND position_id = %s 
                                AND employer_id = %s""", (self.day_id, position_id, employer_id,))
        return []

    def update_position(self, position_id, default_show, comment, try_insert=True):
        self.pg.execute("""UPDATE day_to_position
                                SET to_show = %s, 
                                    comment = %s 
                                WHERE  
                                    day_id = %s AND position_id = %s""", (default_show, comment, self.day_id, position_id,))

        if self.pg.count == 0 and try_insert:
            pm = PositionModel(position_id)
            p_data = pm.get_position_data()
            self.pg.execute("INSERT INTO day_to_position (day_id, position_id, view_order, to_show) VALUES (%s, %s, %s, %s)", (self.day_id,
                                                                                                            p_data["id"],
                                                                                                            p_data["view_order"],
                                                                                                            p_data["default_show"]))
            self.update_position(position_id, default_show, comment, try_insert=False)

    def init_day(self):
        day_id = self.pg.insert("INSERT INTO day (date) VALUES (%s)", (self.date,))
        self.day_id = day_id
        for p in get_positions_models():
            p_data = p.get_position_data()
            self.pg.execute("INSERT INTO day_to_position (day_id, position_id, view_order, to_show) VALUES (%s, %s, %s, %s)", (day_id,
                                                                                                            p_data["id"],
                                                                                                            p_data["view_order"],
                                                                                                            p_data["default_show"]))

    def get_position_employers(self, position_id):
        return [(e["employer_id"], e["view_order"],) for e in self.pg.select("""SELECT employer_id, view_order 
                            FROM day_position_to_employer
                            WHERE day_id = %s 
                                AND position_id = %s
                                ORDER BY view_order ASC""", 
                            (self.day_id, position_id,), auto_one=False)]

    def get_employer_positions(self, employer_id):
        return [PositionModel(e["position_id"]) for e in self.pg.select("""SELECT position_id 
                            FROM day_position_to_employer
                            WHERE day_id = %s 
                                AND employer_id = %s""", 
                            (self.day_id, employer_id,), auto_one=False)]

    def get_duty_data(self):
        duty_data = self.pg.select("""SELECT p.id, p.name as pname, e.name FROM position p
                                    LEFT JOIN position_group pg ON pg.id = p.position_group_id
                                    LEFT JOIN day_position_to_employer dpte ON dpte.day_id = %s
                                                                                AND dpte.position_id = p.id
                                    LEFT JOIN employer e ON e.id = dpte.employer_id
                                WHERE pg.key_name = 'DUTY'
                                ORDER BY p.view_order ASC""", (self.day_id,))
        return duty_data
    
    def get_clear_day_data(self):
        day_data = self.get_day_data()
        positions = day_data["positions"]
        day_data["positions"] = []
        day_data["position_groups"] = []
        day_data["positions_cnt"]  = 0

        for pgroup in get_position_groups_models():
            pgroup_data = dict(pgroup.get_position_group_data())
            pgroup_data["positions"] = []
            pgroup_data["positions_cnt"]  = 0
            for p in positions:
                pdata = dict(p.get_position_data())
                if pdata["position_group_id"] == pgroup_data["id"]:
                    pdata["employers"] = []
                    for e, _ in self.get_position_employers(pdata["id"]):
                        em = EmployerModel(e)
                        pdata["employers"].append(dict(em.get_employer_data()))
                    pgroup_data["positions"].append(pdata)
                    pgroup_data["positions_cnt"] += 1
                    day_data["positions_cnt"] += 1
            day_data["position_groups"].append(pgroup_data)

        return day_data

    def get_day_data(self):
        if self.date is None:
            day_data = self.pg.select("SELECT * FROM day WHERE id = %s ORDER BY id DESC LIMIT 1", (self.day_id,))
            day_data = dict(day_data)
            self.date = day_data["date"] 
        else:
            day_data = self.pg.select("SELECT * FROM day WHERE date = %s ORDER BY id DESC LIMIT 1", (self.date,))
            day_data = dict(day_data)
            self.day_id = day_data["id"]

        day_positions_settings = self.pg.select("""SELECT * FROM day_to_position 
                                                    WHERE day_id = %s
                                                    ORDER BY view_order ASC""", (day_data["id"],), auto_one=False)

        positions = get_positions_models()
        for p in positions:
            for dps in day_positions_settings:
                if p.id == dps["position_id"]:
                    p.position_settings_update(dps)

        day_data["positions"] = positions

        return day_data