python main.py

or

FLASK_APP=main.py flask run

for deploy:
gunicorn -k gevent -b 0.0.0.1:5000 -w 1 main:app