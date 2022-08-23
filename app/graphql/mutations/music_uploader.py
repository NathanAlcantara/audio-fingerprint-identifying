import os

from graphene import Boolean, Mutation
from graphene_file_upload.scalars import Upload

from ...repositories import FingerprintRepository, SongRepository
from ...services import AudioService, FingerprintService


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
        channel_amount = len(audio['channels'])

        for channeln, channel in enumerate(audio['channels']):
            msg = '   fingerprinting channel %d/%d'
            print(msg % (channeln+1, channel_amount))

            channel_hashes = fingerprint_service.fingerprint(
                channel, Fs=audio['Fs'])
            channel_hashes = set(channel_hashes)

            msg = '   finished channel %d/%d, got %d hashes'
            print(msg % (channeln+1, channel_amount, len(channel_hashes)))

            hashes |= channel_hashes

        msg = '   finished fingerprinting, got %d unique hashes'

        fingerprints = []
        for hash, offset in hashes:
            fingerprints.append({
                "hash": hash,
                "offset": offset
            })

        msg = '   storing %d hashes in db' % len(fingerprints)
        print(msg)

        fingerprint_repo.upsert_bulk(fingerprints, song)

        os.remove(filename)

        return MusicUploaderMutation(success=True)
