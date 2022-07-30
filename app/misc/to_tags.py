def to_tags(value, tags):
    res = []
    words = value.split(' ')  # TODO trim double spaces
    phrases = []
    length = len(words)
    for idx, word in enumerate(words):
        phrases.append(word)
        for i in range(idx+1, length):
            word = word + ' ' + words[i]
            phrases.append(word)
    for phrase in phrases:
        if phrase not in [t['value'] for t in tags]:
            res.append({'value': phrase})
    return res
