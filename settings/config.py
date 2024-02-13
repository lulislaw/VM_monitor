import os
from dotenv import load_dotenv, find_dotenv

dotenv_file = find_dotenv('settings/.env')
load_dotenv(dotenv_file)

class Config(object):
    def __init__(self):
        self.token = os.getenv('tgtoken')
        self.admin_pass = os.getenv('password')
