from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Its tree view")
root.geometry("1200x600")

my_tree = ttk.Treeview(root)

my_tree['columns'] = ("Product","QNTY","Price")
my_tree.column("#0",width=0,stretch=NO)
my_tree.column("Product",anchor=W,width=120,minwidth=25)
my_tree.column("QNTY",anchor=CENTER,width=80,minwidth=25)
my_tree.column("Price",anchor=CENTER,width=120,minwidth=25)

my_tree.heading("#0",text="",anchor=W)
my_tree.heading("Product",text="Product",anchor=W)
my_tree.heading("QNTY",text="QNTY",anchor=CENTER)
my_tree.heading("Price",text="Price",anchor=CENTER)
data = [
    ["Tomato","1 kg","30rs"],["Mosambi","2 kg","30rs"],["Tomato","3 kg","30rs"]
]

count = 0
for record in data:
    my_tree.insert(parent='',index='end',iid=count,text="P",values=(record[0],record[1],record[2]))
    count +=1

'''
my_tree.insert(parent='',index='end',iid=0,text="Parent",values=("Tomato","1 kg","30rs"))
my_tree.insert(parent='',index='end',iid=1,text="Parent",values=("Mosambi","2 kg","30rs"))
my_tree.insert(parent='',index='end',iid=2,text="Parent",values=("Tomato","3 kg","30rs"))
'''
my_tree.pack(pady=20)
root.mainloop()