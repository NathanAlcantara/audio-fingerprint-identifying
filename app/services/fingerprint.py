import hashlib
from operator import itemgetter

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (binary_erosion,
                                      generate_binary_structure,
                                      iterate_structure)

from ..configs.fingerprint import (DEFAULT_AMP_MIN, DEFAULT_FAN_VALUE,
                                   DEFAULT_FS, DEFAULT_OVERLAP_RATIO,
                                   DEFAULT_WINDOW_SIZE, FINGERPRINT_REDUCTION,
                                   IDX_FREQ_I, IDX_TIME_J, MAX_HASH_TIME_DELTA,
                                   MIN_HASH_TIME_DELTA, PEAK_NEIGHBORHOOD_SIZE,
                                   PEAK_SORT)


class FingerprintService:
    def fingerprint(self, channel_samples, Fs=DEFAULT_FS,
                    wsize=DEFAULT_WINDOW_SIZE,
                    wratio=DEFAULT_OVERLAP_RATIO,
                    fan_value=DEFAULT_FAN_VALUE,
                    amp_min=DEFAULT_AMP_MIN,
                    plots=False):

        # show samples plot
        if plots:
            plt.plot(channel_samples)
            plt.title('%d samples' % len(channel_samples))
            plt.xlabel('time (s)')
            plt.ylabel('amplitude (A)')
            plt.show()
            plt.gca().invert_yaxis()

        # FFT the channel, log transform output, find local maxima, then return
        # locally sensitive hashes.
        # FFT the signal and extract frequency components

        # plot the angle spectrum of segments within the signal in a colormap
        arr2D = mlab.specgram(
            channel_samples,
            NFFT=wsize,
            Fs=Fs,
            window=mlab.window_hanning,
            noverlap=int(wsize * wratio))[0]

        # show spectrogram plot
        if plots:
            plt.plot(arr2D)
            plt.title('FFT')
            plt.show()

        # apply log transform since specgram() returns linear array
        # calculates the base 10 logarithm for all elements of arr2D
        np.seterr(divide='ignore')
        arr2D = 10 * np.log10(arr2D)
        np.seterr(divide='warn')
        
        arr2D[arr2D == -np.inf] = 0  # replace infs with zeros

        # find local maxima
        local_maxima = self._get_2D_peaks(arr2D, plot=plots, amp_min=amp_min)

        msg = '   local_maxima: %d of frequency & time pairs'
        print(msg % len(local_maxima))

        # return hashes
        return self._generate_hashes(local_maxima, fan_value=fan_value)

    def _get_2D_peaks(self, arr2D, plot=False, amp_min=DEFAULT_AMP_MIN):
        # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
        struct = generate_binary_structure(2, 1)
        neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

        # find local maxima using our fliter shape
        local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
        background = (arr2D == 0)
        eroded_background = binary_erosion(background, structure=neighborhood,
                                           border_value=1)

        # Boolean mask of arr2D with True at peaks
        detected_peaks = local_max ^ eroded_background

        # extract peaks
        amps = arr2D[detected_peaks]
        j, i = np.where(detected_peaks)

        # filter peaks
        amps = amps.flatten()
        peaks = zip(i, j, amps)
        peaks_filtered = [x for x in peaks if x[2]
                          > amp_min]  # freq, time, amp

        # get indices for frequency and time
        frequency_idx = [x[1] for x in peaks_filtered]
        time_idx = [x[0] for x in peaks_filtered]

        # scatter of the peaks
        if plot:
            fig, ax = plt.subplots()
            ax.imshow(arr2D)
            ax.scatter(time_idx, frequency_idx)
            ax.set_xlabel('Time')
            ax.set_ylabel('Frequency')
            ax.set_title("Spectrogram")
            plt.gca().invert_yaxis()
            plt.show()

        return list(zip(frequency_idx, time_idx))

    # Hash list structure: sha1_hash[0:20] time_offset
    # example: [(e05b341a9b77a51fd26, 32), ... ]

    def _generate_hashes(self, peaks, fan_value=DEFAULT_FAN_VALUE):
        if PEAK_SORT:
            peaks = sorted(peaks, key=itemgetter(1))

        # bruteforce all peaks
        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks):

                    # take current & next peak frequency value
                    freq1 = peaks[i][IDX_FREQ_I]
                    freq2 = peaks[i + j][IDX_FREQ_I]

                    # take current & next -peak time offset
                    t1 = peaks[i][IDX_TIME_J]
                    t2 = peaks[i + j][IDX_TIME_J]

                    # get diff of time offsets
                    t_delta = t2 - t1

                    # check if delta is between min & max
                    if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                        h = hashlib.sha1(
                            f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode())
                        yield (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)
