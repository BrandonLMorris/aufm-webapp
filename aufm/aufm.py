import os

from aufm import app, database

app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('AUFM_SETTINGS', silent=True)

database.init_db()

@app.teardown_appcontext
def remove_db_connection(exception=None):
    database.db_session.remove()

def connect_db():
    return None
