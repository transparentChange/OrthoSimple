import tkinter as tk

import sys
import threading
import time
import socket

from pynput import keyboard
import subprocess
from tempfile import TemporaryFile

import reader
import language_inputs
from drawing_transformer import DrawingTransformer

class OrthoSimple(tk.Tk):
    '''
    This class initializes the gui, defaulting to the drawing pad. It also enables keyboard
    keybindings, which can be used as a seperate feature.
    '''
    
    DIM = 400
    ROW0_Y_PADDING = (40, 0)
    ROW0_X_PADDING = (DIM - DrawingTransformer.CANVAS_SIDE) / 2
    HEIGHT_ROW0 = 350
    X_BUTTON_PADDING = 30
    Y_BUTTON_PADDING = 10
    
    DEFAULT_LANGUAGE = "FR"
    
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.gui_socket = socket.socket()
        #self.gui_socket.connect((DrawingTransformer.LOCAL_IP, 43938))
        self.protocol("WM_DELETE_WINDOW", quit)

        self.dbReader = reader.AssociationReader()
        self.key_listener = language_inputs.KeyboardListener(
            language_inputs.LanguageInput(self.DEFAULT_LANGUAGE, self.dbReader))
        self.language_reader = reader.LanguageReader()
        
        if (sys.platform == "linux"):
            window_map_listener = keyboard.Listener(on_press = self.toggle_visibility, on_release = None)
            window_map_listener.start()
        
        self.resizable(False, False)
        self.configure(background = "white")
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)
        
        self.frame = MainFrame(self.container, self, self.dbReader)
        self.frame.pack(fill = "both")
        
        self.grid_columnconfigure(0, weight = 1)
        
        self.mainloop()
    
    def toggle_visibility(self, key_typed):
        """
        This function toggles the visibility of the main program using xdotool
        """
        if (key_typed == keyboard.Key.esc):
            with TemporaryFile() as wid_file:
                wid_process = subprocess.Popen(["xdotool", "search", "--name", "tk"], stdout = wid_file);
                wid_process.wait()
                wid_file.flush()
                wid_file.seek(0)
                active_window_process = subprocess.Popen(["xdotool", "search", "--onlyvisible", "--name", "tk"],
                                                         stdout = subprocess.PIPE)
                if (active_window_process.stdout.read() != b""):
                    subprocess.call(["xdotool", "windowunmap", wid_file.read()])
                else:
                    subprocess.call(["xdotool", "windowmap", wid_file.read()])
    
    def quit(self):
        self.gui_socket.close()
        self.destroy()
        
    def change_frame(self):
        self.frame.pack_forget()
        if (type(self.frame) is MainFrame):
            self.frame = OptionsFrame(self.container, self)
        else:
            self.frame = MainFrame(self.container, self, self.dbReader)
            empty_menu = tk.Menu(self)
            self.configure(menu = empty_menu)
        self.frame.pack(fill = "both") 
    
    def update_language(self, new_language):
        new_abbrev = self.language_reader.abbrev(new_language)
        self.key_listener.update_language(language_inputs.LanguageInput(new_abbrev, self.dbReader))
    
    def name_curr_language(self):
        return self.language_reader.full_name(self.key_listener.get_language())
        
class MainFrame(tk.Frame):
    '''
    Displays the main page of the gui. This includes the DrawingTransformer that 
    receives mouse input and communicates with the gesture recognition software. Displays
    the special character recognized when it is drawn and provides access to the OptionsFrame
    (see change_frame method in OrthoSimple)
    '''
    
    
    def __init__(self, parent, controller, sqlReader):
        tk.Frame.__init__(self, parent)
        
        self.controller = controller
        controller.geometry("%dx%d+0+0" % (OrthoSimple.DIM, OrthoSimple.DIM))
        
        self.configure(background = "white")
        self.draw_frame = DrawingTransformer(self, controller.gui_socket, sqlReader)
        self.draw_frame.grid(pady = OrthoSimple.ROW0_Y_PADDING, sticky = "nsew"),
        
        settings_button = tk.Button(self, command = lambda : controller.change_frame(), 
                                    text = "→", bg = "#EAEAEA")
        settings_button.grid(row = 1, column = 0, pady = OrthoSimple.Y_BUTTON_PADDING, sticky = "SE", 
                             padx = OrthoSimple.X_BUTTON_PADDING)
        
        self.message = tk.StringVar()
        message_updater = threading.Thread(target = self.update_message)
        message_updater.daemon = True
        message_updater.start() 

        message_label = tk.Label(self, textvariable = self.message)
        message_label.configure(background = "white", font = ("TkDefaultFont", 9))
        message_label.grid(row = 1, sticky = "W", padx = OrthoSimple.ROW0_Y_PADDING, 
                           pady = OrthoSimple.Y_BUTTON_PADDING)
        
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1, minsize = OrthoSimple.HEIGHT_ROW0) 
        self.grid_rowconfigure(1, weight = 0, minsize = OrthoSimple.DIM - OrthoSimple.HEIGHT_ROW0)
         
    def update_message(self):
        while (True):
            transformed_char = self.draw_frame.get_result()
            if (not (transformed_char == "")):
                self.message.set(self.draw_frame.get_result() + " copied!")
            time.sleep(0.05)
         
         
