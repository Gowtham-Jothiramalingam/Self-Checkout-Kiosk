import tkinter as tk
from pathlib import Path
from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from tkinter import messagebox
import subprocess
import csv
import torch
from contextlib import contextmanager
import pathlib
import urllib.request
import numpy as np



OUTPUT_PATH = Path(__file__).parent
Start_ASSETS_PATH = OUTPUT_PATH / Path(r"E:/Project/GUI TWO FRAME/build/start_page/assets")
Main_ASSETS_PATH = OUTPUT_PATH / Path(r"E:/Project/GUI TWO FRAME/build/main_page/assets")
Payment_ASSETS_PATH = OUTPUT_PATH / Path(r"E:/Project/GUI TWO FRAME/build/payment_page/assets")

save_location = "E:/Project/Major project/Results/takpic/"

def start_relative_to_assets(path: str) -> Path:
    return Start_ASSETS_PATH / Path(path)
def main_relative_to_assets(path: str) -> Path:
    return Main_ASSETS_PATH / Path(path)
def payment_relative_to_assets(path: str) -> Path:
    return Payment_ASSETS_PATH / Path(path)

count = 0

camera = cv2.VideoCapture(0)
image_counter = 0
l1=[]
url = "http://192.168.43.92/"
@contextmanager
def set_posix_windows():
    posix_backup = pathlib.PosixPath
    try:
        pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup
EXPORT_PATH = pathlib.Path('C:/Users/gowth/Downloads/Yolov5x/best.pt')
with set_posix_windows():
    model = torch.hub.load('E:/Project/Major project/yolov5', 'custom',path = EXPORT_PATH,source='local')


root = tk.Tk() 
root.withdraw()  

def mainWindow():
    Main_window()

def paymentWindow():
    Payment()

total_cost = 0
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
            205.0,
            206.0,
            anchor="nw",
            text="SELF CHECKOUT KIOSK",
            fill="#0C22E7",
            font=("MontserratRoman Black", 64 * -1)
        )

        button_image_1 = PhotoImage(file=start_relative_to_assets("button_1.png"))
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

