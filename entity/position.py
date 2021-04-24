from graphene import ObjectType, relay, String, Int, Mutation, Boolean, Field, List
from model import PositionGroupModel, PositionModel

from entity.employer import PositionEmployer
from middlewares import auth

class PositionGroup(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, model, *args, **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.model = model
        self.data = self.model.get_position_group_data()

    entity_id = Int()
    name = String()
    view_order = Int()

    def resolve_entity_id(self, info, **args):
        return self.data["id"]

    def resolve_name(self, info, **args):
        return self.data["name"]

    def resolve_view_order(self, info, **args):
        return self.data["view_order"]

class DayPosition(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, day_model , model, *args, **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.model = model
        self.day_model = day_model
        self.data = self.model.get_position_data()

    entity_id = Int()
    comment = String()
    position_capacity = Int()
    one_position = Boolean()
    default_show = Boolean()
    view_order = Int()
    employers = List(PositionEmployer)

    def resolve_employers(self, info, **args):
        return [PositionEmployer(*e) for e in self.day_model.get_position_employers(self.data["id"])]

    def resolve_view_order(self, info, **args):
        return self.data["view_order"]

    def resolve_entity_id(self, info, **args):
        return self.data["id"]

    def resolve_position_capacity(self, info, **args):
        return self.data["capacity"]

    def resolve_default_show(self, info, **args):
        return self.data["default_show"]

    def resolve_one_position(self, info, **args):
        return self.data["one_position"]

    def resolve_comment(self, info, **args):
        if "comment" in self.data.keys():
            return self.data["comment"]
        else:
            return ""

class Position(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, model, *args, **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.model = model
        self.data = self.model.get_position_data()

    entity_id = Int()
    name = String()
    comment = String()
    position_group = Field(PositionGroup)
    position_capacity = Int()
    one_position = Boolean()
    default_show = Boolean()
    view_order = Int()

    def resolve_view_order(self, info, **args):
        return self.data["view_order"]

    def resolve_entity_id(self, info, **args):
        return self.data["id"]

    def resolve_position_capacity(self, info, **args):
        return self.data["capacity"]

    def resolve_default_show(self, info, **args):
        return self.data["default_show"]

    def resolve_one_position(self, info, **args):
        return self.data["one_position"]

    def resolve_position_group(self, info, **args):
        return PositionGroup(PositionGroupModel(self.data["position_group_id"]))

    def resolve_name(self, info, **args):
        return self.data["name"]

    def resolve_comment(self, info, **args):
        if "comment" in self.data.keys():
            return self.data["comment"]
        else:
            return ""

class AddPosition(Mutation):
    class Arguments:
        name = String()
        position_group = Int()
        position_capacity = Int()
        default_show = Boolean()
        one_position = Boolean()

    success = Boolean()
    entity_id = Int()

    @auth(["EDIT_POSITION"])
    def mutate(self, info, name=None, position_group=-1, position_capacity=-1, default_show=False, one_position=False, *args, **kwargs):
        if name is not None and len(name) > 0:
            pgm = PositionGroupModel(position_group)
            if pgm.exists():
                if position_capacity > 0:
                    if name is not None and len(name) > 0:
                        pm = PositionModel(None)
                        id = pm.add_position(name, position_capacity, position_group, default_show, one_position)
                        return AddPosition(success=True, entity_id=id)
                    else:
                       return AddPosition(success=False, entity_id=-1) 
                else:
                    return AddPosition(success=False, entity_id=-1)
            else:
                return AddPosition(success=False, entity_id=-1)
        else:
            return AddPosition(success=False, entity_id=-1)

class AddPositionGroup(Mutation):
    class Arguments:
        name = String()

    success = Boolean()
    entity_id = Int()

    @auth(["EDIT_POSITION"])
    def mutate(self, info, name=None, *args, **kwargs):
        if name is not None and len(name) > 0:
            pgm = PositionGroupModel(None)
            id = pgm.add_new_position_group(name)
            return AddPositionGroup(success=True, entity_id=id)
        else:
            return AddPositionGroup(success=False, entity_id=-1)