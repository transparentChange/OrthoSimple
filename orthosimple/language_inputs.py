import mappings
from pynput import keyboard
        
class KeyboardListener:
    def __init__(self, language):
        self.language = language
        
        self.on_press = lambda key: self.language.update(key)
        self.on_release = None
        
        self.key_listener = keyboard.Listener(on_press = self.on_press, 
                                              on_release = self.on_release)
        self.key_listener.start()
    
    def update_language(self, new_language):
        self.language = new_language
        
class LanguageInput:
    def __init__(self, association_reader):
        GRAVE_COND = keyboard.KeyCode(char = "\\")
        ACUTE_COND = keyboard.KeyCode(char = "/")
        TREMA_COND = keyboard.KeyCode(char = '"')
        SPECIAL_COND = keyboard.KeyCode(char = ";")
        OTHER_COND = keyboard.KeyCode(char = ".")
        
        LanguageInput.GRAVE_COND = self.default_mapping(GRAVE_COND)
        LanguageInput.ACUTE_COND = self.default_mapping(ACUTE_COND)
        LanguageInput.TREMA_COND = self.default_mapping(TREMA_COND)
        LanguageInput.SPECIAL_COND = self.default_mapping(SPECIAL_COND)
        LanguageInput.OTHER_COND = self.default_mapping(OTHER_COND)
        
        self.groups = association_reader
        self.mappings = []
        self.association_reader = association_reader
         
    def addMapping(self, map_condition, group, language_abbrev):
        char_association = self.association_reader.select_char_association(group, language_abbrev)
        self.mappings.append(mappings.Mapping(map_condition, char_association[0],
                                              char_association[1]))
 
    def default_mapping(self, prev_to_match):
        return lambda curr, prev : prev == prev_to_match
    
    def update(self, keyTyped):
        for accentMapping in self.mappings:
            accentMapping.writeNewChar(keyTyped)
 
class FrenchInput(LanguageInput):
    def __init__(self, association_reader):
        LanguageInput.__init__(self, association_reader)
        
        ABBREV = "FR"
        groups = association_reader.get_groups(ABBREV)
        super().addMapping(lambda curr, prev: curr == prev, groups[0], ABBREV)
        super().addMapping(LanguageInput.GRAVE_COND, groups[1], ABBREV)
        super().addMapping(LanguageInput.ACUTE_COND, groups[2], ABBREV)
        super().addMapping(LanguageInput.TREMA_COND, groups[3], ABBREV)
        super().addMapping(LanguageInput.SPECIAL_COND, groups[4], ABBREV)
        super().addMapping(LanguageInput.OTHER_COND, groups[5], ABBREV)
        
class SpanishInput(LanguageInput):
    def __init__(self, association_reader):
        LanguageInput.__init__(self, association_reader)
        
        ABBREV = "SP"
        groups = association_reader.get_groups(ABBREV)
        super().addMapping(LanguageInput.ACUTE_COND, groups[0], ABBREV)
        super().addMapping(LanguageInput.TREMA_COND, groups[1], ABBREV)
        super().addMapping(LanguageInput.SPECIAL_COND, groups[2], ABBREV)
        super().addMapping(LanguageInput.OTHER_COND, groups[3], ABBREV)