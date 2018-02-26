import os

from aufm import app, database, render_template

app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    TEMPLATES_AUTO_RELOAD=True
))
app.config.from_envvar('AUFM_SETTINGS', silent=True)

database.init_db()

@app.teardown_appcontext
def remove_db_connection(exception=None):
    database.db_session.remove()

def connect_db():
    return None

@app.route('/')
def index():
    return render_template('mat.html')