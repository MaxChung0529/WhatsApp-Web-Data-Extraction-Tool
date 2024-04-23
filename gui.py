import tkinter as tk
from tkinter import ttk
from tkinter import *
import sqlite3
import os
import matplotlib.pyplot as plt
from sys import platform
import subprocess

global con
global cur
global btns
global lbls
global btn_font_size_sml
global btn_font_size_md
global btn_font_size_lg
global font_btns
global current_font_size

btn_font_size_sml = 10
btn_font_size_md = 15
btn_font_size_lg = 20
lbl_font_size_sml = 12
lbl_font_size_md = 15
lbl_font_size_lg = 24
current_font_size = btn_font_size_md

btns = []
lbls = []
font_btns = []

con = sqlite3.connect("sqlite.db")
cur = con.cursor()

def pop_btns():
    global btns
    if len(btns) > 5:
        btns = btns[:5]

def choose_btn(button):
    pop_btns()
    for btn in btns:
        btn.configure(bg= "White")
    if button != None:
        button.configure(bg= "#148eff")

def change_font_size(size, font_btn):
    global current_font_size

    if size == "LARGE":
        btn_size = btn_font_size_lg
        lbl_size = btn_font_size_lg
        current_font_size = btn_font_size_lg
    elif size == "MIDDLE":
        btn_size = btn_font_size_md
        lbl_size = lbl_font_size_md
        current_font_size = btn_font_size_md
    elif size == "SMALL":
        btn_size = btn_font_size_sml
        lbl_size = btn_font_size_sml
        current_font_size = btn_font_size_sml

    for button in font_btns:
        button.configure(bg= "White")
    font_btn.configure(bg= "#148eff")

    for btn in btns:
        btn.configure(font=("Arial", btn_size))
    for lbl in lbls:
        lbl.configure(font=("Arial", lbl_size))    

def show_num(num, dates_frame):
    global lbls

    show_num = ttk.Label(dates_frame, text= str(num), font=("Arial", current_font_size) )
    lbls.append(show_num)
    show_num.grid(row= 1, column= 1, rowspan= 2)

def msg_page(detail_header, content_frame, btn):
    choose_btn(btn)
    destroy(content_frame)
    pop_btns()
    global lbls
    lbls = []

    #Query to find the chat names
    contact_query = '''SELECT DISTINCT chat from messages
                        ORDER BY chat asc'''
    contacts = []

    results = con.execute(contact_query)

    for result in results:
        contacts.append(result)

    detail_header.config(text= "Chat analysis")

    combo_frame = tk.Frame(content_frame, width= 250, height= 550, highlightthickness= 2, highlightbackground= "Gray")
    combo_frame.propagate(False)
    combo_frame.place(relx= 0.15, rely= 0.5, anchor= "center")

    #Choose categories
    chat_label = ttk.Label(combo_frame, text= "Choose the chat you want", font=("Arial", current_font_size), wraplength= 200)
    chat_label.place(relx= 0.5, rely= 0.3, anchor= "center")
    lbls.append(chat_label)

    chats = ttk.Combobox(combo_frame, state= "readonly", values= contacts, width= 15, font= ("Arial", current_font_size))
    chats.place(relx= 0.5, rely= 0.5, anchor= "center")
    lbls.append(chats)

    chats_btn = tk.Button(combo_frame, text= "Show", command= lambda:get_msg_data(chats.get(), content_frame), width= 12, font= ("Arial", current_font_size), relief= RAISED)
    chats_btn.place(relx= 0.5, rely= 0.8, anchor= "center")
    btns.append(chats_btn)

