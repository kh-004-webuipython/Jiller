//const USER = 'phobos';
//const USER_ID = 1;
const USER_ID = Number(prompt());
//const ROOM = document.querySelector('body').dataset['room'];
let ROOM = '';
const USER = USER_ID;
let startUserList = [];
let startIssueList = [];
let chatLog = [];
function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


if (location.pathname.substr(1,4) === 'room') {
    ROOM = location.pathname.replace(/^\/room\/|\/$/g, '')
}

let socket = io.connect('http://127.0.0.1:5000');
socket.on('connect', () => socket.emit('join',{'room': ROOM}));
console.log(ROOM);

socket.on('start_data', (data) => {
    startUserList = data.user_list;
    startIssueList = data.issue_list;
    chatLog = data.chat_log;
    console.log(startUserList);
    let startIssue = 0;
let startFlip = (() => {
	for (var i = 0; i < startUserList.length; i++) {
		if (startUserList[i].current_vote === '') {
			return false;
		}
	}
	return true;
}) ();
console.log(startFlip, startUserList);
    //*********************************
    // поднять на уровень выше юзелист и флип
    // Определиться с дизайном естимейшен аксепт
    // написать функцию резет воута, которая будет использоваться при повторном голосвании и успешном сохранении сервером естимешена
    // пересадить большую часть интерфейса на таблицы
    // поставить вебсокет на новые колеса: gevent + gunicorn + Nginx
    // настроить фласк в облаке

    // добавить авторизацию
    // добавить румы
    // прикрутить ДБ в которую будет записываться рума и потом в нее будут добавляться/удаляться ишью
    // добавить очистку "состояния румы", если из нее все вышли


let cardList = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, '?', 'coffee'];
let status = {
    'flip': true,
};


class PokerBox extends React.Component {
    render() {
        return (
            <div>
                <h3>Jiller planning poker service
                    <div className="profile">{USER}</div>
                </h3>
                <IssueBox />
                <UserBox />
                <CommentBox />
            </div>
        );
    }
}


class UserBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'userList': startUserList,
            'flip': startFlip,
        }
    }
    componentWillMount() {
        this._changeUserStatus();
    }
    render() {
        const users = this._getUsers();
        /*<h4 className="user-count">{ userList.filter(x => x.online).length }
                    user online</h4>*/

        return (
            <div className="user-box col-md-3 col-sm-2 pull-right">
                <div className="user-list info info-striped">
                    <div className="info-row">
                        <div className="col-md-8 info-name">Nickname</div>
                        <div className="col-md-4 info-value">Vote</div>
                    </div>
                    { users }
                </div>
            </div> );
    }

    _getUsers() {
        return (this.state.userList.map(user => {
                return <User name={user.name} vote={user.current_vote}
                             key={user.id} flip={this.state.flip} />
            })
        )
    };

    _changeUserStatus() {
        socket.on('make_vote', newUserList => {
            this.setState({userList: newUserList});
            console.log('make_vote');
            if (newUserList.filter(x => x.current_vote).length == newUserList.length) {
                this.setState({'flip': true});
                console.log('set_true_flip');
            } else {
                this.setState({'flip': false});
                console.log('set_false_flip');
            }
        });
    }
}

class User extends React.Component {
    render() {
        let ok = <span className="glyphicon glyphicon-ok" aria-hidden="true"></span>;
        let coffee = <i className="fa fa-coffee fa-2x" aria-hidden="true"></i>;
        return (
            <div className="info-row">
                <div className="col-md-8 info-name">{this.props.name}</div>
                <div className="col-md-4 info-value">{this.props.vote === 'coffee' ? coffee: this.props.flip ? this.props.vote: this.props.vote? ok: ''}</div>
            </div> );
    }
}


class IssueBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'currentIssue': startIssueList.filter(x=>x.estimation === '')[0],
            'currentSlide': 'active',
            'issueList': startIssueList,
            'vote': startUserList.find(x=>x.id=USER_ID)['current_vote'],
            'flip': startFlip,
        };
        this._userList = startUserList;

    }

    componentWillMount() {
        this._changeUserStatus();
    }

    render() {
        if (this.state.currentIssue && this.state.currentSlide == 'active') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped overflow">
                        <div className="info-row ">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.currentIssue.title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value overflow">{this.state.currentIssue.description}</div>
                        </div>
                    </div>
                    <CardBox vote={this.state.vote} flip={this.state.flip} saveVote={this._setVote.bind(this)} />
                    <IssueNavbar activeSlide={this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                </div>
            );
        }
        if (this.state.currentIssue && this.state.currentSlide == 'accept') {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped overflow">
                        <div className="info-row">
                            <div className="info-name">Issue on estimation:</div>
                            <div className="info-value">{this.state.currentIssue.title}</div>
                        </div>
                        <div className="info-row">
                            <div className="info-name">Description:</div>
                            <div className="info-value">{this.state.currentIssue.description}</div>
                        </div>
                    </div>
                    <div>СТАТИСТИКА</div>

                    <div>
                        <p>Estimation manager</p>
                        <button className={this._checkBtn('accept')} onClick={this._estimationAccept.bind(this)}>Accept issue estimation</button>
                        <button className="btn btn-default" onClick={this._estimationReset.bind(this)}>Reset votes</button>
                        <button className="btn btn-default" onClick={this._estimationSkip.bind(this, 'skip')}>Skip issue</button>
                    </div>
                    <IssueNavbar activeSlide = {this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                </div>
            );

        }


        // аксепт: сенд дату + редирект вкладки
        // резет: сенд резет + редирект вкладки
        // скип: сенд резет + редирект
        if (this.state.currentSlide == 'completed') {
        //current issue slide
            return (
                <div className="main-block col-md-9 overflow">
                {
                this.state.issueList.filter(x=>x['estimation']).map((issue, index) => {
                return (<div className="info info-striped" key={index}>
                    <div className="info-row flex">
                        <div className="info-name col-md-1">{index+1}</div>
                        <div className="info-value col-md-2">{issue.title}</div>
                        <div className="info-value col-md-8">{issue.description}</div>
                        <div className="info-value col-md-1">{issue.estimation}</div>
                    </div>
                    </div>)
                })
                }
                <IssueNavbar activeSlide={this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
             </div>)
        }
        if (this.state.currentSlide == 'all') {
        //current issue slide
            return (<div className="main-block col-md-9 overflow">
                <div className="info info-striped">
                {
                this.state.issueList.map((issue, index) => {
                return (<div className="info-row flex" key={index}>
                    <div className="info-name col-md-1">{index+1}</div>
                    <div className="info-value col-md-2">{issue.title}</div>
                    <div className="info-value col-md-8">{issue.description}</div>
                    <div className="info-value col-md-1">{issue.estimation}</div>
                    </div>)
                })
                }
                </div>
                <IssueNavbar activeSlide={this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
            </div>);
        } else {
        //current issue slide
            return (
                <div className="main-block col-md-9">
                    <div className="info info-striped overflow">
                        <p className="text-center">No Issues to estimate</p>
                    </div>
                    <IssueNavbar activeSlide={this.state.currentSlide} setSlide={this._setSlide.bind(this)} />
                </div>
            );
        }
    }

    _setSlide(slide) {
        this.setState({'currentSlide': slide});
        console.log('set_slide');
    }

    _setVote(vote) {
        this.setState({vote});
        console.log('set_vote');
    }

    _checkBtn(btn) {
        if (btn == 'accept') {
            return this.state.flip ? "btn btn-success" : "btn btn-danger";
        }
    }

    _estimationAccept() {
        if (this.state.flip) {
            for(let i = 1; i < this._userList.length; i++) {
	            if (this._userList[i - 1].current_vote !== this._userList[i].current_vote) {
	                console.log(this._userList);
		            alert('Sorry, you can not set estimation on issue when teammates have made different votes!');
		            return
	            }
            }

            if (isNumber(this._userList[0].current_vote)) {
                console.log('vote');
                let issue = this.state.currentIssue;
                let vote = this._userList[0].current_vote
                socket.emit('accept_estimation', {'issue_id': issue.id, 'estimation': vote});
            }
        } else {
            alert('Sorry, you can not set estimation on issue before all teammates make vote!')
        }
    }

    _estimationReset() {
        socket.emit('reset_estimation');
    }

    _estimationSkip() {
        socket.emit('skip_estimation');
    }

    _changeUserStatus() {
        socket.on('make_vote', newUserList => {
            this._userList = newUserList;
            console.log('make_vote');
            if (newUserList.filter(x => x.current_vote).length == newUserList.length) {
                this.setState({'flip': true});
                this.setState({'currentSlide': 'accept'});
                console.log('set_true_flip');
            } /*else {
                this.setState({'flip': false});
                console.log('set_false_flip');
            }*/
        });


        socket.on('issue_was_estimated', (data)=> {
            let nextSecIssue = () => this.state.issueList.filter(issue => issue.estimation === '')[1];
            this._userList = data.users;
            this.setState({'flip': false, 'currentIssue': nextSecIssue(), 'issueList': data.issues});
            console.log(this.state.flip, this._userList, this.state.currentIssue);
        });


        socket.on('skip_estimation', (users)=> {
            let nextSecIssue = () => this.state.issueList.filter(issue => issue.estimation === '')[1];
            this._userList = users;
            this.setState({'flip': false, 'currentIssue': nextSecIssue()});
            console.log(this.state.flip, this._userList);
        });

        socket.on('reset_estimation', (users)=> {
            this._userList = users;
            this.setState({'flip': false});
            console.log(this.state.flip, this._userList);

        });
    }

    //TODO: применить функцию
    _nextIssue(param) {
        let noEstimatedIssue = this.state.issueList.filter(issue => issue.estimation === '');
        if(param === 'start') {
            return noEstimatedIssue[0]
        }

        if (param === 'save') {
            return noEstimatedIssue[1]
        }
        if (param === 'skip') {
            if (noEstimatedIssue.length > 1) {
                return noEstimatedIssue[1]
            } else {
                return noEstimatedIssue[0]
            }
        }
    }

}


