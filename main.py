import copy
import threading
import time
import tkinter
from tkinter import Tk, StringVar, HORIZONTAL, Scale
from tkinter.ttk import *

import rtmidi

threads = []
midiin = rtmidi.RtMidiIn()
midiout = rtmidi.RtMidiOut()
rec = False
added_interval = 0


def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())


def get_midi_devices_in():
    ports = range(midiin.getPortCount())
    devices = []
    devices.append("Eingangsgerät")
    for i in ports:
        devices.append(midiin.getPortName(i))

    return devices


def get_midi_devices_out():
    ports = range(midiout.getPortCount())
    devices = []
    devices.append("Ausgangsgerät")
    for i in ports:
        devices.append(midiout.getPortName(i))

    return devices


def get_intervals():
    return ["Ohne", "Kleine Sekunde", "Grosse Sekunde", "Kleine Terz", "Grosse Terz", "Quarte",
            "Tritonus", "Quinte", "Kleine Sexte", "Grosse Sexte", "Kleine Septime", "Grosse Septime"]


def connect_midi_in(selection):
    midiin.closePort()
    counter = -1
    for device in get_midi_devices_in():
        if device == selection:
            print(device + " connected as input")
            midiin.openPort(counter)
        counter += 1


def connect_midi_out(selection):
    midiout.closePort()
    counter = -1
    for device in get_midi_devices_out():
        if device == selection:
            print(device + " connected as output")
            midiout.openPort(counter)
        counter += 1

def set_added_interval(interval):
    print("Hinzugefügtes Intervall: " + interval)
    counter = 0
    global added_interval
    for i in get_intervals():
        if i == interval:
            added_interval = counter
            print("Verschiebung um " + str(counter) + " Halbtöne")
        counter += 1



def record(*args):
    global rec
    rec = True
    thread = threading.Thread(target=record_in_thread)
    thread.start()


def record_in_thread():
    while rec:
        m = midiin.getMessage(10)  # some timeout in ms
        if m:
            print_message(m)
            prepare_message(m)


def prepare_message(message):
    transposition = slider_transpose.get()
    print("Transposition: " + str(transposition))
    message.setNoteNumber(message.getNoteNumber() + transposition * 12)
    show_note_in_scale(message, "red")
    midiout.sendMessage(message)
    original_note = message.getNoteNumber()

    if added_interval != 0:
        message.setNoteNumber(original_note + added_interval)
        show_note_in_scale(message, "brown")


    color_added_notes = "orange"

    if checkbox_minus_2.instate(['selected']):
        message.setNoteNumber(original_note - 24)
        midiout.sendMessage(message)
        show_note_in_scale(message, color_added_notes)
    if checkbox_minus_1.instate(['selected']):
        message.setNoteNumber(original_note - 12)
        midiout.sendMessage(message)
        show_note_in_scale(message, color_added_notes)
    if checkbox_plus_1.instate(['selected']):
        message.setNoteNumber(original_note + 12)
        midiout.sendMessage(message)
        show_note_in_scale(message, color_added_notes)
    if checkbox_plus_2.instate(['selected']):
        message.setNoteNumber(original_note + 24)
        midiout.sendMessage(message)
        show_note_in_scale(message, color_added_notes)



def show_note_in_scale(message, color):
    if message.isNoteOn():
        number = message.getNoteNumber()
        print(number)
        notes[number].config(foreground=color)
    if message.isNoteOff():
        number = message.getNoteNumber()
        print(number)
        notes[number].config(foreground="black")


def stop():
    global rec
    rec = False


def choose_preset(number):
    label_chosen_preset.config(text="Preset: " + str(number))


# Window
window = Tk()  # erstellt das Fenster
window.title("Miditransmitter")  # setzt den Fenstertitel
window.resizable(width=False, height=False)  # fixiert die Fenstergrösse
window.configure(background="#ECECEC")
window.geometry("1200x750")
window.bind('<r>', record)

label_device = Label(text="Gerät", width=20)
label_preset = Label(text="Presets", width=20)
frame_rec_buttons = Frame(window, width=200)
button_record = Button(master=frame_rec_buttons, text="rec.", command=record, underline=0)
button_record.pack()
button_stop = Button(master=frame_rec_buttons, text="stop", command=stop)
button_stop.pack()

clicked_in = StringVar()
optionmenu_devices_in = OptionMenu(window, clicked_in, *get_midi_devices_in(), command=connect_midi_in)
optionmenu_devices_in.config(width=30)

clicked_out = StringVar()
optionmenu_devices_out = OptionMenu(window, clicked_out, *get_midi_devices_out(), command=connect_midi_out)
optionmenu_devices_out.config(width=30)

