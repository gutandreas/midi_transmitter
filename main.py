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
added_interval_absolute = 0
added_interval_tonal = 0
interval_direction = 0
chosen_tonart = "Keine"

backgroundcolor = "#ECECEC"
color_1 = "lightblue"

dur_distances = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23]
moll_distances = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22]


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


def get_intervals_absolute():
    return ["Ohne", "Kleine Sekunde", "Grosse Sekunde", "Kleine Terz", "Grosse Terz", "Reine Quarte",
            "Tritonus", "Reine Quinte", "Kleine Sexte", "Grosse Sexte", "Kleine Septime", "Grosse Septime"]


def get_intervals_tonal():
    return ["Ohne", "Sekunde", "Terz", "Quarte", "Quinte", "Sexte", "Septime"]


def get_direction():
    return ["Richtung", "Aufwärts", "Abwärts"]


def get_tonart():
    return ["Tonart", "Keine", "C-Dur", "G-Dur", "A-Dur", "E-Dur", "H-Dur", "Fis-Dur", "F-Dur", "B-Dur", "Es-Dur",
            "As-Dur", "Des-Dur", "Ges-Dur",
            "a-moll", "e-moll", "fis-moll", "cis-moll", "dis-moll", "d-moll", "g-moll", "c-moll", "f-moll", "b-moll",
            "es-moll"]


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
    global added_interval_absolute
    global added_interval_tonal
    if interval in get_intervals_tonal():
        for i in get_intervals_tonal():
            if i == interval:
                added_interval_tonal = counter
                print("Verschiebung um " + str(counter) + " Tonleiterstufen")
            counter += 1
    else:
        for i in get_intervals_absolute():
            if i == interval:
                added_interval_absolute = counter
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


def set_tonart(tonart):
    print(tonart)
    global chosen_tonart
    chosen_tonart = tonart
    if tonart == "Keine":
        optionmenu_interval.set_menu(*get_intervals_absolute())
    else:
        optionmenu_interval.set_menu(*get_intervals_tonal())


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

    if chosen_tonart == "Keine" and added_interval_absolute != 0:
        if interval_direction == 0:
            message.setNoteNumber(original_note + added_interval_absolute)
            midiout.sendMessage(message)
            show_note_in_scale(message, "blue")
        else:
            message.setNoteNumber(original_note - added_interval_absolute)
            midiout.sendMessage(message)
            show_note_in_scale(message, "blue")
    else:
        _send_interval_tonal(original_note, message)


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

def _send_interval_tonal(original_note, message):
    number_in_c = message.getNoteNumber() % 12
    number_in_a = (message.getNoteNumber() + 3) % 12
    print("number in c: ", number_in_c)
    print("number in a: ", number_in_a)
    delta = 0
    scale = dur_distances
    tonart_reference = number_in_c
    if chosen_tonart == "C-Dur":
        delta = 0
    elif chosen_tonart == "G-Dur":
        delta = 5
    elif chosen_tonart == "D-Dur":
        delta = 10
    elif chosen_tonart == "A-Dur":
        delta = 3
    elif chosen_tonart == "H-Dur":
        delta = 1
    elif chosen_tonart == "E-Dur":
        delta = 8
    elif chosen_tonart == "Fis-Dur":
        delta = 6
    elif chosen_tonart == "F-Dur":
        delta = 7
    elif chosen_tonart == "B-Dur":
        delta = 2
    elif chosen_tonart == "Es-Dur":
        delta = 9
    elif chosen_tonart == "As-Dur":
        delta = 4
    elif chosen_tonart == "Des-Dur":
        delta = 11
    elif chosen_tonart == "Ges-Dur":
        delta = 6
    else:
        scale = moll_distances
        tonart_reference = number_in_a
        if chosen_tonart == "a-moll":
            delta = 0
        if chosen_tonart == "e-moll":
            delta = 5
        if chosen_tonart == "h-moll":
            delta = 10
        if chosen_tonart == "fis-moll":
            delta = 3
        if chosen_tonart == "cis-moll":
            delta = 8
        if chosen_tonart == "gis-moll":
            delta = 1
        if chosen_tonart == "dis-moll":
            delta = 6
        if chosen_tonart == "d-moll":
            delta = 7
        if chosen_tonart == "g-moll":
            delta = 2
        if chosen_tonart == "c-moll":
            delta = 9
        if chosen_tonart == "f-moll":
            delta = 4
        if chosen_tonart == "b-moll":
            delta = 11
        if chosen_tonart == "des-moll":
            delta = 8


    number_in_scale = (tonart_reference + delta) % 12
    print("number in scale: ", number_in_scale)
    if (number_in_scale in scale):
        index = scale.index(number_in_scale)
        difference = scale[index + added_interval_tonal] - scale[index]
        message.setNoteNumber(original_note + difference)
        midiout.sendMessage(message)
        show_note_in_scale(message, "purple")

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
window.geometry("900x450")

