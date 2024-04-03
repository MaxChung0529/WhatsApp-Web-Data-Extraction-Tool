import emoji

def convert_emoji_to_text(emoji_text):
    text_with_emoji = emoji.demojize(emoji_text)
    return text_with_emoji

emoji_text = "I love Python! 😍"
converted_text = convert_emoji_to_text(emoji_text)
print(converted_text)