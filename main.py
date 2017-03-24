# -*- coding: utf-8 -*-
import os
import sqlite3

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask.ext.pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pocker_db'
app.config['MONGO_URI'] = 'mongodb://admin:pockeradmin@ds139480.mlab.com' \
                          ':39480/pocker_db'

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


room_db = PyMongo(app)


@app.route('/', methods=['POST'])
def main_page():
    if request.method == 'POST':
        issue_json = request.get_json(force='True')
        room = room_db.db.rooms
        q = room.find_one({'url': issue_json['url']})
        if q:
            output = 'its already in db'
            #room.insert(jsonify(issue_json))
        else:
            output = 'no row in db'
            room.insert(issue_json)
    return render_template('index.html', result=output)


@app.route('/link/')
@app.route('/link/<name>')
def main_page1(name=None):
    return render_template('index.html', link=name)


socketio = SocketIO(app)


@socketio.on('message')
def hendleMessage(msg):
    print ('Messega: ' + msg)
    send(msg, broadcast=True)



# @socketio.on('URI_link')
# def handle_json(json):
#     print('received json: ' + str(json))
#     send(json, json=True, namespace='URI_link')
#
#
# @socketio.on('my event')
# def handle_my_custom_event(json):
#     print('received json: ' + str(json))


if __name__ == '__main__':
    socketio.run(app)
