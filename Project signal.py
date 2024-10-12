import pygame
import sys
import numpy as np
import soundfile as sf
import tkinter as tk
from pedalboard import Pedalboard, Reverb, Chorus, LowpassFilter, PitchShift, Phaser, Clipping
from pygame import sndarray


def apply_effects():
    global processed_audio, reverb_room_size, chorus_depth, lowpass_cutoff, pitch_shift_semi, clipping_gain

    board = Pedalboard([])

    if reverb_room_size > 0:
        board.append(Reverb(room_size=reverb_room_size))
    if chorus_depth > 0:
        board.append(Chorus(depth=chorus_depth))
    if lowpass_cutoff < 20000:
        board.append(LowpassFilter(cutoff_frequency_hz=lowpass_cutoff))
    if pitch_shift_semi != 0:
        board.append(PitchShift(semitones=pitch_shift_semi))
    if clipping_gain != 0:
        board.append(Clipping(threshold_db=clipping_gain))

    board.append(Phaser())
    processed_audio = board(audio_data, sample_rate)
    processed_audio = np.clip(processed_audio, -1.0, 1.0)
    processed_audio = (processed_audio * 32767).astype(np.int16)


def play_music():
    global running, processed_audio, current_sound
    if processed_audio is None:
        apply_effects()
    current_sound = sndarray.make_sound(processed_audio)
    current_sound.play(-1)


def stop_music():
    global running
    running = False
    pygame.mixer.stop()


def on_closing():
    stop_music()
    root.destroy()


def adjust_volume(val):
    global current_sound
    volume = int(val) / 100
    if current_sound:
        current_sound.set_volume(volume)


def update_reverb(val):
    global reverb_room_size
    reverb_room_size = int(val) / 100


def update_chorus(val):
    global chorus_depth
    chorus_depth = int(val) / 100


def update_lowpass(val):
    global lowpass_cutoff
    lowpass_cutoff = int(val)


def update_pitch_shift(val):
    global pitch_shift_semi
    pitch_shift_semi = int(val)


def update_clipping(val):
    global clipping_gain
    clipping_gain = int(val)


def start_music():
    stop_music()
    apply_effects()
    play_music()


# Function to reset all sliders and effect values
def reset_sliders():
    global reverb_room_size, chorus_depth, lowpass_cutoff, pitch_shift_semi, clipping_gain

    # Reset effect values to their default settings
    reverb_room_size = 0
    chorus_depth = 0
    lowpass_cutoff = 20000
    pitch_shift_semi = 0
    clipping_gain = 0

    # Reset the slider positions
    reverb_slider.set(int(reverb_room_size * 100))
    chorus_slider.set(int(chorus_depth * 100))
    lowpass_slider.set(lowpass_cutoff)
    pitch_shift_slider.set(pitch_shift_semi)
    clipping_slider.set(clipping_gain)

    # Apply the reset effects and restart music if needed
    apply_effects()


# Initialize pygame
pygame.init()

# Load audio data
starman = r"C:\Users\mckra\Downloads\python_practical\music\Its My Life ｜ Sri Lankan Version ｜ Sandaru Sathsara.wav"
audio_data, sample_rate = sf.read(starman)

# Initialize global variables
reverb_room_size = 0
chorus_depth = 0  # Default chorus depth
lowpass_cutoff = 20000  # Default cutoff frequency for Lowpass Filter (max frequency means no filtering)
pitch_shift_semi = 0  # Default pitch shift in semitones (no shift)
clipping_gain = 0  # Default clipping gain (no clipping)
running = False
processed_audio = None
current_sound = None  # Track the currently playing sound

# Tkinter window setup
root = tk.Tk()
root.geometry('500x800')
root.title('Music Player')

# Play button
play_button = tk.Button(root, text='Play music', command=start_music, bg='#4CAF50', fg='#ffffff')
play_button.pack(pady=20)
play_button.config(width='10', height='2')

# Stop button
stop_button = tk.Button(root, text='Stop music', command=stop_music, bg='#f44336', fg='#ffffff')
stop_button.pack(pady=20)
stop_button.config(width='10', height='2')

# Volume slider
volume_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=adjust_volume, label='Volume')
volume_slider.set(50)  # Set the initial volume to 50%
volume_slider.pack(pady=10)

# Reverb slider (applies reverb before playing)
reverb_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_reverb, label='Reverb Room Size')
reverb_slider.set(int(reverb_room_size * 100))  # Set initial reverb room size
reverb_slider.pack(pady=10)

# Chorus depth slider (applies chorus before playing)
chorus_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_chorus, label='Chorus Depth')
chorus_slider.set(int(chorus_depth * 100))  # Set initial chorus depth
chorus_slider.pack(pady=10)

# Lowpass filter cutoff frequency slider (applies Lowpass Filter before playing)
lowpass_slider = tk.Scale(root, from_=20, to=20000, orient='horizontal', command=update_lowpass,
                          label='Lowpass Cutoff (Hz)')
lowpass_slider.set(lowpass_cutoff)  # Set initial cutoff frequency
lowpass_slider.pack(pady=10)

# Pitch shift slider (applies Pitch Shift before playing)
pitch_shift_slider = tk.Scale(root, from_=-12, to=12, orient='horizontal', command=update_pitch_shift,
                              label='Pitch Shift (semitones)')
pitch_shift_slider.set(pitch_shift_semi)  # Set initial pitch shift
pitch_shift_slider.pack(pady=10)

# Clipping gain slider (applies Clipping before playing)
clipping_slider = tk.Scale(root, from_=-20, to=20, orient='horizontal', command=update_clipping,
                           label='Clipping Gain (dB)')
clipping_slider.set(clipping_gain)  # Set initial clipping gain
clipping_slider.pack(pady=10)

# Reset button to reset all sliders to their initial values
reset_button = tk.Button(root, text='Reset', command=reset_sliders, bg='#FFC107', fg='#ffffff')
reset_button.pack(pady=20)
reset_button.config(width='10', height='2')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

pygame.quit()
sys.exit()
