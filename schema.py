import graphene
from graphene import relay

from entity import *
from model import get_employers, get_position_groups_models, get_positions_models, DayModel
from middlewares import auth

from db import get_pg

class Query(graphene.ObjectType):
    is_authorized = graphene.Boolean()
    employers = graphene.List(Employer)
    position_groups = graphene.List(PositionGroup)
    positions = graphene.List(Position)
    employer = graphene.Field(Employer, entity_id=graphene.Int())
    day = graphene.Field(Day, year=graphene.Int(), month=graphene.Int(), day=graphene.Int())

    def resolve_position_groups(self, info, **args):
        return [PositionGroup(pg) for pg in get_position_groups_models()]

    def resolve_employer(self, info, **args):
        return get_employer(args["entity_id"])

    @auth(["DAY_EDITOR"])
    def resolve_day(self, info, **args):
        if all([i in args.keys() for i in ["year", "month", "day"]]):
            return Day(DayModel(year=args["year"], month=args["month"], day=args["day"]))
        return None

    def resolve_employers(self, info, **args):
        return [Employer(e) for e in get_employers()]

    def resolve_positions(self, info, **args):
        return [Position(e) for e in get_positions_models()]

    def resolve_is_authorized(self, info, **args):
        if args["user"] is not None:
            return True
        else:
            return False

# class TestM(graphene.Mutation):
#     class Arguments:
#         name = graphene.String()

#     success = graphene.Boolean()
#     token = graphene.String()

#     def mutate(self, info, name, **args):
#         return TestM(success=True, token=name)

class Mutations(graphene.ObjectType):
    update_employer = UpdateEmployer.Field()
    add_position_group = AddPositionGroup.Field()
    add_position = AddPosition.Field()
    update_day_position = UpdateDayPosition.Field()
    add_position_employer = AddPositionEmployer.Field()
    delete_position_employer = DeletePositionEmployer.Field()
    switch_position_employer_order = SwitchPositionEmployerOrder.Field()
    auth_employer = AuthEmployer.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)