"""
TDMS Signal Visualization Script (Time & Frequency Domains).
I was only capable of writing this script after doing an
exploratory analysis of the sample file... in other words,
I tryed this, I failled, I explored the file, I learned something,
I came back here, I got some level of sucess...

Purpose:
    Reads a specific channel from a NI TDMS file and plots:
    1. The raw signal waveform (Voltage vs Time).
    2. The frequency spectrum (FFT Magnitude vs Frequency).

Usage:
    Adjust the 'Configuration' section constants to match your file path
    and channel structure.
    
    Note: 'CUT_DURATION' limits the amount of data loaded to prevent 
    memory overflow on large files. Set to None to read the full file.
    As uncle Ben said once: "With great computers comes great RAM usage!!!"

Powered by:
    Goryunov @2025
    This script is the result of going home without stoping at the supermarket
    to buy a pack o beer... mental note: NEVER do it again.
"""

import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile
from scipy.fft import fft, fftfreq

# --- CONFIGURATION ---
FILE_PATH = 'LogFile_2025-11-21-17-30-18.tdms'
GROUP_NAME = 'Log'
CHANNEL_NAME = 'Dev1/ai0'

# Limit data loading to avoid freezing the PC with huge files
# Set to 'None' to load the entire file (!DANGER!).
# This should be updated to support a "signal slice" in the future
CUT_DURATION = 3.0 # in seconds
# CUT_DURATION = None

try:
    print(f"Loading TDMS file: {FILE_PATH} ...")
    tdms_file = TdmsFile.read(FILE_PATH)
    
    # Accessing the specific channel
    channel = tdms_file[GROUP_NAME][CHANNEL_NAME]
    
    # Extracting metadata
    # 'wf_increment' is the time step (dt). Fs = 1 / dt
    # wf stands for We are Fucked... no it is not, just kidding
    fs = 1.0 / channel.properties.get('wf_increment', 1e-6) # Default to 1MHz if missing
    total_points = len(channel)
    
    print(f"Sampling Rate (Fs): {fs/1000:.2f} kHz") # Show in kHz, just because I like it better
    print(f"Total points in file: {total_points}")

    # --- DATA SLICING (Memory Management) ---
    if CUT_DURATION:
        points_to_read = int(CUT_DURATION * fs)
        # Ensure we don't try to read more points than available
        points_to_read = min(points_to_read, total_points)
        
        print(f"Reading first {CUT_DURATION} seconds ({points_to_read} points)...")
        data = channel[:points_to_read]
    else:
        print("Reading the FULL file (Warning: Check your RAM usage)...")
        data = channel[:] 

    # Create Time Vector: from 0 to N/Fs
    time_axis = np.linspace(0, len(data) / fs, num=len(data))

    # --- PLOTTING ---
    print("Generating plots...")
    plt.figure(figsize=(12, 10))
    
    # 1. Time Domain Plot (Waveform)
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, data, color='#1f77b4', linewidth=0.5) # Standard Blue
    plt.title(f"Acoustic Signal - First {time_axis[-1]:.2f}s")
    plt.ylabel("Amplitude (V)")
    plt.xlabel("Time (s)")
    plt.grid(True, alpha=0.3)
    
    # 2. Frequency Domain Plot (FFT)
    # Source: https://pysdr.org/content/frequency_domain.html
    # Step A: Remove DC Offset (Mean) to visualize AC signal peaks better
    data_no_offset = data - np.mean(data)
    
    # Step B: Compute FFT
    n_samples = len(data_no_offset)
    fft_values = fft(data_no_offset)
    freq_axis = fftfreq(n_samples, 1 / fs)
    
    # Step C: Plot (Only positive frequencies, up to Nyquist limit)
    plt.subplot(2, 1, 2)
    half_n = n_samples // 2
    
    # Note: 2.0/n is the normalization factor to get true magnitude
    fft_magnitude = 2.0 / n_samples * np.abs(fft_values[:half_n])
    
    plt.plot(freq_axis[:half_n], fft_magnitude, color='#d62728', linewidth=0.5) # Red
    plt.title("Frequency Spectrum (FFT)")
    plt.ylabel("Magnitude")
    plt.xlabel("Frequency (Hz)")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout(h_pad=2.0)
    plt.show()

except KeyError:
    print(f"ERROR: Could not find Group '{GROUP_NAME}' or Channel '{CHANNEL_NAME}'.")
    print("Tip: Run the exploration script to check the exact internal names.")
except Exception as e:
    print(f"An unexpected error occurred (now we cry): {e}")