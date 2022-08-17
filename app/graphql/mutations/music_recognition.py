import os

from graphene import Boolean, Mutation
from graphene_file_upload.scalars import Upload

from ...services import AudioService, SongService


class MusicRecognitionMutation(Mutation):
    class Arguments:
        sample_file = Upload(required=True)

    success = Boolean()

    def mutate(self, info, sample_file, **kwargs):
        songname, extension = os.path.splitext(sample_file.filename)

        filename = songname+extension

        sample_file.save(filename)

        audio_service = AudioService()

        audio = audio_service.parse_audio(filename)

        song_service = SongService(audio)

        song_service.recognize()

        os.remove(filename)

        return MusicRecognitionMutation(success=True)
