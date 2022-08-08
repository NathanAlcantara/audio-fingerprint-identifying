from graphene import ObjectType, String, Int


class Example(ObjectType):
    string = String()
    int = Int()
