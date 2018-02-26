# from .aufm import app
from flask import Flask

app = Flask(__name__)

import aufm.views
