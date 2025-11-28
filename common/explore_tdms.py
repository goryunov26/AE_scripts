"""
TDMS File Explorer script.

Purpose:
    This script inspects the internal structure (Groups -> Channels) of TDMS files.
    Why am I doing it? Because I forgot to ask Ediblu about the expected structure.
    
Context:
    Standard NI documentation suggests a hierarchy that differs from the
    specific lab results file. This script helps identify where the raw data 
    and sampling rates are stored before processing.
    NI source material: https://pypi.org/project/npTDMS/

Usage:
    Update 'path_to_file' variable and run.
    This should be automated in the future.

Powered by:
    Goryunov @2025
    This script is the result of going home without stoping at the supermarket
    to buy a pack o beer... mental note: NEVER do it again.
"""

from nptdms import TdmsFile

# --- Configuration ---
path_to_file = 'LogFile_2025-11-21-17-30-18.tdms'

try:
    # Read the file structure (metadata is loaded, raw data is loaded on demand)
    tdms_file = TdmsFile.read(path_to_file)
    print(f"--- Exploring file: {path_to_file} ---\n")

    # 1. Loop to check all 'Groups'
    for group in tdms_file.groups():
        print(f"📁 GROUP: '{group.name}'")
        
        if group.properties:
            print(f"   Group Properties: {group.properties}")
        
        # Get list of channels in this group
        channels = group.channels()
        
        if not channels:
            print("   (This group has no channels/data))")
        
        # 2. Loop all channels inside each group
        for channel in channels:
            channel_name = channel.name
            data_length = len(channel)
            
            # Extract a small sample (first 5 points) to preview data
            if data_length > 0:
                sample = channel[:5] 
                print(f"   └─ 📊 CHANNEL: '{channel_name}'")
                print(f"        Total N. of points: {data_length}")
                print(f"        First Values: {sample}")
                
                # Check time information to calculate Sampling Rate (Fs)
                if 'wf_increment' in channel.properties:
                    dt = channel.properties['wf_increment']
                    fs = 1.0 / dt if dt else 0
                    print(f"        Sampling Rate (Fs): {fs:.2f} Hz")
            else:
                print(f"   └─ 📄 CHANNEL: '{channel_name}' (Empty or just metadata)")
                print(f"        Properties: {channel.properties}")
        
        print("-" * 40) # Visual separator

except Exception as e:
    print(f"Error trying to read the file: {e}")