import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image
import sqlite3
import math

def setActive(btn):
    btn.configure(bg= "#0b78de")

    
# def deactivate(btn):
#     btn.config(background= "Blue")

#Window initialisation
window = tk.Tk()
window.title('DATA EXTRACTION')
window.geometry('600x600')
window.grid_columnconfigure(0, weight= 1)
window.grid_columnconfigure(1, weight= 1)
window.grid_columnconfigure(2, weight= 1)
btns = []

btn1 = tk.Button(window, text= "Hello", bg= "White", fg= "Black", command= lambda: setActive(btn1))
btns.append(btn1)
btn1.grid(row= 0, column= 0)

btn2 = tk.Button(window, text="Submit", background= "Gray", highlightbackground= "Blue", highlightthickness= 2, width= 12, height= 3, font= ("Arial", 12), command= lambda: setActive(btn2))
btns.append(btn2)
btn2.grid(row= 0, column= 1)

window.mainloop()