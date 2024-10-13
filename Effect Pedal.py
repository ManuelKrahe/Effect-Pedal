import pygame
import sys
import numpy as np
import soundfile as sf
import tkinter as tk
from tkinter import filedialog
from pedalboard import Pedalboard, Reverb, Chorus, LowpassFilter, PitchShift, Phaser, Clipping
from pygame import sndarray

print('Hello user! First load our favorite song in .wav format. Then tweak the effects how you like them, and start the song! Unfortunately, the effects \ndo not update in real time so to change them again you have to stop the song, change them, and then you are ready to go! It may take a couple of seconds...')


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

    processed_audio = board(audio_data, sample_rate)

    if processed_audio.ndim == 1:
        processed_audio = np.stack([processed_audio, processed_audio], axis=1)

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


def reset_sliders():
    global reverb_room_size, chorus_depth, lowpass_cutoff, pitch_shift_semi, clipping_gain

    reverb_room_size = 0
    chorus_depth = 0
    lowpass_cutoff = 20000
    pitch_shift_semi = 0
    clipping_gain = 0

    reverb_slider.set(int(reverb_room_size * 100))
    chorus_slider.set(int(chorus_depth * 100))
    lowpass_slider.set(lowpass_cutoff)
    pitch_shift_slider.set(pitch_shift_semi)
    clipping_slider.set(clipping_gain)

    apply_effects()


def load_file():
    global audio_data, sample_rate
    file_path = filedialog.askopenfilename(
        title="Select a WAV file",
        filetypes=[("WAV Files", "*.wav")]
    )
    if file_path:
        audio_data, sample_rate = sf.read(file_path)
        if audio_data.ndim == 1:
            audio_data = np.stack([audio_data, audio_data], axis=1)
        reset_sliders()



pygame.init()

#global variables
reverb_room_size = 0
chorus_depth = 0
lowpass_cutoff = 20000
pitch_shift_semi = 0
clipping_gain = 0
running = False
processed_audio = None
current_sound = None

#tkinter window
root = tk.Tk()
root.geometry('500x800')
root.title('Music Player')

#buttons
load_button = tk.Button(root, text='Load music', command=load_file, bg='#2196F3', fg='#ffffff')
load_button.pack(pady=20)
load_button.config(width='10', height='2')

play_button = tk.Button(root, text='Play music', command=start_music, bg='#4CAF50', fg='#ffffff')
play_button.pack(pady=20)
play_button.config(width='10', height='2')

stop_button = tk.Button(root, text='Stop music', command=stop_music, bg='#f44336', fg='#ffffff')
stop_button.pack(pady=20)
stop_button.config(width='10', height='2')

volume_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=adjust_volume, label='Volume')
volume_slider.set(50)
volume_slider.pack(pady=10)

reverb_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_reverb, label='Reverb Room Size')
reverb_slider.set(int(reverb_room_size * 100))
reverb_slider.pack(pady=10)

chorus_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_chorus, label='Chorus Depth')
chorus_slider.set(int(chorus_depth * 100))
chorus_slider.pack(pady=10)

lowpass_slider = tk.Scale(root, from_=20, to=20000, orient='horizontal', command=update_lowpass, label='Lowpass Cutoff (Hz)')
lowpass_slider.set(lowpass_cutoff)
lowpass_slider.pack(pady=10)

pitch_shift_slider = tk.Scale(root, from_=-12, to=12, orient='horizontal', command=update_pitch_shift, label='Pitch Shift (semitones)')
pitch_shift_slider.set(pitch_shift_semi)
pitch_shift_slider.pack(pady=10)

clipping_slider = tk.Scale(root, from_=-20, to=20, orient='horizontal', command=update_clipping, label='Clipping Gain (dB)')
clipping_slider.set(clipping_gain)
clipping_slider.pack(pady=10)

reset_button = tk.Button(root, text='Reset', command=reset_sliders, bg='#FFC107', fg='#ffffff')
reset_button.pack(pady=20)
reset_button.config(width='10', height='2')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

pygame.quit()
sys.exit()