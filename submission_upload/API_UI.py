#!/usr/bin/env python3.7
#  -*- coding: utf-8 -*-
import tk as tk
from submission_upload.submission_API import *
try:
    from Tkinter import *
    from tkMessageBox import *
except ImportError:
    from tkinter import *


class MyFirstGUI:
    def __init__(self, master):
        # inital UI windows and config size
        self.master = master
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_size = str(640) + "x" + str(480) + "+0+0"
        master.title("A simple GUI")
        master.geometry(window_size)
        master.title("3PL upload Tool")
        master.configure(highlightcolor="black")

        # inial info button position and size
        # define click button event
        self.infoButton = Button(master, command=self.getInfo)
        self.infoButton.place(x=30, y=50, height=30, width=70)
        self.infoButton.configure(text='''Get Info''')

        # inial upload button position and size
        # define click button event
        self.uploadButton = Button(master, command=self.uploadButton)
        self.uploadButton.place(x=100, y=50, height=30, width=70)
        self.uploadButton.configure(text='''upload''')

        # inial clear button position and size
        # define clear button event
        self.clearButton = Button(master, command=self.clear)
        self.clearButton.place(x=170, y=50, height=30, width=70)
        self.clearButton.configure(text='''clear''')

        # inial statusbox position, size and font
        self.mesListbox = Text(master)
        self.mesListbox.place(x=20, y=100, height=300, width=550)
        self.mesListbox.configure(background="white")
        self.mesListbox.configure(font="TkFixedFont")
        self.mesListbox.configure(width=314)

    # unuse function
    def clear(self):
        self.mesListbox.delete(1.0, END)

    def getInfo(self):
        fingerprint, clientID = unzip_and_get_info()
        self.mesListbox.delete(1.0, END)
        self.mesListbox.insert(END, "FingerPrint:" + fingerprint + "\n")
        self.mesListbox.insert(END, "ClientID :" + clientID + "\n")

    def uploadButton(self):
        self.mesListbox.insert(END, "-------upload status-------""\n")
        upload()
        self.mesListbox.insert(END, "-------upload done-------""\n")


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()

