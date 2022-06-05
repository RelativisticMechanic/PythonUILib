import engine2D
import engine2D_UI
import engine2D_plot
import math

screen_w = 800
screen_h = 800

class TransparentFileListBox(engine2D_UI.FileListBox):

    def Draw(self, elapsed):
        super().Draw(elapsed)
    
class imagenplot(engine2D.Object):

    def Draw(self, elapsed):
        engine2D_plot.PlotFunction(lambda x: math.sin(x), 20, 20, 300, 300, -10, 10, -5, 5)


def callback(id, i):
    console.GetInput(">:")
    return

def progressbar_timer_callback(id):
    progressbar.SetProgress(progressbar.progress+10)
    timer.Start()

def file_list_callback(id, type, s):
    print(s)

def dialogbox_callback(id, b):
    if(b):
        engine2D.AddObject(engine2D_UI.Label("You pressed OK!", 5, 5, font))
    else:
        engine2D.AddObject(engine2D_UI.Label("You pressed Cancel!", 5, 5, font))

engine2D.Init(screen_w, screen_h)
engine2D.SetCaption("UI test")
font = engine2D.BitmapFont("./cp8x16.png", 8, 16, ch_offset=32)
console = engine2D_UI.Console(40, 600, 500, 100, font, callback)
console.PutString("This is a console test! You can type stuff below!\n")
console.GetInput(">:")
lbox = TransparentFileListBox("C:\\Users\\", file_list_callback, 16, 400, 376, 150, font)
progressbar = engine2D_UI.ProgressBar(40, 40, 200, 18, font)
timer = engine2D.Timer(1000, progressbar_timer_callback)
engine2D.AddObject(engine2D_UI.PictureBox("./picture.png", 600, 100, 200, 200))
engine2D.AddObject(lbox)
engine2D.AddObject(console)
engine2D.AddObject(imagenplot())
engine2D.AddObject(progressbar)
engine2D.AddObject(timer)
engine2D.AddObject(engine2D_UI.TextBox(10, 10, 300, font))
timer.Start()
engine2D.AddObject(engine2D_UI.DialogBoxOKCancel("Hello World! This is a message from a Dialog box!", 200, 200, font, (60, 60, 60), dialogbox_callback))
engine2D.Loop(60)