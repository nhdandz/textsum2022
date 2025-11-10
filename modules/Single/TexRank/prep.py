def reset_punkt(text):
    if(text.startswith('\n')):
        text = text[1:]
    text = text.replace('\n', '. \\n \\n ')
    text = text.replace('. .', '.')
    # text = text.replace('. \\n \\n ', ' \\n \\n ')
    text = text.replace("'s", "\\'s")
    text = text[:-6]
    text = text + '|||| '
    return text

def prep(textst):
    for text in textst:
        text = reset_punkt(text)
    return " ".join([reset_punkt(tex) for tex in textst])
