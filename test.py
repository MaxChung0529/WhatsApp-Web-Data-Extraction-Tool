print("I'm here")

text = 'It’s no big deal'
text = text.replace("’","'")

print(text.encode('utf-8').decode('cp1252'))