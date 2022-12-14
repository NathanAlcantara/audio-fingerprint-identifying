from itertools import zip_longest

from ..configs.fingerprint import DEFAULT_OVERLAP_RATIO, DEFAULT_WINDOW_SIZE
from ..repositories import FingerprintRepository, SongRepository
from .fingerprint import FingerprintService


class SongService:
    def __init__(self, audio) -> None:
        self.song_repo = SongRepository()
        self.fingerprint_repo = FingerprintRepository()
        self.fingerprint_service = FingerprintService()

        self.audio = audio

    def recognize(self):
        matches = []
        data = self.audio['channels']
        channel_amount = len(data)

        for channeln, channel in enumerate(data):
            msg = '   fingerprinting channel %d/%d'
            print(msg % (channeln+1, channel_amount))

            channel_hashes = self.fingerprint_service.fingerprint(
                channel, Fs=self.audio['Fs'])

            matches.extend(self._return_matches(channel_hashes))

            msg = '   finished channel %d/%d, got %d hashes'
            print(msg % (
                channeln+1, channel_amount, len(matches)
            ))

        total_matches_found = len(matches)

        if total_matches_found > 0:
            msg = ' ** totally found %d hash matches'
            print(msg % total_matches_found)

            song = self._align_matches(matches)

            msg = ' => song: %s (id=%d)\n'
            msg += '    offset: %d (%d secs)\n'
            msg += '    confidence: %d'

            print(msg % (
                song['SONG_NAME'], song['SONG_ID'],
                song['OFFSET'], song['OFFSET_SECS'],
                song['CONFIDENCE']
            ))
        else:
            msg = ' ** not matches found at all'
            print(msg)

    @staticmethod
    def _grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        result = []
        for values in zip_longest(fillvalue=fillvalue, *args):
            if values is not fillvalue:
                result.append(values)
        return result

    def _return_matches(self, hashes):
        mapper = {}
        for hash, offset in hashes:
            mapper[hash] = offset
        values = mapper.keys()

        for split_values in self._grouper(values, 1000):
            fingerpints = self.fingerprint_repo.get_all_by_hashes(split_values)
            matches_found = len(fingerpints)

            if matches_found > 0:
                msg = '   ** found %d hash matches (step %d/%d)'
                print(msg % (
                    matches_found,
                    len(split_values),
                    len(values)
                ))
            else:
                msg = '   ** not matches found (step %d/%d)'
                print(msg % (
                    len(split_values),
                    len(values)
                ))

            for fingerprint in fingerpints:
                # (sid, db_offset - song_sampled_offset)
                hash = fingerprint.hash
                sid = fingerprint.song_id
                offset = fingerprint.offset
                yield (sid, offset - mapper[hash])

    def _align_matches(self, matches):
        diff_counter = {}
        largest = 0
        largest_count = 0
        song_id = -1

        for tup in matches:
            sid, diff = tup

            if diff not in diff_counter:
                diff_counter[diff] = {}

            if sid not in diff_counter[diff]:
                diff_counter[diff][sid] = 0

            diff_counter[diff][sid] += 1

            if diff_counter[diff][sid] > largest_count:
                largest = diff
                largest_count = diff_counter[diff][sid]
                song_id = sid

        songM = self.song_repo.get_by_id(song_id)

        nseconds = round(float(largest) / self.audio['Fs'] *
                         DEFAULT_WINDOW_SIZE *
                         DEFAULT_OVERLAP_RATIO, 5)

        return {
            "SONG_ID": song_id,
            "SONG_NAME": songM.name,
            "CONFIDENCE": largest_count,
            "OFFSET": int(largest),
            "OFFSET_SECS": nseconds
        }
