def newline_write(f, str):
    a = f
    a.write(b'\n')
    a.write(bytes(str, encoding='utf-8'))
    return a