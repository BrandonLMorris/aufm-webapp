import os
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    TEMPLATES_AUTO_RELOAD=True
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return None

@app.route('/')
def index():
    return render_template('mat.html')