import pygame
import sys
import numpy as np
import soundfile as sf
import tkinter as tk
from tkinter import filedialog
from pedalboard import Pedalboard, Reverb, Chorus, LowpassFilter, PitchShift, Clipping, Distortion, Gain
from pygame import sndarray

print('Hello user! First load our favorite song in .wav format. Then tweak the effects how you like them, and start the song! Unfortunately, the effects \ndo not update in real time so to change them again you have to stop the song, change them, and then you are ready to go! It may take a couple of seconds...')

def apply_effects():
    global processed_audio, audio_data, sample_rate, reverb_room_size, chorus_depth, lowpass_cutoff, pitch_shift_semi, clipping_gain, gain, distortion

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
    if gain != 0:
        board.append(Gain(gain_db=gain))
    if distortion != 0:
        board.append(Distortion(drive_db=distortion))

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

def update_gain(val):
    global gain
    gain = int(val)

def update_distortion(val):
    global distortion
    distortion = int(val)

def start_music():
    stop_music()
    apply_effects()
    play_music()


def reset_sliders():
    global reverb_room_size, chorus_depth, lowpass_cutoff, pitch_shift_semi, clipping_gain, gain, distortion

    reverb_room_size = 0
    chorus_depth = 0
    lowpass_cutoff = 20000
    pitch_shift_semi = 0
    clipping_gain = 0
    gain = 0
    distortion = 0

    reverb_slider.set(int(reverb_room_size * 100))
    chorus_slider.set(int(chorus_depth * 100))
    lowpass_slider.set(lowpass_cutoff)
    pitch_shift_slider.set(pitch_shift_semi)
    clipping_slider.set(clipping_gain)
    gain_slider.set(gain)
    distortion_slider.set(distortion)

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


def save_file():
    """Function to save the processed audio data to a file."""
    global processed_audio
    if processed_audio is None:
        print("No processed audio to save.")
        return

    # Open a file dialog to select save location
    file_path = filedialog.asksaveasfilename(
        title="Save processed audio",
        defaultextension=".wav",
        filetypes=[("WAV Files", "*.wav")]
    )

    if file_path:
        # Save the processed audio using soundfile
        sf.write(file_path, processed_audio, sample_rate)
        print(f"File saved to {file_path}")


class ToolTip:
    def __init__(self, widget, text, delay=1000):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = delay
        self.after_id = None

        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_tooltip(self, event):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 100
        y += self.widget.winfo_rooty() + 5

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, background="#dee9fa", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

pygame.init()

#global variables
reverb_room_size = 0
chorus_depth = 0
lowpass_cutoff = 20000
pitch_shift_semi = 0
clipping_gain = 0
gain = 0
distortion = 0
running = False
processed_audio = None
current_sound = None

#tkinter window
root = tk.Tk()
root.geometry('500x800')
root.title('Music Player')

#assigning buttons and sliders to columns and rows
root.grid_columnconfigure(0, weight=1) #blank
root.grid_columnconfigure(1, weight=1) #blank
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1) #blank
root.grid_columnconfigure(5, weight=1) #blank

button_frame = tk.Frame(root)
button_frame.grid(row=0, column=2, sticky='nsew')

slider_frame = tk.Frame(root)
slider_frame.grid(row=0, column=3, sticky='nsew')

#buttons
load_button = tk.Button(root, text='Load music', command=load_file, bg='#335C67', fg='#ffffff', width='20')
load_button.config(width='10', height='2')
load_button.grid(row=0, column=2, sticky='ew')
ToolTip(load_button, "Load the audio you want to play", delay=1000)

play_button = tk.Button(root, text='Play music', command=start_music, bg='#31854d', fg='#ffffff', width='20')
play_button.config(width='10', height='2')
play_button.grid(row=1, column=2, sticky='ew')
ToolTip(play_button, "Start the audio playback", delay=1000)

stop_button = tk.Button(root, text='Stop music', command=stop_music, bg='#E09F3E', fg='#ffffff', width='20')
stop_button.config(width='10', height='2')
stop_button.grid(row=2, column=2, sticky='ew')
ToolTip(stop_button, "Stop the audio playback", delay=1000)

reset_button = tk.Button(root, text='Reset', command=reset_sliders, bg='#9E2A2B', fg='#ffffff', width='20')
reset_button.config(width='10', height='2')
reset_button.grid(row=3, column=2, sticky='ew')
ToolTip(reset_button, "Reset all the sliders to their original position", delay=1000)

save_button = tk.Button(root, text='Save audio', command=save_file, bg='#540B0E', fg='#ffffff', width='20')
save_button.config(width='10', height='2')
save_button.grid(row=4, column=2, sticky='ew')
ToolTip(save_button, "Save processed audio to your computer", delay=1000)

#sliders
volume_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=adjust_volume, label='Volume', length='150')
volume_slider.set(50)
volume_slider.config(length='150')
volume_slider.grid(row=0, column=3, sticky='ew')

reverb_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_reverb, label='Reverb Room Size', length='150')
reverb_slider.set(int(reverb_room_size * 100))
reverb_slider.grid(row=1, column=3, sticky='ew')

chorus_slider = tk.Scale(root, from_=0, to=100, orient='horizontal', command=update_chorus, label='Chorus Depth', length='150')
chorus_slider.set(int(chorus_depth * 100))
chorus_slider.grid(row=2, column=3, sticky='ew')

lowpass_slider = tk.Scale(root, from_=20, to=20000, orient='horizontal', command=update_lowpass, label='Lowpass Cutoff (Hz)', length='150')
lowpass_slider.set(lowpass_cutoff)
lowpass_slider.grid(row=3, column=3, sticky='ew')

pitch_shift_slider = tk.Scale(root, from_=-12, to=12, orient='horizontal', command=update_pitch_shift, label='Pitch Shift (semitones)', length='150')
pitch_shift_slider.set(pitch_shift_semi)
pitch_shift_slider.grid(row=4, column=3, sticky='ew')

clipping_slider = tk.Scale(root, from_=-20, to=20, orient='horizontal', command=update_clipping, label='Clipping Gain (dB)', length='150')
clipping_slider.set(clipping_gain)
clipping_slider.grid(row=5, column=3, sticky='ew')
ToolTip(clipping_slider, "Add gain to the song. Negative values increase gain while positive values", delay=1000)

gain_slider = tk.Scale(root, from_=-50, to=50, orient='horizontal', command=update_gain, label='Gain (db)', length='150')
gain_slider.set(gain)
gain_slider.grid(row=6, column=3, sticky='ew')

distortion_slider = tk.Scale(root, from_=0, to=50, orient='horizontal', command=update_distortion, label='Distortion (db)', length='150')
distortion_slider.set(distortion)
distortion_slider.grid(row=7, column=3, sticky='ew')

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

pygame.quit()
sys.exit()
