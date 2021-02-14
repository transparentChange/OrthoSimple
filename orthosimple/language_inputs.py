import mappings
from pynput import keyboard
        
class KeyboardListener:
    def __init__(self, language):
        self.language = language
        
        self.on_press = lambda key: self.language.update(key) 
        self.key_listener = keyboard.Listener(on_press = self.on_press, 
                                              on_release = None)
        self.key_listener.start()
    
    def update_language(self, new_language):
        self.language = new_language
        
class LanguageInput:
    def __init__(self, language_abbrev, association_reader):
        # functions associated with escape characters
        LanguageInput.GRAVE_COND = self.default_mapping('\\')
        LanguageInput.ACUTE_COND = self.default_mapping('/')
        LanguageInput.TREMA_COND = self.default_mapping('"')
        LanguageInput.SUB_CURL_COND = self.default_mapping(',')
        LanguageInput.SPECIAL_COND = self.default_mapping(';')
        LanguageInput.OTHER_COND = self.default_mapping('.')
        LanguageInput.OE_COND = self.default_mapping('o')
        LanguageInput.AE_COND = self.default_mapping('a')
        
        self.mappings = []
        self.language = language_abbrev
        self.association_reader = association_reader
        
        self.add_all_mappings()
    
    def add_all_mappings(self):
        """
        Appends all of the mappings for the language, based on the default
        keystrokes for the special groups, to the mappings field via add_mapping
        """
        
        groups = self.association_reader.get_groups(self.language)
        for special_group in groups:
            if (special_group == "circumflex"):
                map_condition = lambda curr, prev: curr == prev; 
            elif (special_group == "acute"):
                map_condition = LanguageInput.ACUTE_COND
            elif (special_group == "grave"):
                map_condition = LanguageInput.GRAVE_COND
            elif (special_group == "trema"):
                map_condition = LanguageInput.TREMA_COND
            elif (special_group == "sub_curl"):
                map_condition = LanguageInput.SUB_CURL_COND
            elif (special_group == "special"):
                map_condition = LanguageInput.SPECIAL_COND
            elif (special_group == "other"):
                map_condition = LanguageInput.OTHER_COND
            elif (special_group == "oe"):
                map_condition = LanguageInput.OE_COND;
            elif (special_group == "ae"):
                map_condition = LanguageInput.AE_COND;
            
            self.add_mapping(map_condition, special_group, self.language)
            
    def add_mapping(self, map_condition, group, language_abbrev):
        char_association = self.association_reader.select_char_association(group, language_abbrev)
        self.mappings.append(mappings.Mapping(map_condition, char_association[0],
                                              char_association[1]))
 
    def default_mapping(self, prev_to_match):
        return lambda curr, prev : prev == prev_to_match
    
    def update(self, keyTyped):
        for accentMapping in self.mappings:
            accentMapping.writeNewChar(keyTyped)

'''
DEPRECATED
class FrenchInput(LanguageInput):
    def __init__(self, association_reader):
        LanguageInput.__init__(self, association_reader)
        
        ABBREV = "FR"
        groups = association_reader.get_groups(ABBREV)
        super().addMapping(LanguageInput.ACUTE_COND, groups[0], ABBREV)
        super().addMapping(lambda curr, prev: curr == prev, groups[1], ABBREV)
        super().addMapping(LanguageInput.GRAVE_COND, groups[2], ABBREV)
        super().addMapping(LanguageInput.TREMA_COND, groups[3], ABBREV)
        super().addMapping(LanguageInput.SUB_CURL_COND, groups[4], ABBREV)
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
        '''
            