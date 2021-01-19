import tkinter as tk
import pyperclip

class DrawingTransformer(tk.Frame):
    LOCAL_IP = "localhost"
    
    CANVAS_SIDE = 300
    RECT_SIDE = 2
    
    def __init__(self, master, socket, sqlReader):
        tk.Frame.__init__(self, master)
        
        self.configure(background = "white")
        self.addCanvas()
        self.canvas.configure(background = "white")
        
        #
        self.f = open("charGestures.txt", "w+")
        #self.f.write("hello")
        #self.master.protocol("WM_DELETE_WINDOW", lambda : self.f.close())
        
        self.gui_socket = socket
        
        self.setStrokes()
        
        self.sqlReader = sqlReader
        self.result_char = ""
     
    def setStrokes(self):  
        self.strokes = []  
        self.strokesCount = 0
        
    def addCanvas(self):
        self.canvas = tk.Canvas(self, width = DrawingTransformer.CANVAS_SIDE, 
                           height = DrawingTransformer.CANVAS_SIDE)
        self.canvas.bind("<Button-1>", self.onPress)
        self.canvas.bind("<Button-3>", self.reset)
        self.canvas.bind("<B1-Motion>", self.onMove)
        self.canvas.bind("<ButtonRelease-1>", self.onRelease)
        self.canvas.pack()

    
    def onPress(self, event):
        self.strokes.append(list())
        self.strokes[self.strokesCount].append((event.x, event.y)) # avoids empty stroke
        self.prevX = event.x
        self.prevY = event.y
        
    def onMove(self, event):
        self.canvas.create_line(event.x, event.y, self.prevX, self.prevY, width = 2)
        self.strokes[self.strokesCount].append((event.x, event.y))
        self.prevX = event.x
        self.prevY = event.y
            
    def onRelease(self, event):
        self.strokesCount += 1
        
        if (self.strokesCount == 2):
            self.gui_socket.sendall(repr(self.strokes).encode("utf-8"))
            strokeIds = self.gui_socket.recv(16).decode("utf-8")
            parsedIds = strokeIds[1:len(strokeIds) - 1].split(" ")[0:2]
            self.result_char = self.sqlReader.select_new_char(parsedIds[0], parsedIds[1])
            
            #self.f.write(repr(self.strokes[0]))
            #self.f.write("\n")
            #self.message = resultChar + " copied"
            
            pyperclip.copy(self.result_char) 
            
    def get_result(self):
        return self.result_char
    
    def reset(self, event):
        self.canvas.delete("all")
        self.setStrokes() 

        