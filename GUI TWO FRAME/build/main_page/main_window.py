import tkinter as tk
from tkinter import *
from pathlib import Path
from tkinter import Toplevel,Tk, Canvas, Entry, Text, Button, PhotoImage
from tkinter import ttk
import random

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"E:/Project/GUI TWO FRAME/build/main_page/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

 #Main window constructor
#root = tk.Tk()  # Make temporary window for app to start
#root.withdraw()  # WithDraw the window

def mainWindow():
   #.place_forget()
   Main_window()

class Main_window(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)

        self.geometry("1200x600+100+100")
        self.configure(bg = "#FFFFFF")

        self.canvas = Canvas(self,bg = "#FFFFFF",height = 601,width = 1200,bd = 0,highlightthickness = 0,relief = "ridge")
        self.canvas.place(x = 0, y = 0)
        self.canvas.create_text(134.80865478515625,42.47597659432165,anchor="nw",text="PLACE THE ITEM IN KIOSK",fill="#5E95FF",font=("Montserrat Bold", 26 * -1))
        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        self.add_button = Button(
            self.canvas,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.show_data,
            relief="flat"
        )
        self.add_button.place(
            x=330.9999990463257,
            y=105.99998812696492,
            width=460.1075148164746,
            height=48.59711299145067
        )
        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        self.checkout_button = Button(
            self.canvas,
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
            relief="flat"
        )
        self.checkout_button.place(
            x=927.0,
            y=499.99997655535117,
            width=174.0621602497995,
            height=48.22581719001755
        )
        '''
        self.canvas.create_rectangle(
            90.0,
            182.000003721565,
            1101.0,
            485.000003721565,
            fill="#D9D9D9",
            outline="")
        '''
        self.my_tree = ttk.Treeview(self)

        self.my_tree['columns'] = ("Product", "QNTY", "Price")
        self.my_tree.column("#0", width=0, stretch=NO)
        self.my_tree.column("Product", anchor=W, width=120, minwidth=25)
        self.my_tree.column("QNTY", anchor=CENTER, width=80, minwidth=25)
        self.my_tree.column("Price", anchor=CENTER, width=120, minwidth=25)

        self.my_tree.heading("#0", text="", anchor=W)
        self.my_tree.heading("Product", text="Product", anchor=W)
        self.my_tree.heading("QNTY", text="QNTY", anchor=CENTER)
        self.my_tree.heading("Price", text="Price", anchor=CENTER)

        self.my_tree.place(x=90.0, y=182.0, width=1000, height=300.0)
        self.data = [
            ["Tomato", "1 kg", "30rs"], ["Mosambi", "2 kg", "30rs"], ["Apple", "3 kg", "30rs"]
        ]        

        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        self.remove_button = Button(
            self.canvas,
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_3 clicked"),
            relief="flat"
        )
        self.remove_button.place(
            x=48.0,
            y=499.95168149962797,
            width=211.26855010077998,
            height=48.27411224574075
        )
        
        self.count = 0 
        self.resizable(False, False)
        self.mainloop()
    def show_data(self):
        
        
        self.my_tree.insert(parent='',index='end',iid=self.count,text="Parent",values=self.data[self.count])
        
        self.count +=1
    

#Main_window()