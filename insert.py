def insert(time, sender, texts, con, cur):
    
    #query = 'INSERT INTO messages(time, sender, texts) VALUES (' + str(time) + ', ' + str(sender) + ', ' + str(texts) + ')'

    cur.execute('INSERT INTO messages (time, sender, texts) VALUES (?,?,?)',(str(time),str(sender),str(texts)))

    #query = 'INSERT INTO messages (time, sender, texts) VALUES (?,?,?)'
    #tuple = {'n':str(time),'f':str(sender),'r':str(texts)}

    #cur.execute(query)

