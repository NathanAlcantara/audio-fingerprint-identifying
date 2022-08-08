from graphene import Field, ObjectType

from ..models import Example


class Queries(ObjectType):
    example = Field(Example)
