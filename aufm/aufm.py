import bcrypt
from flask_login import LoginManager

from aufm import app, database, models
from aufm.models import User


app.config.from_object(__name__)

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


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


@app.before_first_request
def insert_test_user():
    test_user = User.query.filter(User.first_name == 'Test').first()
    if test_user is None:
        hashed = bcrypt.hashpw(b'super-secret-password',
                               bcrypt.gensalt())
        new_user = User(
                first_name='Test', last_name='User',
                email='tester@aufm.auburn.edu', password=hashed
        )
        database.db_session.add(new_user)
        database.db_session.commit()


@app.teardown_appcontext
def remove_db_connection(exception=None):
    database.db_session.remove()


if __name__ == '__main__':
    app.run()

