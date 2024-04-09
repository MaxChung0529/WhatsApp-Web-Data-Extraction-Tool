import tkinter as tk
from tkinter import ttk
    
def start_window():

    #Window initialisation
    window = tk.Tk()
    window.title('DATA EXTRACTION')
    window.geometry('1280x720')

    #Main frame to start
    main_frame = ttk.Frame(window, width= 1280, height= 720)
    main_frame.pack()

    start_btn = tk.Button(master= main_frame, height= 4, width= 30,  text= "Start extraction")
    start_btn.place(relx=0.5, rely=0.5, anchor= "center")

    #Chat selection page
    chat_select_frame = ttk.Frame(window)

    page1_label = ttk.Label(master= chat_select_frame, text= "Select chats you want to extract")
    page1_label.pack()


    result_label = ttk.Label(master= chat_select_frame)
    result_label.pack()

    #Run
    window.mainloop()
