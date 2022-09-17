import threading

import simpleaudio, time
strong_beat = simpleaudio.WaveObject.from_wave_file('resources/strong_beat.wav')
weak_beat = simpleaudio.WaveObject.from_wave_file('resources/weak_beat.wav')

on = False

def start(tempo, measure):
    if not on:
        thread = threading.Thread(target=start_in_thread, args=(tempo,measure))
        thread.start()
    else:
        print("Metronom läuft bereits")


def start_in_thread(tempo, measure):
    time_to_wait = 60/tempo
    global on
    on = True

    while (on):
        strong_beat.play()
        time.sleep(time_to_wait)

        for i in range(int(measure)-1):
            weak_beat.play()
            time.sleep(time_to_wait)

def stop():
    global on
    on = False
