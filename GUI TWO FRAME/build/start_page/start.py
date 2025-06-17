import tkinter as tk
from pathlib import Path
from tkinter import Toplevel,Tk, Canvas, Entry, Text, Button, PhotoImage
from ..main_page.main_window import mainWindow

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"E:/Project/GUI TWO FRAME/build/start_page/assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Main window constructor
#root = tk.Tk()  # Make temporary window for app to start
#root.withdraw()  # WithDraw the window

def startWindow():
    Start()

class Start(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)

        self.geometry("1200x600+100+100")
        self.configure(bg = "#FFFFFF")

        self.canvas = Canvas(
            self,
            bg = "#FFFFFF",
             height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)

        self.canvas.create_text(
            98.0,
            0.0,
            anchor="nw",
            text="SELF CHECKOUT KIOSK",
            fill="#0C22E7",
            font=("MontserratRoman Black", 64 * -1)
        )

        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        self.start_button = Button(
            self.canvas,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=mainWindow,
            relief="flat"
        )
        self.start_button.place(x=430.0,y=332.0,width=354.0,height=79.4838714599609)
        
        self.resizable(False, False)
        self.mainloop()

#Start()