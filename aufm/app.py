from flask import Flask

aufm = Flask(__name__)


@aufm.route('/')
def root():
    return 'Hello, world!'


aufm.run()