notes = []
note_names = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h",
              "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h"]

note_frames = []
for i in range(11):
    frame_notes = Frame(window)
    note_frames.append(frame_notes)

for i in range(132):
    if i >= 0 and i < 12:
        label = Label(note_frames[0], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 12 and i < 24:
        label = Label(note_frames[1], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 24 and i < 36:
        label = Label(note_frames[2], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 36 and i < 48:
        label = Label(note_frames[3], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 48 and i < 60:
        label = Label(note_frames[4], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 60 and i < 72:
        label = Label(note_frames[5], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 72 and i < 84:
        label = Label(note_frames[6], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 84 and i < 96:
        label = Label(note_frames[7], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 96 and i < 108:
        label = Label(note_frames[8], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 108 and i < 120:
        label = Label(note_frames[9], text=note_names[i], width=2)
        label.pack(side="left")
    if i >= 120 and i < 132:
        label = Label(note_frames[10], text=note_names[i], width=2)
        label.pack(side="left")

    notes.append(label)

# Presets
buttons_preset = []
frame_presetbuttons = Frame(window)
label_chosen_preset = Label(master=frame_presetbuttons, text="Preset: -")
label_chosen_preset.pack(side="right")

button1 = Button(frame_presetbuttons, text=1, width=2, command=lambda: choose_preset(1))
button1.pack(side="left")
buttons_preset.append(button1)

button2 = Button(frame_presetbuttons, text=2, width=2, command=lambda: choose_preset(2))
button2.pack(side="left")
buttons_preset.append(button2)

button3 = Button(frame_presetbuttons, text=3, width=2, command=lambda: choose_preset(3))
button3.pack(side="left")
buttons_preset.append(button3)

button4 = Button(frame_presetbuttons, text=4, width=2, command=lambda: choose_preset(4))
button4.pack(side="left")
buttons_preset.append(button4)

button5 = Button(frame_presetbuttons, text=5, width=2, command=lambda: choose_preset(5))
button5.pack(side="left")
buttons_preset.append(button5)


frame_presetbuttons.grid(row=1, column=1)

ports = range(midiin.getPortCount())
if ports:
    for i in ports:
        print(midiin.getPortName(i))
else:
    print('NO MIDI INPUT PORTS!')

# Delay
frame_delay = Frame(window)
label_delay = Label(master=frame_delay, text="Delay (ms):")
label_delay.pack(side="left")
entry_delay = Entry(master=frame_delay)
entry_delay.pack(side="left")

# Transpose
frame_transpose = Frame(window)
label_transpose = Label(master=frame_transpose, text="Transponieren:")
label_transpose.pack(side="left")
slider_transpose = tkinter.Scale(master=frame_transpose, from_=-3, to=3, tickinterval=1, orient=HORIZONTAL)
slider_transpose.pack(side="left")

# Added Octaves
frame_added_octaves = Frame(window)
label_added_octaves = Label(master=frame_added_octaves, text="Oktaven hinzufügen:")
label_added_octaves.pack(side="left")
checkbox_minus_2 = Checkbutton(master=frame_added_octaves, text="-2")
checkbox_minus_2.pack(side="left")
checkbox_minus_1 = Checkbutton(master=frame_added_octaves, text="-1")
checkbox_minus_1.pack(side="left")
checkbox_plus_1 = Checkbutton(master=frame_added_octaves, text="+1")
checkbox_plus_1.pack(side="left")
checkbox_plus_2 = Checkbutton(master=frame_added_octaves, text="+2")
checkbox_plus_2.pack(side="left")

# Added Interval
frame_added_interval = Frame(window)
label_added_interval = Label(master=frame_added_interval, text="Intervall hinzufügen:")
label_added_interval.pack(side="left")
clicked_intervals = StringVar()
optionmenu_interval = OptionMenu(frame_added_interval, clicked_intervals, *get_intervals(), command=set_added_interval)
optionmenu_interval.pack(side="left")



# Grid
label_device.grid(row=0, column=0)
optionmenu_devices_in.grid(row=0, column=1)
optionmenu_devices_out.grid(row=0, column=2)
label_preset.grid(row=1, column=0)
frame_rec_buttons.grid(row=2, column=0)
# frame_delay.grid(row=14, column=0)
frame_transpose.grid(row=15, column=0)
frame_added_octaves.grid(row=16, column=0)
frame_added_interval.grid(row=17, column=0)

for i in range(11):
    note_frames[i].grid(row=i + 3, column=0, columnspan=5)

# Run the application
window.mainloop()
