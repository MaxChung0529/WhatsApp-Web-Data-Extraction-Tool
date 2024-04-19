import sqlite3

con = sqlite3.connect("sqlite.db")
cur = con.cursor()

#Find entities of that category
category = "PERSON"
entity_query = f'''SELECT text, COUNT(*) from entities
                        WHERE category="{category}"
                        GROUP BY text'''

#Find number of messages sent by both sides
contact_name = "Connie"
chat_num_query = f'''SELECT sender, COUNT(*) from messages
                    WHERE chat = "{contact_name}"
                    GROUP BY sender'''

#Find number of messages sent on the date
date_query = f'''SELECT date, sender, COUNT(*) from messages
                WHERE chat = "{contact_name}"
                GROUP BY date, sender'''

contact_name = "Max"
img_query = f'''SELECT sender, COUNT(*) from messages
                WHERE (type = "Image" OR type = "Images and texts")
                AND chat = "{contact_name}"
                GROUP BY sender'''


contact_name = "Max"
src_query = f'''SELECT img_src from messages
                WHERE  (type = "Image" OR type = "Images and texts")
                AND chat = "{contact_name}"'''

contact_name = "Max"
date_query = f'''SELECT date, COUNT(*) from messages
                WHERE chat = "{contact_name}" and date != "Unkown"
                GROUP BY date
                ORDER BY COUNT(*) desc'''

results = cur.execute(date_query)

#print(query)

for result in results:
    print(result)