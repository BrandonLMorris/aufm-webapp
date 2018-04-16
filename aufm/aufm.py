import bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from aufm import app, database, models
from aufm.models import User


app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME='do.not.reply.aufm@gmail.com',
    MAIL_PASSWORD='group2-aufm',
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True
))
app.config.from_envvar('AUFM_SETTINGS', silent=True)

database.init_db()

login_manager = LoginManager()
login_manager.init_app(app)

mail = Mail(app)
app.mail = mail

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

