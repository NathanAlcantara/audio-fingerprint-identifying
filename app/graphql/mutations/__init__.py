from graphene import ObjectType

from .music_recognition import MusicRecognitionMutation
from .music_uploader import MusicUploaderMutation


class Mutations(ObjectType):
    upload = MusicUploaderMutation.Field()
    recognition = MusicRecognitionMutation.Field()
