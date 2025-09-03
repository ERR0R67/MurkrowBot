import pyperclip
import pyautogui
import keyboard
import time

def sketch(filepath, hotkey='ctrl+alt+z', delay = 2.5):
    # Reading lines from generated commands, takes file path as input so it can be saved from Murkrow
    keywords = ['Nugget', 'Pearl', 'Metronome']
    valid_lines = []
    excluded_lines = []

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # takes file path of command file and opens it, encoding set to same as murkrow in case of different defaults
            lines = [line.strip() for line in file]

    # Exception for wrong path
    except FileNotFoundError:
        print(f'File not found: {filepath}')
        return
    
    for line in lines:
        if "item:" in line:
            item = line.split("item:")[-1].strip()
            if item in keywords:
                excluded_lines.append(line)
            else:
                valid_lines.append(line)
        else:
            valid_lines.append(line)

    duration = round(len(valid_lines) * delay / 60)
    print(f'File loaded, estimated completion in {duration} minutes')
    print(f'Place cursor in discord chat and press "{hotkey.upper()}" to start')

    keyboard.wait(hotkey) # code waits for hotkey press
    print('Starting in 3 seconds')
    time.sleep(3) # Buffer just in case

    for line in valid_lines:
        pyperclip.copy(line)            # Copy line from text file
        pyautogui.hotkey('ctrl','v')    # Paste line from text file
        pyautogui.press('enter')        # Press Enter
        time.sleep(delay)               # Delay so bot can buffer

    linecount = len(excluded_lines)
    print(f'Initial lines finished, starting manual input of {linecount} lines')
    print(f'Please enter {hotkey.upper()} to continue')
    keyboard.wait(hotkey)    
    
    for line in excluded_lines:
        pyperclip.copy(line)            # Copy line from text file
        print('paste line to proceed to next')
        keyboard.wait('ctrl+v')              
        time.sleep(delay)

    print('Completed')


path = input('Input file path: ')
sketch(path)
