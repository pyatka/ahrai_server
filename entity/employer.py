from graphene import ObjectType, relay, String, Int, Mutation, Boolean, Field
from model.employer import EmployerModel, auth_employer
from middlewares import auth

class PositionEmployer(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, entity_id, view_order, *args, **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.id = entity_id
        self.order = view_order

    entity_id = Int()
    view_order = Int()

    def resolve_entity_id(self, info, **args):
        return self.id

    def resolve_view_order(self, info, **args):
        return self.order

class Employer(ObjectType):
    class Meta:
        interfaces = (relay.Node, )

    def __init__(self, model, *args, **kwargs):
        ObjectType.__init__(self, *args, **kwargs)
        self.model = model
        self.employer_data = self.model.get_employer_data()

    entity_id = Int()
    name = String()
    surname = String()

    def resolve_entity_id(self, info, **args):
        return int(self.employer_data["id"])

    def resolve_name(self, info, **args):
        return self.employer_data["name"]

    def resolve_surname(self, info, **args):
        return self.employer_data["surname"]

class AuthEmployer(Mutation):
    class Arguments:
        email = String()
        password = String()

    success = Boolean()
    token = String()

    def mutate(self, info, email=None, password=None, *args, **kwargs):
        e = auth_employer(email, password)
        if e is None:
            return AuthEmployer(success=False, token="")
        
        return AuthEmployer(success=True, token=e.get_token())

class UpdateEmployer(Mutation):
    class Arguments:
        entity_id = Int()
        name = String()
        surname = String()

    success = Boolean()

    @auth(["EDIT_EMPLOYER"])
    def mutate(self, info, name=None, surname=None, *args, **kwargs):
        em = EmployerModel(kwargs["entity_id"])
        em.update_emplyer_data(name=name, surname=surname)
        return UpdateEmployer(success=True)

def get_employer(id=None):
    if id is not None:
        return Employer(EmployerModel(id))

    return None