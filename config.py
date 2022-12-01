from dotenv import dotenv_values

def config():
    return dotenv_values(".env")