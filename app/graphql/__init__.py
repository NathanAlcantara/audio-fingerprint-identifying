import graphene

from .mutations import Mutations
from .queries import Queries

schema = graphene.Schema(query=Queries, mutation=Mutations)
