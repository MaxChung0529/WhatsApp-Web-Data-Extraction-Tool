import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import sqlite3


def msg_page():
    destroy()

    #Query to find the chat names
    contact_query = '''SELECT DISTINCT chat from messages
                        ORDER BY chat asc'''
    contacts = []

    results = con.execute(contact_query)

    for result in results:
        contacts.append(result)

    detail_header.config(text= "Chat analysis")

    combo_frame = tk.Frame(content_frame, width= 250, height= 350, highlightthickness= 2, highlightbackground= "Gray")
    combo_frame.propagate(False)
    combo_frame.place(relx= 0.15, rely= 0.5, anchor= "center")

    #Choose categories
    chat_label = ttk.Label(combo_frame, text= "Choose the chat you want", font=("Arial", 15))
    chat_label.place(relx= 0.5, rely= 0.35, anchor= "center")

    chats = ttk.Combobox(combo_frame, state= "readonly", values= contacts, width= 15, font= ("Arial", 12))
    chats.place(relx= 0.5, rely= 0.5, anchor= "center")

    chats_btn = ttk.Button(combo_frame, text= "Show", command= lambda:get_msg_data(chats.get()), width= 20)
    chats_btn.place(relx= 0.5, rely= 0.6, anchor= "center")

def get_msg_data(contact_name):
    
    #Find number of messages sent by both sides
    chat_num_query = f'''SELECT sender, COUNT(*) from messages
                        WHERE chat = "{contact_name}"
                        GROUP BY sender'''
    
    chat_results = cur.execute(chat_num_query)

    keywords_frame = tk.Frame(content_frame, width= 500, height= 600, background= "White", highlightbackground= "Gray", highlightthickness= 2)
    keywords_frame.propagate(False)
    keywords_frame.grid_propagate(False)
    keywords_frame.place(relx= 0.6, rely= 0.5, anchor= "center")
    keywords_frame.grid_columnconfigure(0, weight= 1)
    keywords_frame.grid_columnconfigure(1, weight= 1)

    for i in range(0,10):
        keywords_frame.grid_rowconfigure(i, weight= 1)


    msg_num = 0
    user_num = 0
    other_user_num = 0

    for result in chat_results:
        msg_num += result[1]
        if (result[0] == contact_name):
            other_user_num += result[1]
        else:
            user_num += result[1]    

    #Total messages sent
    total_label = ttk.Label(keywords_frame, text= "Total messages sent: ", font=("Arial", 15))
    total_label.grid(row= 0, column= 0)
    num_label = ttk.Label(keywords_frame, text= str(msg_num), font=("Arial", 15))
    num_label.grid(row= 0, column= 1)
    
    user_label = ttk.Label(keywords_frame, text= "No. messages sent by you:", font=("Arial", 15))
    user_label.grid(row= 1, column= 0)
    user_num_label = ttk.Label(keywords_frame, text= str(user_num), font=("Arial", 15))
    user_num_label.grid(row= 1, column= 1)
    
    other_user_label = ttk.Label(keywords_frame, text= f"No. messages sent by {contact_name}:", font=("Arial", 15))
    other_user_label.grid(row= 2, column= 0)
    other_user_num_label = ttk.Label(keywords_frame, text= str(other_user_num), font=("Arial", 15))
    other_user_num_label.grid(row= 2, column= 1)

    # Separator object
    separator = ttk.Separator(keywords_frame, orient='horizontal')
    separator.grid(row= 3, columnspan= 2, sticky= "ew")

    #Find the number of images sent
    img_query = f'''SELECT sender, COUNT(*) from messages
                    WHERE (type = "Image" OR type = "Images and texts")
                    AND chat = "{contact_name}"
                    GROUP BY sender'''
    
    img_results = con.execute(img_query)

    img_total = 0
    user_img_num = 0
    other_user_img_num = 0

    for result in img_results:
        img_total += result[1]
        if (result[0] == contact_name):
            other_user_img_num += result[1]
        else:
            user_img_num += result[1]    

    #Total images sent
    total_img_label = ttk.Label(keywords_frame, text= "Total images sent: ", font=("Arial", 15))
    total_img_label.grid(row= 4, column= 0)
    num_label = ttk.Label(keywords_frame, text= str(img_total), font=("Arial", 15))
    num_label.grid(row= 4, column= 1)
    
    user_img_label = ttk.Label(keywords_frame, text= "No. images sent by you:", font=("Arial", 15))
    user_img_label.grid(row= 5, column= 0)
    user_img_num_label = ttk.Label(keywords_frame, text= str(user_img_num), font=("Arial", 15))
    user_img_num_label.grid(row= 5, column= 1)
    
    other_user_img_label = ttk.Label(keywords_frame, text= f"No. images sent by {contact_name}:", font=("Arial", 15))
    other_user_img_label.grid(row= 6, column= 0)
    other_user_img_num_label = ttk.Label(keywords_frame, text= str(other_user_img_num), font=("Arial", 15))
    other_user_img_num_label.grid(row= 6, column= 1)


