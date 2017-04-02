# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room, disconnect
from flask_pymongo import PyMongo
from random import choice


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pocker_db'
app.config['MONGO_URI'] = 'mongodb://db_admin:db_pass@ds145380.mlab.com' \
                          ':45380/pocker_db'

app.config.from_envvar('POKER_SETTINGS', silent=True)


room_db = PyMongo(app)
socketio = SocketIO(app)
state = dict()

def create_room_db(issue_json):
    room = room_db.db.rooms
    for issue in issue_json:
        issue['estimation'] = ''
    try:
        q = room.find_one({'project_id': int(issue_json["project_id"])})
    except Exception:
        print("Can't read database")
    else:
        # room.update_one(q, {'$set': issue_json}, upsert=True)
        if not q:
            issue_json['issues'] = []
            room.insert_one(issue_json)
    return True


def read_room_db(project_id):
    room = room_db.db.rooms
    id = int(project_id)
    try:
        q = room.find_one({'project_id': id}, {'issues': 1,
                                               'team': 1,
                                               '_id': 0})
        room_name = project_id
        state[room_name] = dict()
        issue_list = []
        for issue in q['issues']:
            issue_list.append({'id': issue['id'],
                               'title': issue['title'],
                               'description': issue['description'],
                               'estimation': issue['estimation']})
        user_list = []
        for teammate in q['team']:
            user_list.append({'id': teammate['id'],
                              'name': teammate['name'],
                              'role': '',
                              'current_vote': ''})
        state[room_name] = {
            "user_list": user_list,
            "issue_list": issue_list,
            "chat_log": []
        }
    except Exception:
        print ("Can't read database")
        disconnect()
    return True

# global room
#@app.route('/')
#def main_page():
#    # change 1 for dynamic id
#    return render_template('index.html')


# room page
@app.route('/room/<room_name>/')
def main_room_page(room_name=None):
    # get name of user from request
    name_list = ['egepsihora', 'gnom', 'irena']
    user_name = choice(name_list)
    return render_template('index.html', room_name=room_name,
                           user_name=user_name)


@app.route('/create_room/', methods=['POST'])
def create_room():
    issue_json = request.get_json(force='True')
    create_room_db(issue_json)
    room_name = int(issue_json['project_id'])
    return redirect('index.html', room_name=room_name)


@app.route('/add_issue/', methods=['POST'])
def add_issue():
    issue_json = request.get_json(force='True')
    room = room_db.db.rooms
    try:
        q = room.find_one({'project_id': int(issue_json["project_id"])})
    except Exception:
        print ("Can't read database")
    else:
        room.update_one(q, {'$set': {'issues': issue_json['issues']}}, upsert=True)
    return redirect('index.html')


@socketio.on('join')
def on_join(data):
    #username = data['username']
    room = int(data['room'])
    # if user in team:
    join_room(room)
    try:
        state[room]
    except:
        read_room_db(room)
    # drop user on bad DB request
    if (not state[room]):
        disconnect()
    emit('start_data', state[room])
    comment = dict()
    comment['id'] = len(state[room]['chat_log']) + 1
    comment['body'] = 'user' + ' has entered the room.'
    comment['user'] = 'Server'
    state[room]['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('leave')
def on_leave(data):
    # Need add event to clear room, when no one online
    #username = data['username']
    room = int(data['room'])
    leave_room(room)
    send('user has left the room.', room=room)


state = {
    500: {
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
                'role': 'developer',
                'current_vote': ''
            },
            {
                'id': 3,
                'name': 'john Smith',
                'role': 'developer',
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
'Employee was assigned to the issue. 2) ' +
                               'Employee that was assigned to the issue, ' +
                               'now is not assigned to the issue. 3) If ' +
                               'issue was changed in any way, it sends to ' +
                               'assigned issue employee. if NOTHING is ' +
                               'changed, do not send anything.',
                'estimation': '',
            },
            {
                'id': 2,
                'title': 'Profiatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qule access',
                'description': 'Make acceuia voluptas sit, aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qui ratione voluptatem sequi nesciunt, neque porro quisquam est, qui dolorem ipsum, quia dolor sit amet, consectetur, adipisci[ng] velit, sed quia non numquam [do] eius modi tempora inci[di]dunt, ut labore et dolore magnam aliquam quaerat voluptatem. Ut ee) and make it bigger',
                'estimation': 10,
            },
            {
                'id': 3,
                'title': 'titatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qule3',
                'description': 'datur aut odit aut fugit, sed quia consequuntur maatur aut odit aut fugit, sed quia consequuntur magni dolores eos, quatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qugni dolores eos, qu3',
                'estimation':'',
            },
            {
                'id': 4,
                'title': 'title4',
                'description': 'descripatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qution4',
                'estimation': '',
            },
            {
                'id': 5,
                'title': 'title5',
                'description': 'deatur aut odit aut fugit, sed quia consequuntur magni dolores eos, quion5',
                'estimation': '',
            },
            {
                'id': 6,
                'title': 'title6',
                'description': 'descripatur aut odit aut fugit, sed quia consequuntur magni dolores eos, qution6',
                'estimation': '',
            },

        ],
        'chat_log': []

    },
}



@socketio.on('add_comment')
def handle_add_comment(data):
    room = int(data['room'])
    comment = dict()
    comment['id'] = len(state[room]['chat_log']) + 1
    comment['body'] = data['body']
    comment['user'] = data['user']
    state[room]['chat_log'].append(comment)
    emit('add_new_comment', comment, room=room)


@socketio.on('make_vote')
def handle_vote(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        if user['id'] == int(data['user_id']):
            user['current_vote'] = data['card']
    emit('make_vote', users, room=room)


@socketio.on('accept_estimation')
def handle_accept(data):
    room = int(data['room'])
    issues = state[room]['issue_list']
    # MAKE REST TO DJANGO AND ON success:
        # DELETE ISSUE IN OUR DB
    for issue in issues:
        if issue['id'] == int(data['issue_id']):
            issue['estimation'] = int(data['estimation'])

    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''

    new_users = state[room]['user_list']
    new_issues = state[room]['issue_list']
    emit('issue_was_estimated', {'users': new_users, 'issues': new_issues},
         room=room)


@socketio.on('reset_estimation')
def handle_reset_estimation(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('reset_estimation', users, room=room)


@socketio.on('skip_estimation')
def handle_skip_estimation(data):
    room = int(data['room'])
    users = state[room]['user_list']
    for user in users:
        user['current_vote'] = ''
    emit('skip_estimation', users, room=room)


if __name__ == '__main__':
    socketio.run(app)