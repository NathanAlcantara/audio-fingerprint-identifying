import os

from graphene import Boolean, Mutation
from graphene_file_upload.scalars import Upload

from ...repositories import FingerprintRepository, SongRepository
from ...services import FingerprintService, AudioService


class MusicUploaderMutation(Mutation):
    class Arguments:
        music_file = Upload(required=True)

    success = Boolean()

    def mutate(self, info, music_file, **kwargs):
        songname, extension = os.path.splitext(music_file.filename)

        filename = songname+extension

        music_file.save(filename)

        audio_service = AudioService()
        fingerprint_service = FingerprintService()

        song_repo = SongRepository()
        fingerprint_repo = FingerprintRepository()

        audio = audio_service.parse_audio(filename)

        song = song_repo.get_by_file_hash(audio['file_hash'])

        if not song:
            song = song_repo.upsert(
                {
                    'name': filename,
                    'file_hash': audio['file_hash']
                }
            )

        hashes = set()

        for channel in audio['channels']:
            channel_hashes = fingerprint_service.fingerprint(
                channel, Fs=audio['Fs'])
            channel_hashes = set(channel_hashes)

            hashes |= channel_hashes

        for hash, offset in hashes:
            fingerprint = fingerprint_repo.get_by_hash(hash)

            if not fingerprint:
                fingerprint_repo.upsert(
                    {
                        "hash": hash,
                        "offset": offset
                    }, song)

        os.remove(filename)

        return MusicUploaderMutation(success=True)
