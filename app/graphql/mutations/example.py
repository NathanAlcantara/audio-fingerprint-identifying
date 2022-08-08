from graphene import Boolean, Field, Mutation, String

from ..models import Example


class ExampleMutation(Mutation):
    class Arguments:
        string = String()

    ok = Boolean()
    example = Field(lambda: Example)

    def mutate(root, info, string):
        example = Example(string=string)
        ok = True
        return ExampleMutation(example=example, ok=ok)
