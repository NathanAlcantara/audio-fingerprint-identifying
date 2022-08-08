from graphene import ObjectType

from .example import ExampleMutation


class Mutations(ObjectType):
    example = ExampleMutation.Field()
