import sqlite3

con = sqlite3.connect("sqlite.db")
cur = con.cursor()

#Find entities of that category
category = "PERSON"
entity_query = '''SELECT text, COUNT(*) from entities
                        WHERE category="''' + str(category) + '''"
                        GROUP BY text'''

#Find number of messages sent by both sides
contact_name = "Connie"
chat_num_query = '''SELECT sender, COUNT(*) from messages
                    WHERE chat = "''' + str(contact_name) + '''"
                    GROUP BY sender'''

#Find number of messages sent on the date
date_query = '''SELECT date, sender, COUNT(*) from messages
                WHERE chat = "''' + str(contact_name) + '''"
                GROUP BY date, sender'''

results = cur.execute(date_query)

#print(query)

for result in results:
    # if result[0] != contact_name:
    #     print(("You",result[1]))
    # else:    
    #     print(result)
    print(result)