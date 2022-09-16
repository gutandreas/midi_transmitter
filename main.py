import tkinter
from tkinter import Tk, StringVar, HORIZONTAL, Scale, SUNKEN, DISABLED, ACTIVE, NORMAL, RIDGE
from tkinter.ttk import *
from rtmidi import *
from tkmacosx import Button
from ttkthemes import ThemedTk

threads = []
midiin = rtmidi.RtMidiIn()
midiout = rtmidi.RtMidiOut()
rec = False
added_interval = 0
interval_direction = 0

backgroundcolor = "#ECECEC"
color_1 = "lightblue"


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


# def update_midi_devices():


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


def get_direction():
    return ["Richtung", "Aufwärts", "Abwärts"]


def connect_midi_in(selection):
    stop()
    midiin.closePort()
    counter = -1
    for device in get_midi_devices_in():
        if device == selection:
            print(device + " connected as input")
            midiin.openPort(counter)
        counter += 1


def connect_midi_out(selection):
    stop()
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


def set_interval_direction(direction):
    print("Intervallrichtung: " + direction)
    counter = -1
    global interval_direction
    for d in get_direction():
        if d == direction:
            interval_direction = counter
        counter += 1


def record(*args):
    global rec
    rec = True
    thread = threading.Thread(target=record_in_thread)
    thread.start()
    button_record.config(background="grey", state=DISABLED)
    button_stop.config(background="red", state=NORMAL)


def send_prg_change():
    bank = int(entry_bank.get())
    preset = int(entry_presetnumber.get())
    if bank <= 8:
        cc = rtmidi.MidiMessage.controllerEvent(1, 0, 0)
    else:
        cc = rtmidi.MidiMessage.controllerEvent(1, 0, 127)
    midiout.sendMessage(cc)
    message = rtmidi.MidiMessage.programChange(1, (bank - 1) * 16 + preset - 1)
    midiout.sendMessage(message)


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
        if interval_direction == 0:
            message.setNoteNumber(original_note + added_interval)
            midiout.sendMessage(message)
            show_note_in_scale(message, "blue")
        else:
            message.setNoteNumber(original_note - added_interval)
            midiout.sendMessage(message)
            show_note_in_scale(message, "blue")

    color_added_notes = "green"

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
        notes[number].config(foreground=color, background=color)
    if message.isNoteOff():
        number = message.getNoteNumber()
        print(number)
        notes[number].config(foreground="black", background=backgroundcolor)


def stop(*args):
    global rec
    rec = False
    button_record.config(background="lightgreen", state=NORMAL)
    button_stop.config(background="grey", state=DISABLED)


def choose_preset(number):
    buttons_preset[number - 1].config(background="#FF9999")
    for i in range(5):
        if i != number - 1:
            buttons_preset[i].config(background="lightblue")


# Window
window = ThemedTk(theme="aqua")
window.title("Miditransmitter")  # setzt den Fenstertitel
window.resizable(width=False, height=False)  # fixiert die Fenstergrösse
window.configure(background="#ECECEC")
window.geometry("900x400")



frame_rec_buttons = Frame(window)
button_record = Button(master=frame_rec_buttons, text="rec.", command=record, underline=0, background="lightgreen",
                       highlightbackground=backgroundcolor, state=DISABLED)
button_record.pack(side="left")
button_stop = Button(master=frame_rec_buttons, text="stop", command=stop, underline=0, background="red",
                     highlightbackground=backgroundcolor, state=DISABLED)
button_stop.pack(side="left")


frame_input = Frame(window)
label_input = Label(master=frame_input, text="Eingang")
label_input.pack()
clicked_in = StringVar()
optionmenu_devices_in = OptionMenu(frame_input, clicked_in, *get_midi_devices_in(), command=connect_midi_in)
optionmenu_devices_in.pack()
optionmenu_devices_in.config(width=20)
# button_update = Button(command=update_midi_devices, text="Update")

