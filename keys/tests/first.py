import pyautogui
import pyperclip
from pyautogui import press
import time

from abc import ABC, abstractmethod

from pynput import keyboard

appendUpper = lambda str : str + str.upper()

CIRC_LOWER = "aeiou"
CIRC_LOWER_MAPPED = "âêîôû"

'''
circumMapping = dict([])
CIRC_KEYS = appendUpper(CIRC_LOWER)
CIRC_KEYS_MAPPED = appendUpper(CIRC_LOWER)

for (keyOrig, keyNew) in zip(CIRC_LOWER, CIRC_LOWER_MAPPED):
    circumMapping[keyboard.KeyCode(char = keyOrig)] = keyboard.KeyCode(char = keyNew)
'''

class Mapping:
    prevKey = keyboard.KeyCode()
    
    def __init__(self, mapCondition, charsOrig, charsNew):
        # check length = 1
        self.mapCondition = mapCondition
        self.map = dict([])
        
        for (charOrig, charNew) in zip(charsOrig, charsNew):
            self.map[keyboard.KeyCode(char = charOrig)] = charNew
    
    def writeNewChar(self, charTyped):
        if ((self.mapCondition(charTyped, Mapping.prevKey)) and (charTyped in self.map)):
            pyperclip.copy(self.map[charTyped])
            pyautogui.hotkey("ctrl", "v")
            
        Mapping.prevKey = charTyped

'''
class AbsoluteMapping(Mapping):
   def __init__(self, preceding, charsOrig, charsNew):
        # check length = 1
        self.preceding = preceding
        
        Mapping.__init__(charsOrig, charsNew)
    
    def writeNewChar(self, charTyped):
        if (self.prevChar == preceding):
            super(RelativeMapping, self).writeNewChar(charTyped)

class RelativeMapping(Mapping):
    def __init__(self, acceptable, charsOrig, charsNew):
        self.acceptable = acceptable
        
        Mapping.__init__(charsOrig, charsNew)
        
    def writeNewChar(self, charTyped):
        if (self.acceptable(prevKey, charTyped)):
            super(RelativeMapping, self).writeNewChar(charTyped)
'''
x = lambda curr, prev: curr == prev
circumMapping = Mapping(lambda curr, prev: curr == prev, CIRC_LOWER, CIRC_LOWER_MAPPED)

'''
CIRC_KEYS = CIRC_LOWER + CIRC_LOWER.upper()
translateCircumflex = str.maketrans(
    appendUpper(CIRC_LOWER), appendUpper(CIRC_LOWER_MAPPED))
'''

def onPress(key):
    circumMapping.writeNewChar(key)
    

def onRelease(key):
    pass

# for blocking
with keyboard.Listener(on_press = onPress, on_release = onRelease) as listenerThread:
    listenerThread.join()
    

'''
SHORTCUT = 'ctrl+a'
#pyautogui.typewrite("Hi")

def testWrite():
    time.sleep(100)
    keyboard.write("hello")
    print("hi")

keyboard.add_hotkey(SHORTCUT, lambda:keyboard.write("got"))
keyboard.write("message me")
keyboard.wait()
'''