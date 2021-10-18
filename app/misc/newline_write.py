def newline_write(f, str):
    f.write(b'\n')
    f.write(bytes(str, encoding='utf-8'))
    return f