def get_msg_data(contact_name, content_frame):

    plt.close()

    global lbls
    global btns
    
    if contact_name == "":
        return

    #Find number of messages sent by both sides
    chat_num_query = f'''SELECT sender, COUNT(*) from messages
                        WHERE chat = "{contact_name}"
                        GROUP BY sender'''
    
    chat_results = cur.execute(chat_num_query)

    keywords_frame = tk.Frame(content_frame, width= 700, height= 600, highlightbackground= "Gray", highlightthickness= 2)
    keywords_frame.propagate(False)
    keywords_frame.grid_propagate(False)
    keywords_frame.place(relx= 0.6, rely= 0.5, anchor= "center")
    keywords_frame.grid_columnconfigure(0, weight= 1)
    keywords_frame.grid_columnconfigure(1, weight= 1)

    for i in range(0,15):
        if i < 15:
            keywords_frame.grid_rowconfigure(i, weight= 1)
        else:
            keywords_frame.grid_rowconfigure(i, weight= 2)

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
    total_label = ttk.Label(keywords_frame, text= "Total messages sent: ", font=("Arial", current_font_size) )
    total_label.grid(row= 0, column= 0)
    lbls.append(total_label)
    num_label = ttk.Label(keywords_frame, text= str(msg_num), font=("Arial", current_font_size) )
    num_label.grid(row= 0, column= 1)
    lbls.append(num_label)
    
    user_label = ttk.Label(keywords_frame, text= "No. messages sent by you:", font=("Arial", current_font_size) )
    user_label.grid(row= 1, column= 0)
    lbls.append(user_label)
    user_num_label = ttk.Label(keywords_frame, text= str(user_num), font=("Arial", current_font_size) )
    user_num_label.grid(row= 1, column= 1)
    lbls.append(user_num_label)
    
    other_user_label = ttk.Label(keywords_frame, text= f"No. messages sent by {contact_name}:", font=("Arial", current_font_size) )
    other_user_label.grid(row= 2, column= 0)
    lbls.append(other_user_label)
    other_user_num_label = ttk.Label(keywords_frame, text= str(other_user_num), font=("Arial", current_font_size) )
    other_user_num_label.grid(row= 2, column= 1)
    lbls.append(other_user_num_label)

    # Separator object
    separator = ttk.Separator(keywords_frame, orient='horizontal')
    separator.grid(row= 3, columnspan= 2, sticky= "ew")

    #Find the number of images sent
    img_query = f'''SELECT sender, COUNT(*) from messages
                    WHERE (type = "Image" OR type = "Image and texts")
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
    total_img_label = ttk.Label(keywords_frame, text= "Total images sent: ", font=("Arial", current_font_size) )
    total_img_label.grid(row= 4, column= 0)
    lbls.append(total_img_label)
    num_label = ttk.Label(keywords_frame, text= str(img_total), font=("Arial", current_font_size))
    num_label.grid(row= 4, column= 1)
    lbls.append(num_label)
    
    user_img_label = ttk.Label(keywords_frame, text= "No. images sent by you:", font=("Arial", current_font_size) )
    user_img_label.grid(row= 5, column= 0)
    lbls.append(user_img_label)
    user_img_num_label = ttk.Label(keywords_frame, text= str(user_img_num), font=("Arial", current_font_size) )
    user_img_num_label.grid(row= 5, column= 1)
    lbls.append(user_img_num_label)
    
    other_user_img_label = ttk.Label(keywords_frame, text= f"No. images sent by {contact_name}:", font=("Arial", current_font_size) )
    other_user_img_label.grid(row= 6, column= 0)
    lbls.append(other_user_img_label)
    other_user_img_num_label = ttk.Label(keywords_frame, text= str(other_user_img_num), font=("Arial", current_font_size) )
    other_user_img_num_label.grid(row= 6, column= 1)
    lbls.append(other_user_img_num_label)
    
    # Separator object
    separator = ttk.Separator(keywords_frame, orient='horizontal')
    separator.grid(row= 7, columnspan= 2, sticky= "ew")

    #Find the number of videos sent
    vid_query = f'''SELECT sender, COUNT(*) from messages
                    WHERE (type = "Video" OR type = "Video and texts")
                    AND chat = "{contact_name}"
                    GROUP BY sender'''
    
    vid_results = con.execute(vid_query)

    vid_total = 0
    user_vid_num = 0
    other_user_vid_num = 0

    for result in vid_results:
        vid_total += result[1]
        if (result[0] == contact_name):
            other_user_vid_num += result[1]
        else:
            user_vid_num += result[1]    

    #Total images sent
    total_vid_label = ttk.Label(keywords_frame, text= "Total videos sent: ", font=("Arial", current_font_size) )
    total_vid_label.grid(row= 8, column= 0)
    lbls.append(total_vid_label)
    num_label = ttk.Label(keywords_frame, text= str(vid_total), font=("Arial", current_font_size))
    num_label.grid(row= 8, column= 1)
    lbls.append(num_label)
    
    user_vid_label = ttk.Label(keywords_frame, text= "No. videos sent by you:", font=("Arial", current_font_size) )
    user_vid_label.grid(row= 9, column= 0)
    lbls.append(user_vid_label)
    user_vid_num_label = ttk.Label(keywords_frame, text= str(user_vid_num), font=("Arial", current_font_size) )
    user_vid_num_label.grid(row= 9, column= 1)
    lbls.append(user_vid_num_label)
    
    other_user_vid_label = ttk.Label(keywords_frame, text= f"No. videos sent by {contact_name}:", font=("Arial", current_font_size) )
    other_user_vid_label.grid(row= 10, column= 0)
    lbls.append(other_user_vid_label)
    other_user_vid_num_label = ttk.Label(keywords_frame, text= str(other_user_vid_num), font=("Arial", current_font_size) )
    other_user_vid_num_label.grid(row= 10, column= 1)
    lbls.append(other_user_vid_num_label)
    
    # Separator object
    separator = ttk.Separator(keywords_frame, orient='horizontal')
    separator.grid(row= 11, columnspan= 2, sticky= "ew")

    #Find the number of messages sent grouped by date
    date_query = f'''SELECT date, COUNT(*) from messages
                WHERE chat = "{contact_name}" and date != "Unkown"
                GROUP BY date
                ORDER BY COUNT(*) desc'''
    
    dates = []
    date_array = []
    date_msg_num_array = []

    for result in con.execute(date_query):
        date_array.append(result[0])
        date_msg_num_array.append(result[1])
        dates.append(result)

    #Most messages sent in a day
    most_msg_lbl = ttk.Label(keywords_frame, text= "Most messages sent on: ", font=("Arial", current_font_size) )
    most_msg_lbl.grid(row= 12, column= 0)
    lbls.append(most_msg_lbl)
    date_label = ttk.Label(keywords_frame, text= str(dates[0][0]), font=("Arial", current_font_size) )
    date_label.grid(row= 12, column= 1)
    lbls.append(date_label)

    date_msg_lbl = ttk.Label(keywords_frame, text= f"No. messages sent on {dates[0][0]}:", font=("Arial", current_font_size) )
    date_msg_lbl.grid(row= 13, column= 0)
    lbls.append(date_msg_lbl)
    date_msg_num_label = ttk.Label(keywords_frame, text= str(dates[0][1]), font=("Arial", current_font_size) )
    date_msg_num_label.grid(row= 13, column= 1)
    lbls.append(date_msg_num_label)
    
    # Separator object
    separator = ttk.Separator(keywords_frame, orient='horizontal')
    separator.grid(row= 14, columnspan= 2, sticky= "ew")

    dates_frame = tk.Frame(keywords_frame, height= 100)
    dates_frame.grid(row= 15, columnspan= 2, sticky= "ew")
    dates_frame.grid_rowconfigure(0, weight= 3)
    dates_frame.grid_rowconfigure(1, weight= 1)
    # dates_frame.grid_rowconfigure(2, weight= 1)
    dates_frame.grid_columnconfigure(0, weight= 1)
    dates_frame.grid_columnconfigure(1, weight= 1)

    dates_only = []
    for date in dates:
        dates_only.append(date[0])     

    dates_lbl = ttk.Label(dates_frame, text="Messages sent on different dates", font=("Arial", current_font_size) )
    dates_lbl.grid(row= 0, column= 0)
    lbls.append(dates_lbl)

    show_date_btn = tk.Button(dates_frame, text= "Show graph", command= lambda: show_date_graph(date_array, date_msg_num_array), width= 10, height= 1, font= ("Arial", current_font_size), relief= RAISED)
    show_date_btn.grid(row= 0, column= 1)
    btns.append(show_date_btn)

def keyword_page(detail_header, content_frame, btn):
    choose_btn(btn)
    destroy(content_frame)
    pop_btns()

    global lbls
    lbls = []

    categories = ["PERSON", "ORG", "GPE", "EVENTS"]
    detail_header.config(text= "Named entities")

    combo_frame = tk.Frame(content_frame, width= 250, height= 550, highlightthickness= 2, highlightbackground= "Gray")
    combo_frame.propagate(False)
    combo_frame.place(relx= 0.15, rely= 0.5, anchor= "center")

    #Choose categories
    cats_label = ttk.Label(combo_frame, text= "Choose the category of keywords you want", font=("Arial", current_font_size), wraplength= 200)
    cats_label.place(relx= 0.5, rely= 0.3, anchor= "center")
    lbls.append(cats_label)

    cats = ttk.Combobox(combo_frame, state= "readonly", values= categories,width= 15, font= ("Arial", current_font_size))
    cats.place(relx= 0.5, rely= 0.5, anchor= "center")
    lbls.append(cats)

    cats_btn = tk.Button(combo_frame, text= "Show", command= lambda:get_keywords(cats.get(), content_frame), width= 12, font= ("Arial", current_font_size), relief= RAISED)
    cats_btn.place(relx= 0.5, rely= 0.8, anchor= "center")
    btns.append(cats_btn)

def get_keywords(category, content_frame):

    global lbls

    #Find entities of that category
    entity_query = f'''SELECT text, COUNT(*) from entities
                            WHERE category="{category}"
                            GROUP BY text
                            ORDER BY COUNT(*) desc
                            LIMIT 10'''
    
    results = cur.execute(entity_query)
    keywords_frame = tk.Frame(content_frame, width= 700, height= 600, highlightbackground= "Gray", highlightthickness= 2)
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
    
    entity_label = ttk.Label(keywords_frame, text= "Keywords ", font=("Arial", current_font_size) )
    entity_label.grid(row= 0, column= 0)
    lbls.append(entity_label)
    num_label = ttk.Label(keywords_frame, text= " Appearance", font=("Arial", current_font_size) )
    num_label.grid(row= 0, column= 2)
    lbls.append(num_label)
    
    count = 1
    for row in results:
        tmp_ent_lbl = ttk.Label(keywords_frame, text= row[0], font=("Arial", current_font_size) )
        tmp_ent_lbl.grid(row= count, column= 0)
        lbls.append(tmp_ent_lbl)
        tmp_num_lbl = ttk.Label(keywords_frame, text= row[1], font=("Arial", current_font_size) ) 
        tmp_num_lbl.grid(row= count, column= 2)
        lbls.append(tmp_num_lbl)
        count += 1

def main_page(detail_header, content_frame):

    destroy(content_frame)
    detail_header.config(text= "Home")
    choose_btn(None)
    pop_btns()

    global lbls
    lbls = []

    label1 = tk.Label(content_frame, text= "Keywords - Keywords mentioned in the chats (PERSON, ORGANISATION,...)", font=("Arial", current_font_size))
    lbls.append(label1)
    label1.place(relx= 0.5, rely= 0.20, anchor= "center")

    label2 = tk.Label(content_frame, text= "Messages - Overview of chat data (How many messages was sent,...)", font=("Arial", current_font_size))
    lbls.append(label2)
    label2.place(relx= 0.5, rely= 0.35, anchor= "center")

    label3 = tk.Label(content_frame, text= "Images - Open the file containing extracted images in file explorer", font=("Arial", current_font_size))
    lbls.append(label3)
    label3.place(relx= 0.5, rely= 0.49, anchor= "center")

    label4 = tk.Label(content_frame, text= "Videos - Open the file containing extracted videos in file explorer", font=("Arial", current_font_size))
    lbls.append(label4)
    label4.place(relx= 0.5, rely= 0.63, anchor= "center")

    label5 = tk.Label(content_frame, text= "Font size buttons - Change font sizes", font=("Arial", current_font_size))
    lbls.append(label5)
    label5.place(relx= 0.5, rely= 0.85, anchor= "center")
    

def destroy(content_frame):
    for frame in content_frame.winfo_children():
        frame.destroy()

def open_images_folder():
    path = "images"
    if platform == "win32":
        os.startfile(path)
    elif platform == "darwin":
        subprocess.call(['open', path])

def open_videos_folder():
    path = "videos"
    if platform == "win32":
        os.startfile(path)
    elif platform == "darwin":
        subprocess.call(['open', path])

def show_date_graph(x, y):
    
    plt.xlabel("Dates", fontweight='bold', color = 'black', fontsize='15', horizontalalignment='center')
    plt.ylabel("Messages sent", fontweight='bold', color = 'black', fontsize='15', horizontalalignment='center')

    plt.plot(x,y)
    plt.show()

def overview():

    windowScreen = tk.Tk()
    windowScreen.title('DATA OVERVIEW')
    windowScreen.geometry('1280x720')
    windowScreen.grid_columnconfigure(0, weight= 1)
    windowScreen.grid_rowconfigure(0, weight= 1)
    window = tk.Frame(windowScreen, background= "#FFFFFF")
    window.grid(row= 0, column= 0, sticky= "nesw")
    window.grid_columnconfigure(0, weight= 1)
    window.grid_columnconfigure(1, weight= 12)
    window.grid_rowconfigure(0, weight= 1)
    
    

    #Options
    option_frame = tk.Frame(window, bg= "#545454",width= 120, padx= 0)
    option_frame.grid(row= 0, column= 0, sticky= 'nesw')
    option_frame.grid_propagate(False)

    option_frame.grid_columnconfigure(0, weight= 1)
    option_frame.grid_rowconfigure(0, weight= 5)
    option_frame.grid_rowconfigure(1, weight= 2)
    option_frame.grid_rowconfigure(2, weight= 2)
    option_frame.grid_rowconfigure(3, weight= 2)
    option_frame.grid_rowconfigure(4, weight= 2)
    option_frame.grid_rowconfigure(5, weight= 5)

    btn1 = tk.Button(option_frame, text= "Keywords", command= lambda:keyword_page(detail_header, content_frame, btn1), font=("Arial", btn_font_size_sml), relief= RAISED)
    btns.append(btn1)
    btn1.grid(column= 0, row= 1)

    btn2 = tk.Button(option_frame, text="Messages", command= lambda:msg_page(detail_header, content_frame, btn2), font=("Arial", btn_font_size_sml), relief= RAISED)
    btns.append(btn2)
    btn2.grid(column= 0, row= 2)

    btn3 = tk.Button(option_frame, text="Images", command= open_images_folder, font=("Arial", btn_font_size_sml), relief= RAISED)
    btns.append(btn3)
    btn3.grid(column= 0, row= 3)

    btn4 = tk.Button(option_frame, text="Videos", command= open_videos_folder, font=("Arial", btn_font_size_sml), relief= RAISED)
    btns.append(btn4)
    btn4.grid(column= 0, row= 4)

    font_size_frame = tk.Frame(option_frame, bg= "#545454", height= 50)
    font_size_frame.grid(column= 0, row= 5, sticky= "nesw")
    font_size_frame.grid_columnconfigure(0, weight= 1)
    font_size_frame.grid_columnconfigure(1, weight= 1)
    font_size_frame.grid_columnconfigure(2, weight= 1)
    font_size_frame.grid_rowconfigure(0, weight= 1)
    font_size_frame.grid_propagate(False)

    sml_font_btn = tk.Button(font_size_frame, text="Aa", font=("Arial", btn_font_size_sml), command= lambda: change_font_size("SMALL", sml_font_btn))
    sml_font_btn.grid(column= 0, row= 0)
    font_btns.append(sml_font_btn)

    md_font_btn = tk.Button(font_size_frame, text="Aa", font=("Arial", btn_font_size_md), command= lambda: change_font_size("MIDDLE", md_font_btn))
    md_font_btn.grid(column= 1, row= 0)
    font_btns.append(md_font_btn)

    lg_font_btn = tk.Button(font_size_frame, text="Aa", font=("Arial", btn_font_size_lg), command= lambda: change_font_size("LARGE", lg_font_btn))
    lg_font_btn.grid(column= 2, row= 0)
    font_btns.append(lg_font_btn)

    detail_frame = tk.Frame(window, bg= "#262626")
    detail_frame.grid_propagate(False)
    detail_frame.grid(row= 0, column= 1, sticky= "nesw")

    detail_frame.grid_columnconfigure(0, weight= 1)
    detail_frame.grid_rowconfigure(0, weight= 1)
    detail_frame.grid_rowconfigure(1, weight= 18)

    detail_header = tk.Label(detail_frame, bg= "#0b78de", text= "Home", font= ("Arial", 30), padx= 0, pady= 0)
    detail_header.grid(row= 0, column= 0, sticky= "nesw")

    content_frame = tk.Frame(detail_frame)
    content_frame.propagate(False)
    content_frame.grid(row= 1, column= 0, sticky= "nesw")
    content_frame.grid_columnconfigure(0, weight= 1)
    content_frame.grid_columnconfigure(1, weight= 4)
    content_frame.grid_rowconfigure(0, weight= 1)

    home_btn = tk.Button(option_frame, text= "Home", font= ("Arial", current_font_size), command= lambda: main_page(detail_header, content_frame))
    btns.append(home_btn)
    home_btn.grid(column= 0, row= 0)

    main_page(detail_header, content_frame)

    change_font_size("MIDDLE", md_font_btn)
    
    #Run
    window.mainloop()

if __name__ == '__main__':
    overview()    