from graphene import ObjectType, relay, String, Int, Mutation, Boolean, Field, Date, List
from datetime import datetime, date

from entity import DayPosition
from model import  *
from middlewares import auth

class Alert(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, *args, type="info", message="", **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.mtype = type
        self.message = message

    type = String()
    message = String()

    def resolve_type(self, info, **args):
        return self.mtype

    def resolve_message(self, info, **args):
        return self.message

class Day(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, model, *args, **kwargs):
        self.model = model
        self.data = self.model.get_day_data()

        ObjectType.__init__(self, *args, **kwargs)

    entity_id = Int()
    date = Date()
    positions = List(DayPosition)

    def resolve_entity_id(self, info, **args):
        return self.data["id"]

    def resolve_date(self, info, **args):
        return self.model.date

    def resolve_positions(self, info, **args):
        return [DayPosition(self.model, d) for d in self.data["positions"]]

class AddPositionEmployer(Mutation):
    class Arguments:
        day_id = Int()
        position_id = Int()
        employer_id = Int()
        order_view = Int()

    success = Boolean()
    entity_id = Int()
    alerts = List(Alert)

    @auth(["DAY_EDITOR"])
    def mutate(self, info, day_id=None, position_id=None, employer_id=None, order_view=None, *args, **kwargs):
        dm = DayModel(day_id=day_id)
        alerts = dm.add_position_employer(position_id, employer_id, order_view)
        alerts = [Alert(**a) for a in alerts]
        return AddPositionEmployer(success=True, entity_id=1, alerts=alerts)

class DeletePositionEmployer(Mutation):
    class Arguments:
        day_id = Int()
        position_id = Int()
        employer_id = Int()

    success = Boolean()
    entity_id = Int()
    alerts = List(Alert)

    @auth(["DAY_EDITOR"])
    def mutate(self, info, day_id=None, position_id=None, employer_id=None, *args, **kwargs):
        dm = DayModel(day_id=day_id)
        alerts = dm.delete_position_employer(position_id, employer_id)
        alerts = [Alert(**a) for a in alerts]
        return DeletePositionEmployer(success=True, entity_id=1, alerts=alerts)

class SwitchPositionEmployerOrder(Mutation):
    class Arguments:
        day_id = Int()
        position_id = Int()
        first_id = Int()
        second_id = Int()

    success = Boolean()
    entity_id = Int()

    @auth(["DAY_EDITOR"])
    def mutate(self, info, day_id=None, position_id=None, first_id=None, second_id=None, *args, **kwargs):
        dm = DayModel(day_id=day_id)
        dm.switch_position_employer_order(position_id, first_id, second_id)
        return SwitchPositionEmployerOrder(success=True, entity_id=1)

class UpdateDayPosition(Mutation):
    class Arguments:
        day_id = Int()
        position_id = Int()
        default_show = Boolean()
        comment = String()

    success = Boolean()
    entity_id = Int()

    @auth(["DAY_EDITOR"])
    def mutate(self, info, day_id=None, position_id=None, default_show=None, comment="", *args, **kwargs):
        d = DayModel(day_id=day_id)
        d.update_position(position_id, default_show, comment)
        return UpdateDayPosition(success=True, entity_id=1)