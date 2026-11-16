import tkinter as tk
from build.start_page.start import startWindow
from build.main_page.main_window import mainWindow

# Main window constructor
root = tk.Tk()  # Make temporary window for app to start
root.withdraw()  # WithDraw the window


if __name__ == "__main__":

    startWindow()
    #mainWindow()

    root.mainloop()