frame_rec_buttons = Frame(window, padding=10)
label_record = Label(master=frame_rec_buttons, text="Verbindung", font=("Helvetica", 15, "bold"))
label_record.pack()
button_record = Button(master=frame_rec_buttons, text="rec.", command=record, underline=0, background="lightgreen",
                       highlightbackground=backgroundcolor, state=DISABLED)
button_record.pack(side="left", anchor="center")
button_stop = Button(master=frame_rec_buttons, text="stop", command=stop, underline=0, background="red",
                     highlightbackground=backgroundcolor, state=DISABLED)
button_stop.pack(side="left", anchor="center")

frame_input = Frame(window, padding=10)
label_input = Label(master=frame_input, text="Eingang", font=("Helvetica", 15, "bold"))
label_input.pack()
clicked_in = StringVar()
optionmenu_devices_in = OptionMenu(frame_input, clicked_in, *get_midi_devices_in(), command=connect_midi_in)
optionmenu_devices_in.pack()
optionmenu_devices_in.config(width=20)
# button_update = Button(command=update_midi_devices, text="Update")

frame_output = Frame(window, padding=10)
label_output = Label(master=frame_output, text="Ausgang", font=("Helvetica", 15, "bold"))
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

frame_notes_area = Frame(window, padding=10)
note_frames = []
for i in range(11):
    frame_notes = Frame(frame_notes_area, padding=2)
    frame_notes.pack()
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

# Settings
frame_setting_area = Frame(window)

# Presets
frame_preset_area = Frame(master=frame_setting_area, padding=3)
frame_preset_area.pack(anchor="w")

label_presets = Label(master=frame_preset_area, text="Presets:", font=("Helvetica", 15, "bold"))
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
label_delay = Label(master=frame_delay, text="Delay (ms):", font=("Helvetica", 15, "bold"))
label_delay.pack(side="left")
entry_delay = Entry(master=frame_delay)
entry_delay.pack(side="left")

# Transpose
frame_transpose = Frame(master=frame_setting_area, padding=3)
frame_transpose.pack(anchor="w")
label_transpose = Label(master=frame_transpose, text="Transponieren:", font=("Helvetica", 15, "bold"))
label_transpose.pack(side="left")
slider_transpose = tkinter.Scale(master=frame_transpose, from_=-3, to=3, tickinterval=1, orient=HORIZONTAL,
                                 troughcolor=color_1, background=backgroundcolor, font="Helvetica 10")
slider_transpose.pack(side="left")

# Added Octaves
frame_added_octaves = Frame(master=frame_setting_area, padding=3)
frame_added_octaves.pack(anchor="w")
label_added_octaves = Label(master=frame_added_octaves, text="Oktaven hinzufügen:", font=("Helvetica", 15, "bold"))
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
frame_added_interval = Frame(master=frame_setting_area, padding=3)
frame_added_interval.pack(anchor="w")
label_added_interval = Label(master=frame_added_interval, text="Intervall hinzufügen:", font=("Helvetica", 15, "bold"))
label_added_interval.pack(side="left")
clicked_intervals = StringVar()
optionmenu_interval = OptionMenu(frame_added_interval, clicked_intervals, *get_intervals_absolute(),
                                 command=set_added_interval)
optionmenu_interval.pack(side="left")
clicked_up_down = StringVar()
optionmenu_interval_up_down = OptionMenu(frame_added_interval, clicked_up_down, *get_direction(),
                                         command=set_interval_direction)
optionmenu_interval_up_down.pack(side="left")

# Tonart
frame_tonart = Frame(master=frame_setting_area, padding=3)
frame_tonart.pack(anchor="w")
label_tonart = Label(master=frame_tonart, text="Tonart:", font="Helvetica 15 bold")
label_tonart.pack(side="left")
clicked_tonart = StringVar()
optionmenu_tonart = OptionMenu(frame_tonart, clicked_tonart, *get_tonart(), command=set_tonart)
optionmenu_tonart.pack(side="left")

# Program Change
frame_program_change = Frame(master=frame_setting_area, padding=3)
frame_program_change.pack(anchor="w")
label_program_change = Label(master=frame_program_change, text="Prg. Change:", font=("Helvetica", 15, "bold"))
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
frame_rec_buttons.grid(row=0, column=2)
frame_setting_area.grid(row=2, column=2, rowspan=6, sticky="w")
frame_notes_area.grid(row=2, column=0, columnspan=2)

# for i in range(11):
#     note_frames[i].grid(row=i + 3, column=0, columnspan=2)


# Bind

window.bind('<r>', record)
window.bind('<s>', stop)

# Run the application
window.mainloop()
