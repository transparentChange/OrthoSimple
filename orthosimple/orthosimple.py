import tkinter as tk

import sys
import threading
import time
import socket

from pynput import keyboard
import subprocess
from tempfile import TemporaryFile

import association_reader
import language_inputs
from drawing_transformer import DrawingTransformer

class OrthoSimple(tk.Tk):
    '''
    This class initializes the gui, defaulting to the drawing pad. It also enables keyboard
    keybindings, which can be used as a seperate feature.
    '''
    
    DIM = 400
    ROW0_Y_PADDING = (30, 10)
    HEIGHT_ROW0 = DrawingTransformer.CANVAS_SIDE + ROW0_Y_PADDING[0] + ROW0_Y_PADDING[1]
    X_BUTTON_PADDING = 30
    
    DEFAULT_LANGUAGE = "FR"
    
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.gui_socket = socket.socket()
        self.gui_socket.connect((DrawingTransformer.LOCAL_IP, 43938))
        self.protocol("WM_DELETE_WINDOW", quit)

        self.dbReader = association_reader.Reader()
        self.key_listener = language_inputs.KeyboardListener(
            language_inputs.LanguageInput(self.DEFAULT_LANGUAGE, self.dbReader))
        
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
        if (new_language == "French"):        
            self.key_listener.update_language(language_inputs.SpanishInput(self.dbReader))
        elif (new_language == "Spanish"):
            self.key_listener.update_language(language_inputs.SpanishInput(self.dbReader))
        else:
            raise ValueError(new_language + " is not supported")
            
        
class MainFrame(tk.Frame):
    '''
    Displays the main page of the gui. This includes the DrawingTransformer that 
    receives mouse input and communicates with the gesture recognition software. Displays
    the special character recognized when it is drawn and provides access to the OptionsFrame
    (see change_frame method in OrthoSimple)
    '''
    
    X_PADDING = (OrthoSimple.DIM - DrawingTransformer.CANVAS_SIDE) / 2
    
    def __init__(self, parent, controller, sqlReader):
        tk.Frame.__init__(self, parent)
        
        self.controller = controller
        controller.geometry("%dx%d+0+0" % (OrthoSimple.DIM, OrthoSimple.DIM))
        
        self.configure(background = "white")
        self.draw_frame = DrawingTransformer(self, controller.gui_socket, sqlReader)
        self.draw_frame.grid(pady = OrthoSimple.ROW0_Y_PADDING, sticky = "nsew"),
        
        settings_button = tk.Button(self, command = lambda : controller.change_frame(), 
                                    text = "→", bg = "#EAEAEA")
        settings_button.grid(row = 1, column = 0, pady = 10, sticky = "SE", 
                             padx = OrthoSimple.X_BUTTON_PADDING)
        
        self.message = tk.StringVar()
        message_updater = threading.Thread(target = self.update_message)
        message_updater.daemon = True
        message_updater.start() 

        message_label = tk.Label(self, textvariable = self.message)
        message_label.configure(background = "white", font = ("TkDefaultFont", 9))
        message_label.grid(row = 1, sticky = "W", padx = MainFrame.X_PADDING, pady = 10)
        
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1, minsize = OrthoSimple.HEIGHT_ROW0) 
        self.grid_rowconfigure(1, weight = 1, minsize = OrthoSimple.DIM - OrthoSimple.HEIGHT_ROW0)
         
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
    HEIGHT_MENU = 30
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.configure(background = "white")
        self.controller = controller
        controller.geometry("%dx%d+0+0" % (OrthoSimple.DIM, OrthoSimple.DIM - 30))
        
        self.info_container = tk.Frame(self)
        self.info_container.grid(row = 0, column = 0, pady = OrthoSimple.ROW0_Y_PADDING, 
                                 padx = 30, sticky = "NW")
        self.info_container.columnconfigure(0, weight = 2)
        self.info_container.rowconfigure(0, weight = 1)#, minsize = OptionsFrame.HEIGHT_INFO_ROW0)
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
        settings_button.grid(column = 0, row = 1,
                             pady = 10,
                             padx = OrthoSimple.X_BUTTON_PADDING, sticky = "SE")
        
        self.grid_rowconfigure(0, weight = 0, minsize = OrthoSimple.HEIGHT_ROW0 - 30)
        
        self.grid_rowconfigure(1, weight = 0, minsize = OrthoSimple.DIM 
                               - OrthoSimple.HEIGHT_ROW0) #?
        self.grid_columnconfigure(0, weight = 1)
    
    def to_settings(self):
        if (type(self.curr_frame) is OptionsFrame.InformationKeys):
            self.curr_frame.destroy()
            self.curr_frame = OptionsFrame.Settings(self.info_container, self.controller)
            self.curr_frame.grid()
        
    def to_information(self):
        if (type(self.curr_frame) is OptionsFrame.Settings):
            self.curr_frame.destroy()
            self.curr_frame = OptionsFrame.InformationKeys(self.info_container)
            self.curr_frame.grid()

    def change_frame(self):
        self.curr_frame.destroy()
        if (type(self.curr_frame) is OptionsFrame.Settings):
            self.curr_frame = OptionsFrame.InformationKeys(self.info_container)
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
            language_label.grid(row = 0, column = 0, sticky = "W")
            
            languages = ["French", "Spanish"]
            s_var = tk.StringVar()
            s_var.set(languages[0])   
            s_var.trace("w", lambda *args : controller.update_language(s_var.get()))
            language_menu = tk.OptionMenu(self, s_var, *languages)
            language_menu["highlightthickness"] = 0
            language_menu.grid(row = 0, column = 1, sticky = "W")
            
            self.grid_columnconfigure(0, weight = 1)
            
    class InformationKeys(tk.Frame):
        '''
        This Frame provides information on the key bindings for the languages
        currently implemented. 
        '''
        
        def __init__(self, parent):
            tk.Frame.__init__(self, parent)
            self.configure(background = "white")
            
            self.bindings = dict({})
            info_file = open("text_association.txt", "r")
            association_info = info_file.read().split("\n\n")
            for line in association_info:
                lang_association = line.split("\n")
                self.bindings[lang_association[0]] = [pattern for pattern in lang_association[2:]]
                
            info_file.close()
            
            self.LanguageInfo(self, "French").pack()
            self.LanguageInfo(self, "Spanish").pack()
        
        class LanguageInfo(tk.Frame):
            def __init__(self, parent, language):
                tk.Frame.__init__(self, parent)
                
                self.configure(background = "white")
                lang_label = tk.Label(self, text = language, font = ("TkDefaultFont", 10, "bold"),
                                      bg = "white")
                lang_label.grid(row = 0, column = 0, columnspan = 2, sticky = "w")
                
                lang_bindings = parent.bindings[language]
                counter = 0
                text_label = ""
                while (lang_bindings[counter] != "(also)"):
                    text_label += lang_bindings[counter] + "\n"
                    counter += 1                
                bindings_common = tk.Label(self, text = text_label, bg = "white")
                bindings_common.grid(row = 1, column = 0, sticky = "n")
                
                text_label = ""
                counter += 1
                while (counter != len(lang_bindings)):
                    text_label += lang_bindings[counter] + "\n"
                    counter += 1
                bindings_also = tk.Label(self, text = text_label, bg = "white", padx = 30)
                bindings_also.grid(row = 1, column = 1, sticky = "n")