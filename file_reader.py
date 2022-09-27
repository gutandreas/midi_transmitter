import fileinput
import json

file = open("settings.txt")


def print_settings():
    print(file.name)


def save_settings(dict, line_number):
    # with open('settings.txt', 'w') as settings:
    counter = 0
    for line in fileinput.input("settings.txt", inplace=True):
        if counter == line_number:
            print(json.dumps(dict))
        else:
            print(line[0:len(line)-1])
        counter += 1

    # settings.write(json.dumps(dict))


def load_settings(number):
    with open('settings.txt', 'r') as settings:
        line = str(settings.readlines()[number])
    return line
