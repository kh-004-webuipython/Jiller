# -*- coding: utf-8 -*-

import os
import sqlite3

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pocker_db'
app.config['MONGO_URI'] = 'mongodb://admin:pockeradmin@ds139480.mlab.com' \
                          ':39480/pocker_db'

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


room_db = PyMongo(app)

socketio = SocketIO(app)


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/create_room/', methods=['POST'])
def create_room():
    issue_json = request.get_json(force='True')
    room = room_db.db.rooms
    q = room.find_one({'title': issue_json["title"]})
    # room.update_one(q, {'$set': issue_json}, upsert=True)
    if not q:
        for line in issue_json['team']:
            line['estimate'] = 0
        issue_json['issues'] = []
        #issue_json["link"] = request.url + str(issue_json["title"]) + "/"
        room.insert(issue_json)
    team = issue_json['team']
    return render_template('index.html')


@app.route('/add_issue/', methods=['POST'])
def add_issue():
    issue_json = request.get_json(force='True')
    room = room_db.db.rooms
    q = room.find_one({'title': issue_json["title"]})
    room.update_one(q, {'$set': issue_json['issue']}, upsert=True)


@socketio.on('my event')
def handle_my_custom_event(json):
    print('receive smth:' + str(json))
    emit('resp', json, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
