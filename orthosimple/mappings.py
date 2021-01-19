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
    
    def writeNewChar(self, charTyped):
        if ((self.prev_transformed is not None) and (str(charTyped) == "Key.backspace") and 
            (str(self.prevKey) == "'v'")):
            pyperclip.copy(self.prev_transformed)
            pyautogui.hotkey("ctrl", "v") # pasting avoids recursive calls
            self.prev_transformed = None
        
        if (str(charTyped) == 'Key.caps_lock'): # temporary implementation
            self.capsLockOn = not self.capsLockOn
            return
        
        if (str(charTyped) == "Key.shift"):
            self.shift_pressed = True
        
        typedStr = str(charTyped)
        if (self.capsLockOn and len(typedStr) == 3):
            typedStr = typedStr[1].upper()
            charTyped = keyboard.KeyCode(char = typedStr)
           
        newIndices = self.__getNewIndices(charTyped)
        if (isinstance(newIndices, int) or (newIndices == dict())):
            self.__initIndices()
        else:
            self.indicesSeq = newIndices
        
        if ((self.mapCondition(charTyped, self.prevKey)) and (charTyped in self.map)):
            pyautogui.press('backspace')
            pyautogui.press('backspace')
            
            if (str(charTyped)[1] in Mapping.MANUAL_CHARS):
                pyautogui.PAUSE = 0
                hexNum = hex(ord(self.map[charTyped]))
                
                pyautogui.hotkey('ctrl', 'shift', 'u')
                for digit in hexNum:
                    pyautogui.typewrite(digit)
                pyautogui.typewrite('\n')
                pyautogui.PAUSE = 0.05
            else: 
                pyperclip.copy(self.map[charTyped]) 
                pyautogui.hotkey("ctrl", "v")
            
            self.prev_transformed = str(self.prevKey)[1] + str(charTyped)[1]
            
        self.__updatePrevKey(charTyped)
    
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
    
        