frame_output = Frame(window)
label_output = Label(master=frame_output, text="Ausgang")
label_output.pack()
clicked_out = StringVar()
optionmenu_devices_out = OptionMenu(frame_output, clicked_out, *get_midi_devices_out(), command=connect_midi_out)
optionmenu_devices_out.pack()
optionmenu_devices_out.config(width=20)

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
        label = Label(note_frames[0], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 12 and i < 24:
        label = Label(note_frames[1], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 24 and i < 36:
        label = Label(note_frames[2], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 36 and i < 48:
        label = Label(note_frames[3], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 48 and i < 60:
        label = Label(note_frames[4], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 60 and i < 72:
        label = Label(note_frames[5], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 72 and i < 84:
        label = Label(note_frames[6], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 84 and i < 96:
        label = Label(note_frames[7], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 96 and i < 108:
        label = Label(note_frames[8], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 108 and i < 120:
        label = Label(note_frames[9], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")
    if i >= 120 and i < 132:
        label = Label(note_frames[10], text=note_names[i], width=3, relief=RIDGE, anchor="center", font="Helvetica 20")
        label.pack(side="left")

    notes.append(label)

# Presets
frame_preset_area = Frame(window)

label_presets = Label(master=frame_preset_area, text="Presets:")
label_presets.pack(side="left")

buttons_preset = []
frame_presetbuttons = Frame(frame_preset_area)
frame_presetbuttons.pack(side="left")

button1 = Button(frame_presetbuttons, text=1, width=50, command=lambda: choose_preset(1),
                 highlightbackground=backgroundcolor, background=color_1)
button1.pack(side="left")
buttons_preset.append(button1)

button2 = Button(frame_presetbuttons, text=2, width=50, command=lambda: choose_preset(2),
                 highlightbackground=backgroundcolor, background=color_1)
button2.pack(side="left")
buttons_preset.append(button2)

button3 = Button(frame_presetbuttons, text=3, width=50, command=lambda: choose_preset(3),
                 highlightbackground=backgroundcolor, background=color_1)
button3.pack(side="left")
buttons_preset.append(button3)

button4 = Button(frame_presetbuttons, text=4, width=50, command=lambda: choose_preset(4),
                 highlightbackground=backgroundcolor, background=color_1)
button4.pack(side="left")
buttons_preset.append(button4)

button5 = Button(frame_presetbuttons, text=5, width=50, command=lambda: choose_preset(5),
                 highlightbackground=backgroundcolor, background=color_1)
button5.pack(side="left")
buttons_preset.append(button5)


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
slider_transpose = tkinter.Scale(master=frame_transpose, from_=-3, to=3, tickinterval=1, orient=HORIZONTAL,
                                 troughcolor=color_1, background=backgroundcolor, font="Helvetica 10")
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
clicked_up_down = StringVar()
optionmenu_interval_up_down = OptionMenu(frame_added_interval, clicked_up_down, *get_direction(),
                                         command=set_interval_direction)
optionmenu_interval_up_down.pack(side="left")

# Program Change
frame_program_change = Frame(window)
label_program_change = Label(master=frame_program_change, text="Prg. Change:")
label_program_change.pack(side="left")
label_bank = Label(master=frame_program_change, text="Bank")
label_bank.pack(side="left")
entry_bank = Entry(master=frame_program_change, width=2)
entry_bank.pack(side="left")
label_presetnumber = Label(master=frame_program_change, text="Preset")
label_presetnumber.pack(side="left")
entry_presetnumber = Entry(master=frame_program_change, width=2)
entry_presetnumber.pack(side="left")
button_prgram_change = Button(master=frame_program_change, text="Send", command=send_prg_change,
                              highlightbackground=backgroundcolor)
button_prgram_change.pack(side="left")

# Grid

frame_input.grid(row=0, column=0)
frame_output.grid(row=0, column=1)
# button_update.grid(row=0, column=3)
frame_preset_area.grid(row=3, column=2, sticky="w")
frame_rec_buttons.grid(row=0, column=2, sticky="w")
# frame_delay.grid(row=14, column=0)
frame_transpose.grid(row=4, column=2, rowspan=2, sticky="w")
frame_added_octaves.grid(row=6, column=2, sticky="w")
frame_added_interval.grid(row=7, column=2, sticky="w")
frame_program_change.grid(row=8, column=2, sticky="w")

for i in range(11):
    note_frames[i].grid(row=i + 3, column=0, columnspan=2)

# Bind

window.bind('<r>', record)
window.bind('<s>', stop)

# Run the application
window.mainloop()