class CardBox extends React.Component {
    render() {
        let coffee = <i className="fa fa-coffee" aria-hidden="true"></i>;
        return (<div>
            {
                cardList.map((card, index) => {
                    return <div className={this.props.vote === String(card) ? 'chosen card': 'card'}
                                data-card={card} key={index} onClick={this._sendEstimation.bind(this)}>
                        <div className="card-top-data">{card}</div>
                        <div className="card-center-data">{card =='coffee'? coffee: card}</div>
                        <div className="card-bottom-data">{card}</div>
                    </div>
                })
            }
        </div>)
    }

    _sendEstimation(event) {
        if (!this.props.flip) {
	        let card = event.currentTarget.dataset['card'];
	        this.props.saveVote(card);
	        socket.emit('make_vote', {'user_id': USER_ID, 'card': card});
        }
    }

}


class IssueNavbar extends React.Component {
    render() {
        return (
            <div className="issue-bar">
                <button className={this._checkActiveBtn('active')} onClick = {this.props.setSlide.bind(this, 'active')}>Active issue</button>
                <button className={this._checkActiveBtn('accept')} onClick = {this.props.setSlide.bind(this, 'accept')}>Accept vote</button>
                <button className={this._checkActiveBtn('completed')} onClick = {this.props.setSlide.bind(this, 'completed')}>Completed issue</button>
                <button className={this._checkActiveBtn('all')} onClick = {this.props.setSlide.bind(this, 'all')}>All issue list</button>
            </div>
        )
    }
     _checkActiveBtn(slide) {
        return (slide == this.props.activeSlide) ? "btn btn-info" : "btn";
    }
}


class CommentBox extends React.Component {
    constructor() {
        super();
        this.state = {
            'comments': chatLog
        };
    };
    componentWillMount() {
        this._addNewComment();
    }

    render() {
        let comments = this._getComments();
        return (
            <div className="col-md-12 col-sm-10 chat-box">
                <CommentForm addComment={this._sendComment.bind(this)}/>
                <div className="comment-box"> { comments } </div>
            </div>
        );
    }

    _addNewComment() {
        socket.on('add_new_comment', newComment => {
            console.log('add_new_comment');
            this.setState({comments: this.state.comments.concat([newComment])});
        });
    }

    _sendComment(user, body) {
        const comment = {
            user,
            body
        };
        socket.emit('add_comment', comment);
    }

    _getComments() {
        return this.state.comments.map(comment => {
            return (
                <Comment
                    user={comment.user}
                    body={comment.body}
                    key={comment.id} />
            );
        });
    };
}


class CommentForm extends React.Component {
    render() {
        let sendIcon = <i className="glyphicon glyphicon-share-alt"></i>;
        return (
            <form onSubmit={this._handleSubmit.bind(this)}>
                <div className="input-group">
                    <input className="form-control form-group" placeholder="Type your comment there" ref={(input) => this._body = input} />
                        <div className="input-group-btn">
                            <button className="btn btn-info" type="submit">Post comment {sendIcon} </button>
                        </div>
                </div>
            </form>
        );
    }

    _handleSubmit(event) {
        event.preventDefault();
        let body = this._body.value;
        if (body) {
            this.props.addComment(USER, body);
        this._body.value = '';
        }

    }
}


class Comment extends React.Component {
    render() {
        return (
            <div className="comment">
                <p>{this.props.user}</p>
                <p>{this.props.body}</p>
            </div> );
    }
}


ReactDOM.render(
    <PokerBox />, document.getElementById('poker-app')
);

});