import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.graphics import tsaplots


graphData = pd.read_csv(".\\src\\project\\data\\Graph Data\\element_32-Ge_n-tot.csv", header=None)
corr = graphData.T.corr('pearson')
x, y = graphData.iloc[:, 0].to_numpy(), graphData.iloc[:, 1].to_numpy()


# fig = plt.figure()
# plt.plot(corr)
# plt.show()
# def apply_fft(x, y):
#     # Apply Fast Fourier Transform (FFT)
#     fft_values = np.abs(scipy.fftpack.fft(y))
#     freqs = scipy.fftpack.fftfreq(len(x), d=(x[1] - x[0]))  # Compute frequency axis

#     return freqs[:len(freqs) // 2], fft_values[:len(freqs) // 2]  # Return positive frequencies only


# # Example usage with energy and cross-section data
# freqs, fft_values = apply_fft(x, y)

# # Plot FFT spectrum
# plt.figure(figsize=(10, 5))
# plt.plot(freqs, fft_values, label="FFT Spectrum")
# plt.plot(x, y)
# plt.xlabel("Frequency (1/eV)")
# plt.ylabel("Amplitude")
# plt.title("Fourier Transform of Resonance Spectrum")
# plt.legend()
# plt.show()


import pywt

# Apply Continuous Wavelet Transform (CWT)
coeffs, freqs = pywt.cwt(y, scales=np.arange(1, 128), wavelet='morl')

plt.imshow(coeffs, aspect='auto', extent=[x.min(), x.max(), freqs.min(), freqs.max()])
plt.xlabel("Energy (eV)")  # Keep original energy values
plt.ylabel("Wavelet Scale")
plt.title("Wavelet Transform of Resonance Spectrum")
plt.colorbar(label="Coefficient Magnitude")
plt.show()


import numpy as np
import pywt
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


# Step 1: Find peaks in the original cross-section data
peaks, _ = find_peaks(y, height=2)  # Detect peaks

# Step 2: Compute Continuous Wavelet Transform (CWT)
scales = np.arange(1, 30)  # Define scale range (captures different peak widths)
coeffs, _ = pywt.cwt(y, scales, wavelet='morl')  # Compute wavelet transform

# Step 3: Extract wavelet features at detected peak positions
wavelet_features_at_peaks = coeffs[:, peaks]  # Extract coefficients at peak positions

# Step 4: Map extracted wavelet features back to energy values
energy_peaks = x[peaks]  # Get corresponding energy values for peaks

# Print extracted features
for i, e in enumerate(energy_peaks):
    print(f"Energy {e} eV -> Wavelet Coefficients {wavelet_features_at_peaks[:, i]}")

# Optional: Visualize the wavelet coefficients at peaks
plt.figure(figsize=(10, 5))
for i, peak_idx in enumerate(peaks):
    plt.plot(scales, wavelet_features_at_peaks[:, i], label=f'Peak at {x[peak_idx]} eV')

plt.xlabel("Wavelet Scale")
plt.ylabel("Wavelet Coefficient Magnitude")
plt.title("Wavelet Features Extracted at Peak Positions")
plt.legend()
plt.show()
