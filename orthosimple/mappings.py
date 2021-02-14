import pyautogui
import pyperclip
from pynput import keyboard
import sys

appendUpper = lambda s: s + s.upper()
pyautogui.PAUSE = 0.05

class Mapping:
    SEQUENCES = [[keyboard.Key.shift, keyboard.KeyCode(char = "<")],
                 [keyboard.Key.shift, keyboard.KeyCode(char = ">")]] # avoids false negative
    
    if (sys.platform == "linux"):
        MANUAL_CHARS = "<>AEIOU?!"
    else:
        MANUAL_CHARS = ""
    
    def __init__(self, mapCondition, plainText, newText, seq = SEQUENCES):
        self.mapCondition = mapCondition
        self.map = dict([])
        
        for (charOrig, charNew) in zip(plainText, newText):
            self.map[keyboard.KeyCode(char = charOrig)] = charNew
        self.sequences = seq
        self.prevKey = ""
        self.capsLockOn = False
        self.prev_transformed = None
        
        self.curPositions = set()
        self.__initIndices()
    
    def __initIndices(self):
        self.indicesSeq = dict()
        for i in range(0, len(self.sequences)):
            self.indicesSeq[i] = 0
    
    def writeNewChar(self, key_typed):
        if ((self.prev_transformed is not None) and (str(key_typed) == "Key.backspace") and 
            (str(self.prevKey) == "'v'")):
            pyperclip.copy(self.prev_transformed)
            pyautogui.hotkey("ctrl", "v") # pasting avoids recursive calls
            self.prev_transformed = None
        
        if (str(key_typed) == 'Key.caps_lock'): # temporary implementation
            self.capsLockOn = not self.capsLockOn
            return
        
        if (str(key_typed) == "Key.shift"):
            self.shift_pressed = True
        
        typed_str = str(key_typed)
        letter_typed = ""
        if ((len(typed_str) == 3) or (typed_str == "'\\\\'")):
            letter_typed = typed_str[1]
            
        if (self.capsLockOn and (letter_typed != "")):
            typed_str = typed_str[1].upper()
            key_typed = keyboard.KeyCode(char = typed_str)
           
        newIndices = self.__getNewIndices(key_typed)
        if (isinstance(newIndices, int) or (newIndices == dict())):
            self.__initIndices()
        else:
            self.indicesSeq = newIndices
         
        if ((self.mapCondition(letter_typed, self.prevKey)) and (key_typed in self.map)):
            pyautogui.press('backspace')
            pyautogui.press('backspace')
            
            if (letter_typed in Mapping.MANUAL_CHARS):
                pyautogui.PAUSE = 0
                hexNum = hex(ord(self.map[key_typed]))
                
                pyautogui.hotkey('ctrl', 'shift', 'u')
                for digit in hexNum:
                    pyautogui.typewrite(digit)
                pyautogui.typewrite('\n')
                pyautogui.PAUSE = 0.05
            else: 
                pyperclip.copy(self.map[key_typed]) 
                pyautogui.hotkey("ctrl", "v")
            
            self.prev_transformed = self.prevKey + letter_typed
            
        self.__updatePrevKey(letter_typed)
    
    def on_release(self, key_released):
        if (str(key_released) == "Key.shift"):
            self.shift_pressed = False
            
        
    def __getNewIndices(self, charTyped):
        newIndices = dict()
        for seqNum in self.indicesSeq:
            curIndex = self.indicesSeq[seqNum]
            if (charTyped == self.sequences[seqNum][curIndex]):
                if (curIndex == (len(self.sequences[seqNum]) - 1)):
                    return curIndex
                newIndices[seqNum] = curIndex + 1
        
        return newIndices
    
    def __updatePrevKey(self, charTyped):
        for seqNum in self.indicesSeq:
            curIndex = self.indicesSeq[seqNum] - 1
            if (charTyped == self.sequences[seqNum][curIndex]):
                return # does not update prevKey
        
        self.prevKey = charTyped 

class KeyUpdater:
    def __init__(self, languageInput):
        self.languageInput = languageInput
        
        onPress = lambda key: self.languageInput.update(key)
        onRelease = None
        keyboard.Listener(on_press = onPress, on_release = onRelease).start()
    
        
