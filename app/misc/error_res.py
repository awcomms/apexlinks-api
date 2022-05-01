from flask import abort

def error_res(msg='An error occured', code=400):
    abort