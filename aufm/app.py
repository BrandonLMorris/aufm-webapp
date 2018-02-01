from flask import Flask, render_template

aufm = Flask(__name__)


@aufm.route('/')
def root(name='world'):
    return render_template('index.html', name=name)


@aufm.route('/shelby')
def shelby():
    return render_template('shelby-assets.html')

@aufm.route('/edit-H1456253')
def asset_edit():
    return render_template('edit-asset.html')



aufm.run()