class OptionsFrame(tk.Frame):
    '''
    This class contains the Settings and InformationKeys Frames and deals with
    switching between them and their placement on the window.
    '''
    HEIGHT_MENU = 28 # by observation
    EXTRA_Y_PADDING = (20, 0)
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.configure(background = "white")
        self.controller = controller
        controller.geometry("%dx%d+0+0" % (OrthoSimple.DIM, OrthoSimple.DIM - self.HEIGHT_MENU))
        
        self.info_container = tk.Frame(self)
        self.info_container.grid(row = 0, column = 0, pady = OrthoSimple.ROW0_Y_PADDING[0] - self.HEIGHT_MENU, 
                                 padx = OrthoSimple.ROW0_Y_PADDING, sticky = "NW")
        self.info_container.columnconfigure(0, weight = 2)
        self.info_container.configure(background = "white")
        
        self.curr_frame = self.Settings(self.info_container, controller)
        self.curr_frame.grid()
        
        menu = tk.Menu(self.info_container)
        menu_font = ("TkDefaultFont", 9)
        menu.add_command(label = "Settings", command = self.to_settings, font = menu_font)
        menu.add_command(label = "Keybindings", command = self.to_information, font = menu_font)
        controller.configure(menu = menu)
        
        settings_button = tk.Button(self, command = lambda : controller.change_frame(), 
                                    text = "→", bg = "#EAEAEA")
        settings_button.grid(column = 0, row = 1, pady = OrthoSimple.Y_BUTTON_PADDING,
                             padx = OrthoSimple.X_BUTTON_PADDING, sticky = "SE")
        
        
        self.grid_rowconfigure(0, weight = 1, minsize = OrthoSimple.HEIGHT_ROW0 - self.HEIGHT_MENU)
        self.grid_rowconfigure(1, weight = 0, minsize = OrthoSimple.DIM - OrthoSimple.HEIGHT_ROW0)
        self.grid_columnconfigure(0, weight = 1)
    
    def to_settings(self):
        if (type(self.curr_frame) is OptionsFrame.InformationKeys):
            self.curr_frame.destroy()
            self.curr_frame = OptionsFrame.Settings(self.info_container, self.controller)
            self.curr_frame.grid()
        
    def to_information(self):
        if (type(self.curr_frame) is OptionsFrame.Settings):
            self.curr_frame.destroy()
            self.curr_frame = OptionsFrame.InformationKeys(self.info_container, self.controller)
            self.curr_frame.grid()

    def change_frame(self):
        self.curr_frame.destroy()
        if (type(self.curr_frame) is OptionsFrame.Settings):
            self.curr_frame = OptionsFrame.InformationKeys(self.info_container, self.controller)
        else:
            self.curr_frame = OptionsFrame.Settings(self.info_container, self.controller)
        self.curr_frame.grid()
        
    class Settings(tk.Frame):
        '''
        This Frame provides the capability for global settings to be adjusted
        '''
        
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            
            self.configure(background = "white")
            language_label = tk.Label(self, text = "Language: ",
                                      font = ("TkDefaultFont", 11), bg = "white")
            language_label.grid(row = 0, column = 0, pady = OptionsFrame.EXTRA_Y_PADDING, sticky = "W")
            
            languages = controller.language_reader.all_languages()
            s_var = tk.StringVar()
            s_var.set(controller.name_curr_language())   
            s_var.trace("w", lambda *args : controller.update_language(s_var.get()))
            language_menu = tk.OptionMenu(self, s_var, *languages)
            language_menu["highlightthickness"] = 0
            language_menu.grid(row = 0, column = 1, pady = OptionsFrame.EXTRA_Y_PADDING, sticky = "W")
            
            self.grid_columnconfigure(0, weight = 1)
            
    class InformationKeys(tk.Frame):
        '''
        This Frame provides information on the key bindings for the languages
        currently implemented. 
        '''
        
        SCROLLABLE_HEIGHT = 150
        LABEL_SEP = 10
        LANGUAGE_LABEL = "Current\nKey Bindings"
        OTHER_LABEL = "Supported\nKey Bindings"
        
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            
            self.__init_bindings() 
            self.configure(background = "white")        
            self.__init_info(controller)
            self.__init_labels()
            
        def __init_bindings(self):
            """
            Reads the bindings stored in text_assoiation.txt and stores them as a dictionary
            from languages to each line in the file.
            """
            
            self.bindings = dict({})
            info_file = open("text_association.txt", "r")
            association_info = info_file.read().split("\n\n")
            for line in association_info:
                lang_association = line.split("\n")
                self.bindings[lang_association[0]] = [pattern for pattern in lang_association[2:]] 
            
            info_file.close()
        
        def __init_info(self, controller):
            """
            Displays both the key bindings for the selected languages as well as for the other languages,
            separately, using controller to access this currently selected language. 
            """
            languages = controller.language_reader.all_languages()
            curr_language = controller.name_curr_language()
            self.LanguageInfo(self, self, curr_language).grid(row = 0, column = 0, 
                                                              pady = OptionsFrame.EXTRA_Y_PADDING, sticky = "w")
            self.__init_remaining(languages, curr_language)            
            self.rowconfigure(0, minsize = OrthoSimple.HEIGHT_ROW0 / 2 - OptionsFrame.HEIGHT_MENU)
       
        def __init_remaining(self, languages, language_excluding):
            """
            Displays a scrollable region containing the key bindings for the languages not currently
            in use.
            """
            info_frame = tk.Frame(self)
            canvas = tk.Canvas(info_frame, height = OptionsFrame.InformationKeys.SCROLLABLE_HEIGHT,
                               borderwidth = 0, highlightthickness = 0) 
            frame = tk.Frame(canvas)
            scroll_y = tk.Scrollbar(info_frame, orient = "vertical", 
                                    command = canvas.yview)
            canvas.configure(yscrollcommand = scroll_y.set)            
            self.__init_frame(canvas, frame)
            
            for i in range(len(languages)):
                if (languages.iloc[i] != language_excluding):
                    self.LanguageInfo(frame, self, languages.iloc[i]).pack(fill = "both")
            
            canvas.pack(side = "left", fill = "both")
            scroll_y.pack(side = "right", fill = "y")

            canvas.update()
            canvas.configure(width = frame.winfo_width())
            info_frame.grid(row = 2, column = 0)
            
             
        def __init_labels(self):
            """
            Places the labels on the right of the screen to distinguish the key bindings of the
            selected languages from the rest.
            """
            upper_lab = tk.Label(self, text = self.LANGUAGE_LABEL, bg = "white")
            upper_lab.grid(row = 0, column = 1, padx = 20, pady = self.LABEL_SEP, sticky = "s")
            
            line_frame = tk.Frame(self, height = 1, width = 30, bg = "black")
            line_frame.grid(row = 1, column = 1)
            
            lower_lab = tk.Label(self, text = self.OTHER_LABEL, bg = "white")
            lower_lab.grid(row = 2, column = 1, pady = self.LABEL_SEP, sticky = "n")
             
        def __init_frame(self, canvas, frame):
            """
            Adds the frame as a window in the canvas and identifies its scrollregion.
            """
            canvas.create_window((0, 0), anchor = "nw", window = frame)
            frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion = canvas.bbox("all")
                )
            )
             
        class LanguageInfo(tk.Frame):
            def __init__(self, parent, controller, language):
                tk.Frame.__init__(self, parent)
                
                self.configure(background = "white")
                lang_label = tk.Label(self, text = language, font = ("TkDefaultFont", 10, "bold"),
                                      bg = "white")
                lang_label.grid(row = 0, column = 0, columnspan = 2, sticky = "w")
                
                lang_bindings = controller.bindings[language]
                counter = 0
                text_label = ""
                while ((counter != len(lang_bindings)) and (lang_bindings[counter] != "(also)")):
                    text_label += lang_bindings[counter] + "\n"
                    counter += 1                   
                bindings_common = tk.Label(self, text = text_label, bg = "white")
                bindings_common.grid(row = 1, column = 0, sticky = "n")
             
                if (counter != len(lang_bindings)):
                    text_label = ""
                    counter += 1
                    while (counter != len(lang_bindings)):
                        text_label += lang_bindings[counter] + "\n"
                        counter += 1
                    bindings_also = tk.Label(self, text = text_label, 
                                             bg = "white", padx = 30)
                    bindings_also.grid(row = 1, column = 1, sticky = "n")