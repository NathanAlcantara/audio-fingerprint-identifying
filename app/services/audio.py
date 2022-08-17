from hashlib import sha1

import numpy as np
from pydub import AudioSegment
from pydub.utils import audioop


class AudioService:
    def parse_audio(self, filename):
        limit = None
        # limit = 10

        try:
            audiofile = AudioSegment.from_file(filename)

            if limit:
                audiofile = audiofile[:limit * 1000]

            data = np.fromstring(audiofile._data, np.int16)

            channels = []
            for chn in range(audiofile.channels):
                channels.append(data[chn::audiofile.channels])

            fs = audiofile.frame_rate
        except audioop.error:
            print('audioop.error')
        pass
        # fs, _, audiofile = wavio.readwav(filename)

        # if limit:
        #     audiofile = audiofile[:limit * 1000]

        # audiofile = audiofile.T
        # audiofile = audiofile.astype(np.int16)

        # channels = []
        # for chn in audiofile:
        #     channels.append(chn)

        return {
            "filemname": filename,
            "channels": channels,
            "Fs": audiofile.frame_rate,
            "file_hash": self.parse_file_hash(filename)
        }

    def parse_file_hash(self, filename, blocksize=2**20):
        """ Small function to generate a hash to uniquely generate
        a file. Inspired by MD5 version here:
        http://stackoverflow.com/a/1131255/712997

        Works with large files.
        """
        s = sha1()

        with open(filename, "rb") as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                s.update(buf)

        return s.hexdigest().upper()