class Main_window(Toplevel):
    def __init__(self, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)

        self.geometry("1200x600+100+100")
        self.configure(bg = "#FFFFFF")

        self.canvas = Canvas(self,bg = "#FFFFFF",height = 601,width = 1200,bd = 0,highlightthickness = 0,relief = "ridge")
        self.canvas.place(x = 0, y = 0)
        self.canvas.create_text(376.0000114440918,11.999996606200284,anchor="nw",text="PLACE THE ITEM IN KIOSK",fill="#5E95FF",font=("Montserrat Bold", 26 * -1))
        button_image_1 = PhotoImage(
            file=main_relative_to_assets("button_1.png"))
        self.add_button = Button(
            self.canvas,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.capture_image,
            relief="flat"
        )
        self.add_button.place(
            x=333.00000190734863,
            y=62.99998812696492,
            width=460.1075148164746,
            height=48.59711299145067
        )
        button_image_2 = PhotoImage(
            file=main_relative_to_assets("button_2.png"))
        self.checkout_button = Button(
            self.canvas,
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=paymentWindow,
            relief="flat"
        )
        self.checkout_button.place(
            x=897.0,
            y=459.97490410971204,
            width=193.3779095123282,
            height=48.25088963565668
        )
    
        self.my_tree = ttk.Treeview(self)

        self.my_tree['columns'] = ("Product", "QNTY (in grams)", "Price (in Rs)")
        self.my_tree.column("#0", width=0, stretch=NO)
        self.my_tree.column("Product", anchor=W, width=120, minwidth=25)
        self.my_tree.column("QNTY (in grams)", anchor=CENTER, width=80, minwidth=25)
        self.my_tree.column("Price (in Rs)", anchor=CENTER, width=120, minwidth=25)

        self.my_tree.heading("#0", text="", anchor=W)
        self.my_tree.heading("Product", text="Product", anchor=W)
        self.my_tree.heading("QNTY (in grams)", text="QNTY", anchor=CENTER)
        self.my_tree.heading("Price (in Rs)", text="Price", anchor=CENTER)

        self.my_tree.place(x=90.0, y=131.0, width=1000, height=300.0)
        #self.data1 = [["Tomato", "1 kg", "30rs"], ["Mosambi", "2 kg", "30rs"], ["Apple", "3 kg", "30rs"]]        
        self.data = []
        self.data_cpy = []
        button_image_3 = PhotoImage(
            file=main_relative_to_assets("button_3.png"))
        self.remove_button = Button(
            self.canvas,
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.remove,
            relief="flat"
        )     
        self.remove_button.place(
            x=50.0,
            y=495.97653283280226,
            width=229.3640397614563,
            height=48.297600756316456
        )
        button_image_4 = PhotoImage(
            file=main_relative_to_assets("button_4.png"))
        self.cancel_button = Button(
            self.canvas,
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.destroy1,
            relief="flat"
        )
 
        self.cancel_button.place(
            x=904.0,
            y=533.9844326365036,
            width=186.03715636059133,
            height=48.241361108865135
        )
        
        self.count = 0 
        self.resizable(False, False)
        self.mainloop()

    def destroy1(self):
            global total_cost
            total_cost = 0
            self.destroy()

    def remove(self):
        x = self.my_tree.selection()
        #print(int(x[0]))
        self.data_cpy = [item for item in self.data_cpy if item[0] != int(x[0])]
        #print(self.data_cpy)
        global total_cost
        total_cost = 0
        for cost in self.data_cpy: 
            total_cost += cost[3]
            #print(total_cost)
        #print(total_cost)
        self.update_total_cost()
        for record in x:
            self.my_tree.delete(record)
        
    def get_data(self):
        self.n = urllib.request.urlopen(url).read()  # get the raw html data in bytes (sends request and warn our esp8266)
        self.n = self.n.decode("utf-8")  # convert raw html bytes format to string :3
        return self.n

    def update_total_cost(self):
        self.canvas.delete("total_cost_text")
        self.canvas.create_text(398.99999237060547, 508.0000271237784, anchor="nw",
                                text="TOTAL AMOUNT : " + str(total_cost) +" Rs", fill="#5E95FF",
                                font=("Montserrat Bold", 26 * -1), tag="total_cost_text")
    
    def capture_image(self):
        
        ret, frame = camera.read()
        self.image_name = f"{save_location}image.jpg"
        self.im = f"{save_location}image1.jpg"

        cv2.imwrite(self.image_name, frame)
        im = self.image_name
        results = model(im)
        results.save()

        df=results.pandas().xyxy[0]
        count_df = df['name'].value_counts().reset_index()
        count_df.columns = ['name', 'Count']
        max_index = count_df['Count'].idxmax()
        max_name = count_df.loc[max_index, 'name']
        
        #max_name = 'Potato'
        l=[]
        l1 = []
        st=max_name
        l1.append(self.count)
        l.append(max_name)
        l1.append(max_name)
        ld=self.get_data()
        #ld = 400
        l.append(ld)
        l1.append(ld)
        filename="C:/Users/gowth/Downloads/my_table4.csv"
        with open(filename,newline="") as file:
            r=csv.reader(file)
            for i in r:
                if i[1]==st:
                    #print("Cost : ",ld*int(i[2]))
                    cost = int(ld)*int(i[2])*0.001
                    cost=round(cost,2)
                    global total_cost
                    total_cost += cost
                    total_cost=round(total_cost,2)
                    #print(cost)
                    l.append(str(cost))
                    l1.append(cost)
                    
        self.data.append(l)
        self.data_cpy.append(l1)
        #print(self.data)
        #print(self.data_cpy)
        self.update_total_cost()
        self.my_tree.insert(parent='',index='end',iid=self.count,text="Parent",
                            values=self.data[self.count])
        
        self.count +=1

class Payment(Toplevel):
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
            357.0,
            9.000013355083865,
            anchor="nw",
            text="PAY HERE",
            fill="#5E95FF",
            font=("Montserrat Bold", 96 * -1)
        )

        qr_image_1 = PhotoImage(file=payment_relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(
                            599.0,
                            323.0,
                            image=qr_image_1
                        )
        button_image_1 = PhotoImage(file=payment_relative_to_assets("button_1.png"))
        self.back_button = Button(
            self.canvas,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.destroy,
            relief="flat"
        )
        self.back_button.place(
            x=83.0,
            y=536.000017621813,
            width=211.26927952970442,
            height=48.83606246040631
        )

        button_image_2 = PhotoImage(file=payment_relative_to_assets("button_2.png"))
        self.finish_button = Button(
            self.canvas,
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.destroyed,
            relief="flat"
        )
        self.finish_button.place(
            x=869.0,
            y=532.000017621813,
            width=211.26855010077998,
            height=48.27411224574075
        )
        
        self.resizable(False, False)
        self.mainloop()

    def destroyed(self):
        global total_cost
        total_cost = 0
        self.destroy()
        Start()
    
Start()