def keyword_page():
    destroy()

    categories = ["PERSON", "ORG", "GPE", "EVENTS"]
    detail_header.config(text= "Named entities")

    combo_frame = tk.Frame(content_frame, width= 250, height= 350, highlightthickness= 2, highlightbackground= "Gray")
    combo_frame.propagate(False)
    #combo_frame.pack(anchor= "w")
    combo_frame.place(relx= 0.15, rely= 0.5, anchor= "center")

    #Choose categories
    cats_label = ttk.Label(combo_frame, text= "Choose the category of keywords you want", font=("Arial", 15), wraplength= 200)
    cats_label.place(relx= 0.5, rely= 0.35, anchor= "center")

    cats = ttk.Combobox(combo_frame, state= "readonly", values= categories,width= 15, font= ("Arial", 12))
    cats.place(relx= 0.5, rely= 0.5, anchor= "center")

    cats_btn = ttk.Button(combo_frame, text= "Show", command= lambda:get_keywords(cats.get()), width= 20)
    cats_btn.place(relx= 0.5, rely= 0.6, anchor= "center")

def get_keywords(category):
    #Find entities of that category
    entity_query = f'''SELECT text, COUNT(*) from entities
                            WHERE category="{category}"
                            GROUP BY text
                            ORDER BY COUNT(*) desc
                            LIMIT 10'''
    
    results = cur.execute(entity_query)
    keywords_frame = tk.Frame(content_frame, width= 500, height= 600, background= "White", highlightbackground= "Gray", highlightthickness= 2)
    keywords_frame.propagate(False)
    keywords_frame.grid_propagate(False)
    keywords_frame.place(relx= 0.6, rely= 0.5, anchor= "center")
    keywords_frame.grid_columnconfigure(0, weight= 3)
    keywords_frame.grid_columnconfigure(1, weight= 1)
    keywords_frame.grid_columnconfigure(2, weight= 3)

    for i in range(0,10):
        keywords_frame.grid_rowconfigure(i, weight= 1)

    # Separator object
    separator = ttk.Separator(keywords_frame, orient='vertical')
    separator.grid(rowspan= 11, column= 1, sticky= "ns")
    
    entity_label = ttk.Label(keywords_frame, text= "Keywords ", font=("Arial", 15))
    entity_label.grid(row= 0, column= 0)
    num_label = ttk.Label(keywords_frame, text= " Appearance", font=("Arial", 15))
    num_label.grid(row= 0, column= 2)
    
    count = 1
    for row in results:
        tmp_ent_lbl = ttk.Label(keywords_frame, text= row[0], font=("Arial", 12))
        tmp_ent_lbl.grid(row= count, column= 0)
        tmp_num_lbl = ttk.Label(keywords_frame, text= row[1], font=("Arial", 12)) 
        tmp_num_lbl.grid(row= count, column= 2)
        count += 1

def destroy():
    for frame in content_frame.winfo_children():
        frame.destroy()



con = sqlite3.connect("sqlite.db")
cur = con.cursor()

#Window initialisation
window = tk.Tk()
window.title('DATA EXTRACTION')
window.geometry('1280x720')
window.grid_columnconfigure(0, weight= 1)
window.grid_columnconfigure(1, weight= 12)
window.grid_rowconfigure(0, weight= 1)

#Options
#option_frame = tk.Frame(window, width= 200, height= 720, bg= "red")
option_frame = tk.Frame(window, bg= "#545454", padx= 0, pady= 50)
option_frame.grid(row= 0, column= 0, sticky= 'nesw')

option_frame.grid_columnconfigure(0, weight= 1)
option_frame.grid_rowconfigure(0, weight= 5)
option_frame.grid_rowconfigure(1, weight= 2)
option_frame.grid_rowconfigure(2, weight= 2)
option_frame.grid_rowconfigure(3, weight= 2)
option_frame.grid_rowconfigure(4, weight= 5)

keywords_img = PhotoImage(file= "assets\Keywords_btn.png")
btn1 = ttk.Button(option_frame, image= keywords_img, command= keyword_page)
btn1.grid(column= 0, row= 1)

btn2 = ttk.Button(option_frame, text="Messages", command= msg_page)
btn2.grid(column= 0, row= 2)

btn1 = ttk.Button(option_frame, text="Images", command= destroy)
btn1.grid(column= 0, row= 3)

detail_frame = tk.Frame(window, bg= "#262626")
detail_frame.grid(row= 0, column= 1, sticky= "nesw")

detail_frame.grid_columnconfigure(0, weight= 1)
detail_frame.grid_rowconfigure(0, weight= 1)
detail_frame.grid_rowconfigure(1, weight= 18)

detail_header = tk.Label(detail_frame, bg= "#0b78de", text= "LABEL", font= ("Arial", 30), padx= 0, pady= 0)
detail_header.grid(row= 0, column= 0, sticky= "nesw")

content_frame = tk.Frame(detail_frame)
content_frame.propagate(False)
content_frame.grid(row= 1, column= 0, sticky= "nesw")
content_frame.grid_columnconfigure(0, weight= 1)
content_frame.grid_columnconfigure(1, weight= 4)
content_frame.grid_rowconfigure(0, weight= 1)

#Run
window.mainloop()