from flask_security import Security, SQLAlchemySessionUserDatastore

from aufm import app, database, models


app.config.from_object(__name__)

app.logger.setLevel(1)
print(app.logger)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    SECURITY_PASSWORD_SALT='super-super-salty'
))
app.config.from_envvar('AUFM_SETTINGS', silent=True)

database.init_db()


user_datastore = SQLAlchemySessionUserDatastore(database.db_session, models.User,
                                                models.Role)
security = Security(app, user_datastore)

@app.teardown_appcontext
def remove_db_connection(exception=None):
    database.db_session.remove()


# @app.before_first_request
# def create_user():
#     user_datastore.create_user(email='tester@aufm.auburn.edu',
#                                password='super-secret-password')
#     database.db_session.commit()

