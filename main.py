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


# room page
@app.route('/room/<room_name>/')
def main_room_page(room_name=None):
    return render_template('index.html', room_name=room_name)


# add sockets in our app
socketio = SocketIO(app)


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


state = {
    'room_500': {
        'user_list': [
            {
                'id': 1,
                'name': 'phobos',
                'role': 'developer',
                'current_vote': ''
            },
            {
                'id': 2,
                'name': 'scrum_name',
                'role': 'scrum',
                'current_vote': ''
            },

            {
                'id': 3,
                'name': 'PO',
                'role': 'PO',
                'current_vote': ''
            },

        ],
        'issue_list': [
            {
                'id': 1,
                'title': 'Fix Email Notification(Issues change)',
                'description': 'Email notification has to work for: 1) ' +
                               'Employee was assigned to the issue. 2) ' +
                               'Employee that was assigned to the issue, ' +
                               'now is not assigned to the issue. 3) If ' +
                               'issue was changed in any way, it sends to ' +
                               'assigned issue employee. if NOTHING is ' +
                               'changed, do not send anything.',
                'estimation': 10,
            },
            {
                'id': 2,
                'title': 'Profile access',
                'description': 'Make access to user profile via dropdown(as it was before) and make it bigger',
                'estimation':'',
            },
            {
                'id': 3,
                'title': 'title3',
                'description': 'description3',
                'estimation':'',
            },

        ],
        'chat_log': [
            {
                'id': 1,
                'user': 'phobos',
                'body': ' xxxxxxxxxxxxx'
            },
            {
                'id': 2,
                'user': 'scrum',
                'body': 'zzzzzzzz'
            },
        ]

    },
}


@socketio.on('connect')
def handle_connect():
    emit('start_data', state['room_500'])
    #Add event to clear room, when no one online


@socketio.on('add_comment')
def handle_add_comment(comment_obj):
    comment_obj['id'] = len(state['room_500']['chat_log']) + 1
    state['room_500']['chat_log'].append(comment_obj)
    emit('add_new_comment', comment_obj, broadcast=True)


@socketio.on('make_vote')
def handle_vote(vote_obj):
    users = state['room_500']['user_list']
    for user in users:
        if user['id'] == vote_obj['user_id']:
            user['current_vote'] = vote_obj['card']
    emit('make_vote', users, broadcast=True)


@socketio.on('accept_estimation')
def handle_accept(accept_obj):
    issues = state['room_500']['issue_list']
    # MAKE REST TO DJANGO AND ON success:
        # DELETE ISSUE IN OUR DB
    for issue in issues:
        if issue['id'] == accept_obj['id']:
            issue['estimation'] = accept_obj['estimation']
    [x.__setattr__('current_vote', '') for x in state['room_500']['user_list']]
    """for user in users:
        user['current_vote'] = ''
        """
    emit('reset_vote_and_update_Issue', issue, broadcast=True)


"""
@socketio.on('chat_event')
def handle_json(json):
    print('received json: ' + str(json))
    room = state[json['room']]
    if room['chat']:
       room['chat'].push(json['message'])
    send(json, json=True, namespace='chat_event', broadcast=True)


@socketio.on('message')
def hendleMessage(msg):
    print ('Messega: ' + msg)
    send(msg, broadcast=True)


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

"""

if __name__ == '__main__':
    socketio.run(app)
