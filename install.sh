echo "About to install the flask app"
if [ `basename $(pwd)` != "aufm-webapp" ]
then
  echo "Please make sure you are in the aufm-webapp directory"
  exit
fi

if [ -d "venv" ]
then
  echo "Virtual environment created, not recreating"
else
  virtualenv venv
fi
source venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=`pwd`/aufm/aufm.py
export FLASK_DEBUG=True

echo "App successfully installed. Run 'flask run' to start the app"
