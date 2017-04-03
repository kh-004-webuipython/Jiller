/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "build/";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports) {

	//const USER_ID = Number(prompt());
	'use strict';

	var _createClass = (function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ('value' in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; })();

	var _get = function get(_x, _x2, _x3) { var _again = true; _function: while (_again) { var object = _x, property = _x2, receiver = _x3; _again = false; if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { _x = parent; _x2 = property; _x3 = receiver; _again = true; desc = parent = undefined; continue _function; } } else if ('value' in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } } };

	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } }

	function _inherits(subClass, superClass) { if (typeof superClass !== 'function' && superClass !== null) { throw new TypeError('Super expression must either be null or a function, not ' + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

	var USER_ID = Number(document.getElementById('poker-app').dataset['id']);
	var USER = document.getElementById('poker-app').dataset['name'];
    var ROOM = Number(document.querySelector('body').dataset['room']);
	//var ROOM = '';
	var cardList = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, '?', 'coffee'];
	var startUserList = [];
	var startIssueList = [];
	var chatLog = [];
	function isNumber(n) {
	    return !isNaN(parseFloat(n)) && isFinite(n);
	}

	function progressBar(x) {
	    if (!isNumber(x)) {
	        return 0;
	    }
	    return 56 * cardList.indexOf(Number(x));
	}

	var socket = io.connect('http://46.101.197.108:5000');
	socket.on('connect', function () {
	    return socket.emit('join', { 'room': ROOM , 'user_id': USER_ID,
	    'name': USER});
	});

	socket.on('start_data', function (data) {
	    startUserList = data.user_list;
	    startIssueList = data.issue_list;
	    chatLog = data.chat_log;
	    var startFlip = (function () {
	        for (var i = 0; i < startUserList.length; i++) {
	            if (startUserList[i].current_vote === '') {
	                return false;
	            }
	        }
	        return true;
	    })();

	    var PokerBox = (function (_React$Component) {
	        _inherits(PokerBox, _React$Component);

	        function PokerBox() {
	            _classCallCheck(this, PokerBox);

	            _get(Object.getPrototypeOf(PokerBox.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(PokerBox, [{
	            key: 'render',
	            value: function render() {
	                return React.createElement(
	                    'div',
	                    null,
	                    React.createElement(
	                        'h3',
	                        null,
	                        'Jiller planning poker service',
	                        React.createElement(
	                            'div',
	                            { className: 'profile' },
	                            USER
	                        )
	                    ),
	                    React.createElement(
	                        'div',
	                        { className: 'mark-borders' },
	                        React.createElement(
	                            'div',
	                            { className: 'col-md-9 main-block' },
	                            React.createElement(IssueBox, null)
	                        ),
	                        React.createElement(UserBox, null)
	                    ),
	                    React.createElement(CommentBox, null)
	                );
	            }
	        }]);

	        return PokerBox;
	    })(React.Component);

	    var UserBox = (function (_React$Component2) {
	        _inherits(UserBox, _React$Component2);

	        function UserBox() {
	            _classCallCheck(this, UserBox);

	            _get(Object.getPrototypeOf(UserBox.prototype), 'constructor', this).call(this);
	            this.state = {
	                'userList': startUserList,
	                'flip': startFlip
	            };
	        }

	        _createClass(UserBox, [{
	            key: 'componentWillMount',
	            value: function componentWillMount() {
	                this._changeUserStatus();
	            }
	        }, {
	            key: 'render',
	            value: function render() {
	                var users = this._getUsers();
	                /*<h4 className="user-count">{ userList.filter(x => x.online).length }
	                user online</h4>*/

	                return React.createElement(
	                    'div',
	                    { className: 'user-box col-md-3' },
	                    React.createElement(
	                        'div',
	                        { className: 'user-list info info-striped' },
	                        React.createElement(
	                            'div',
	                            { className: 'info-row' },
	                            React.createElement(
	                                'div',
	                                { className: 'col-md-8 info-name' },
	                                'Teammates'
	                            ),
	                            React.createElement(
	                                'div',
	                                { className: 'col-md-4 info-value' },
	                                'Vote'
	                            )
	                        ),
	                        users
	                    )
	                );
	            }
	        }, {
	            key: '_getUsers',
	            value: function _getUsers() {
	                var _this = this;

	                return this.state.userList.map(function (user) {
	                    return React.createElement(User, { name: user.name, vote: user.current_vote,
	                        key: user.id, flip: _this.state.flip });
	                });
	            }
	        }, {
	            key: '_changeUserStatus',
	            value: function _changeUserStatus() {
	                var _this2 = this;

	                socket.on('make_vote', function (newUserList) {
	                    _this2.setState({ userList: newUserList });
	                    if (newUserList.filter(function (x) {
	                        return x.current_vote;
	                    }).length == newUserList.length) {
	                        _this2.setState({ 'flip': true });
	                    } else {
	                        _this2.setState({ 'flip': false });
	                    }
	                });

	                socket.on('issue_was_estimated', function (data) {
	                    _this2.setState({ 'flip': false, userList: data.users });
	                });

	                socket.on('skip_estimation', function (users) {
	                    _this2._userList = users;
	                    _this2.setState({ 'flip': false, userList: users });
	                });

	                socket.on('reset_estimation', function (users) {
	                    _this2._userList = users;
	                    _this2.setState({ 'flip': false, userList: users });
	                });
	            }
	        }]);

	        return UserBox;
	    })(React.Component);

	    var User = (function (_React$Component3) {
	        _inherits(User, _React$Component3);

	        function User() {
	            _classCallCheck(this, User);

	            _get(Object.getPrototypeOf(User.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(User, [{
	            key: 'render',
	            value: function render() {
	                var ok = React.createElement('span', { className: 'glyphicon glyphicon-ok', 'aria-hidden': 'true' });
	                var coffee = React.createElement('i', { className: 'fa fa-coffee fa-2x', 'aria-hidden': 'true' });
	                return React.createElement(
	                    'div',
	                    { className: 'info-row' },
	                    React.createElement(
	                        'div',
	                        { className: 'col-md-8 info-name' },
	                        this.props.name
	                    ),
	                    React.createElement(
	                        'div',
	                        { className: 'col-md-4 info-value' },
	                        this.props.vote === 'coffee' ? coffee : this.props.flip ? this.props.vote : this.props.vote ? ok : ''
	                    )
	                );
	            }
	        }]);

	        return User;
	    })(React.Component);

	    var IssueBox = (function (_React$Component4) {
	        _inherits(IssueBox, _React$Component4);

	        function IssueBox() {
	            _classCallCheck(this, IssueBox);

	            _get(Object.getPrototypeOf(IssueBox.prototype), 'constructor', this).call(this);
	            this.state = {
	                'currentIssue': startIssueList.filter(function (x) {
	                    return x.estimation === '';
	                })[0],
	                'currentSlide': 'active',
	                'issueList': startIssueList,
	                'vote': startUserList.find(function (x) {
	                    return x.id == USER_ID;
	                })['current_vote'],
	                'flip': startFlip
	            };
	            this._userList = startUserList;
	        }

	        _createClass(IssueBox, [{
	            key: 'componentWillMount',
	            value: function componentWillMount() {
	                this._changeUserStatus();
	            }
	        }, {
	            key: 'render',
	            value: function render() {
	                if (this.state.currentIssue && this.state.currentSlide == 'active') {
	                    //current issue slide
	                    return React.createElement(
	                        'div',
	                        { className: '' },
	                        React.createElement(
	                            'div',
	                            { className: 'main-issue-overflow' },
	                            React.createElement(
	                                'div',
	                                { className: 'info info-striped' },
	                                React.createElement(
	                                    'div',
	                                    { className: 'info-row' },
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-name' },
	                                        'Issue on estimation:'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value' },
	                                        this.state.currentIssue.title
	                                    )
	                                ),
	                                React.createElement(
	                                    'div',
	                                    { className: 'info-row' },
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-name' },
	                                        'Description:'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value overflow' },
	                                        this.state.currentIssue.description
	                                    )
	                                )
	                            )
	                        ),
	                        React.createElement(CardBox, { vote: this.state.vote, flip: this.state.flip, saveVote: this._setVote.bind(this) }),
	                        React.createElement(IssueNavbar, { activeSlide: this.state.currentSlide, setSlide: this._setSlide.bind(this) })
	                    );
	                }

	                if (this.state.currentIssue && this.state.currentSlide == 'accept') {
	                    //current issue slide
	                    var diagram = this._getDiagram();
	                    return React.createElement(
	                        'div',
	                        { className: '' },
	                        React.createElement(
	                            'div',
	                            { id: 'issue-container' },
	                            React.createElement(
	                                'div',
	                                { className: 'main-issue-overflow' },
	                                React.createElement(
	                                    'div',
	                                    { className: 'info info-striped' },
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-row' },
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-name' },
	                                            'Issue on estimation:'
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value' },
	                                            this.state.currentIssue.title
	                                        )
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-row' },
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-name' },
	                                            'Description:'
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value' },
	                                            this.state.currentIssue.description
	                                        )
	                                    )
	                                )
	                            ),
	                            React.createElement(
	                                'div',
	                                null,
	                                React.createElement(
	                                    'div',
	                                    { className: 'acceptManager' },
	                                    React.createElement(
	                                        'button',
	                                        { className: this._checkBtn('accept'), onClick: this._estimationAccept.bind(this) },
	                                        'Accept issue estimation'
	                                    ),
	                                    React.createElement(
	                                        'button',
	                                        { className: 'btn btn-default', onClick: this._estimationReset.bind(this) },
	                                        'Reset votes'
	                                    ),
	                                    React.createElement(
	                                        'button',
	                                        { className: 'btn btn-default', onClick: this._estimationSkip.bind(this, 'skip') },
	                                        'Skip issue'
	                                    )
	                                ),
	                                this.state.flip ? diagram : React.createElement(
	                                    'p',
	                                    null,
	                                    'Diagram can be shown only after all teammates have voted'
	                                )
	                            )
	                        ),
	                        React.createElement(IssueNavbar, { activeSlide: this.state.currentSlide, setSlide: this._setSlide.bind(this) })
	                    );
	                }

	                if (this.state.currentSlide == 'completed') {
	                    //current issue slide
	                    return React.createElement(
	                        'div',
	                        { className: '' },
	                        React.createElement(
	                            'div',
	                            { id: 'issue-container', className: 'overflow' },
	                            React.createElement(
	                                'div',
	                                { className: 'info info-striped' },
	                                React.createElement(
	                                    'div',
	                                    { className: 'info-row flex' },
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-name col-sm-1 col-md-1' },
	                                        'id'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-2 col-md-2' },
	                                        'Title'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-8 col-md-8' },
	                                        'Description'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-1 col-md-1' },
	                                        'Estim.'
	                                    )
	                                ),
	                                this.state.issueList.filter(function (x) {
	                                    return x['estimation'];
	                                }).map(function (issue, index) {
	                                    return React.createElement(
	                                        'div',
	                                        { className: 'info-row flex', key: index },
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-name col-sm-1 col-md-1' },
	                                            issue.id
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-2 col-md-2' },
	                                            issue.title
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-8 col-md-8' },
	                                            issue.description
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-1 col-md-1' },
	                                            issue.estimation
	                                        )
	                                    );
	                                })
	                            )
	                        ),
	                        React.createElement(IssueNavbar, { activeSlide: this.state.currentSlide, setSlide: this._setSlide.bind(this) })
	                    );
	                }

	                if (this.state.currentSlide == 'all') {
	                    //current issue slide
	                    return React.createElement(
	                        'div',
	                        { className: '' },
	                        React.createElement(
	                            'div',
	                            { id: 'issue-container', className: 'overflow' },
	                            React.createElement(
	                                'div',
	                                { className: 'info info-striped' },
	                                React.createElement(
	                                    'div',
	                                    { className: 'info-row flex' },
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-name col-sm-1 col-md-1' },
	                                        'id'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-2 col-md-2' },
	                                        'Title'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-8 col-md-8' },
	                                        'Description'
	                                    ),
	                                    React.createElement(
	                                        'div',
	                                        { className: 'info-value col-sm-1 col-md-1' },
	                                        'Estim.'
	                                    )
	                                ),
	                                this.state.issueList.map(function (issue, index) {
	                                    return React.createElement(
	                                        'div',
	                                        { className: 'info-row flex', key: index },
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-name col-sm-1 col-md-1' },
	                                            issue.id
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-2 col-md-2' },
	                                            issue.title
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-8 col-md-8' },
	                                            issue.description
	                                        ),
	                                        React.createElement(
	                                            'div',
	                                            { className: 'info-value col-sm-1 col-md-1' },
	                                            issue.estimation
	                                        )
	                                    );
	                                })
	                            )
	                        ),
	                        React.createElement(IssueNavbar, { activeSlide: this.state.currentSlide, setSlide: this._setSlide.bind(this) })
	                    );
	                } else {
	                    //current issue slide
	                    return React.createElement(
	                        'div',
	                        { className: '' },
	                        React.createElement(
	                            'div',
	                            { id: 'issue-container', className: 'info info-striped  overflow' },
	                            React.createElement(
	                                'div',
	                                { className: 'info-row flex' },
	                                React.createElement(
	                                    'p',
	                                    { className: 'block-center' },
	                                    'No Issues to estimate'
	                                )
	                            )
	                        ),
	                        React.createElement(IssueNavbar, { activeSlide: this.state.currentSlide, setSlide: this._setSlide.bind(this) })
	                    );
	                }
	            }
	        }, {
	            key: '_setSlide',
	            value: function _setSlide(slide) {
	                this.setState({ 'currentSlide': slide });
	            }
	        }, {
	            key: '_setVote',
	            value: function _setVote(vote) {
	                this.setState({ vote: vote });
	            }
	        }, {
	            key: '_checkBtn',
	            value: function _checkBtn(btn) {
	                if (btn == 'accept') {
	                    var sameVOte = true;
	                    var num = isNumber(this._userList[0].current_vote);
	                    for (var i = 1; i < this._userList.length; i++) {
	                        if (this._userList[i - 1].current_vote !== this._userList[i].current_vote) {
	                            sameVOte = false;
	                        }
	                    }
	                    return this.state.flip && sameVOte && num ? "btn btn-success" : "btn btn-danger";
	                }
	            }
	        }, {
	            key: '_estimationAccept',
	            value: function _estimationAccept() {
	                if (this.state.flip) {
	                    for (var i = 1; i < this._userList.length; i++) {
	                        if (this._userList[i - 1].current_vote !== this._userList[i].current_vote) {
	                            alert('Sorry, you can not set estimation on issue when teammates have made different votes!');
	                            return;
	                        }
	                    }

	                    if (isNumber(this._userList[0].current_vote)) {
	                        var issue = this.state.currentIssue;
	                        var vote = this._userList[0].current_vote;
	                        socket.emit('accept_estimation', { 'issue_id': issue.id, 'estimation': vote, 'room': ROOM });
	                    }
	                } else {
	                    alert('Sorry, you can not set estimation on issue before all teammates make vote!');
	                }
	            }
	        }, {
	            key: '_estimationReset',
	            value: function _estimationReset() {
	                socket.emit('reset_estimation', { 'room': ROOM });
	            }
	        }, {
	            key: '_estimationSkip',
	            value: function _estimationSkip() {
	                socket.emit('skip_estimation', { 'room': ROOM });
	            }
	        }, {
	            key: '_changeUserStatus',
	            value: function _changeUserStatus() {
	                var _this3 = this;

	                socket.on('make_vote', function (newUserList) {
	                    _this3._userList = newUserList;
	                    if (newUserList.filter(function (x) {
	                        return x.current_vote;
	                    }).length == newUserList.length) {
	                        _this3.setState({ 'flip': true });
	                        _this3.setState({ 'currentSlide': 'accept' });
	                    } else {
	                        _this3.setState({ 'flip': false });
	                    }
	                });

	                socket.on('issue_was_estimated', function (data) {
	                    _this3._userList = data.users;
	                    _this3.setState({ 'flip': false, 'currentSlide': 'active', 'currentIssue': _this3._next('save'), 'issueList': data.issues, 'vote': '' });
	                });

	                socket.on('skip_estimation', function (users) {
	                    _this3._userList = users;
	                    _this3.setState({ 'flip': false, 'currentSlide': 'active', 'currentIssue': _this3._next('skip'), 'vote': '' });
	                });

	                socket.on('reset_estimation', function (users) {
	                    _this3._userList = users;
	                    _this3.setState({ 'flip': false, 'currentSlide': 'active', 'vote': '' });
	                });
	            }
	        }, {
	            key: '_next',
	            value: function _next(param) {
	                var noEstimatedIssue = this.state.issueList.filter(function (issue) {
	                    return issue.estimation === '';
	                });
	                var position = noEstimatedIssue.indexOf(this.state.currentIssue);
	                if (param === 'save') {
	                    if (noEstimatedIssue[position + 1]) {
	                        return noEstimatedIssue[position + 1];
	                    }
	                    if (noEstimatedIssue.length > 1) {
	                        return noEstimatedIssue[0];
	                    }
	                }
	                if (param === 'skip') {
	                    if (noEstimatedIssue[position + 1]) {
	                        return noEstimatedIssue[position + 1];
	                    }
	                    return noEstimatedIssue[0];
	                }
	            }
	        }, {
	            key: '_getDiagram',
	            value: function _getDiagram() {
	                return React.createElement(
	                    'table',
	                    { className: 'table-bordered diagram' },
	                    React.createElement(
	                        'tbody',
	                        null,
	                        this._userList.slice().sort(function (a, b) {
	                            return Number(a.current_vote) > Number(b.current_vote);
	                        }).map(function (user) {
	                            return React.createElement(
	                                'tr',
	                                { className: 'col-md-12 test', key: user.id },
	                                React.createElement(
	                                    'td',
	                                    { className: 'col-md-3' },
	                                    user.name
	                                ),
	                                React.createElement(
	                                    'td',
	                                    { className: 'col-md-1 text-center' },
	                                    user.current_vote
	                                ),
	                                React.createElement(
	                                    'td',
	                                    { className: 'col-md-8' },
	                                    React.createElement('div', { className: 'est-bar', style: { width: progressBar(user.current_vote) + 'px' } })
	                                )
	                            );
	                        })
	                    )
	                );
	            }
	        }]);

	        return IssueBox;
	    })(React.Component);

	    var CardBox = (function (_React$Component5) {
	        _inherits(CardBox, _React$Component5);

	        function CardBox() {
	            _classCallCheck(this, CardBox);

	            _get(Object.getPrototypeOf(CardBox.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(CardBox, [{
	            key: 'render',
	            value: function render() {
	                var _this4 = this;

	                var coffee = React.createElement('i', { className: 'fa fa-coffee', 'aria-hidden': 'true' });
	                return React.createElement(
	                    'div',
	                    null,
	                    cardList.map(function (card, index) {
	                        return React.createElement(
	                            'div',
	                            { className: _this4.props.vote === String(card) ? 'chosen card' : 'card',
	                                'data-card': card, key: index, onClick: _this4._sendEstimation.bind(_this4) },
	                            React.createElement(
	                                'div',
	                                { className: 'card-top-data' },
	                                card
	                            ),
	                            React.createElement(
	                                'div',
	                                { className: 'card-center-data' },
	                                card == 'coffee' ? coffee : card
	                            ),
	                            React.createElement(
	                                'div',
	                                { className: 'card-bottom-data' },
	                                card
	                            )
	                        );
	                    })
	                );
	            }
	        }, {
	            key: '_sendEstimation',
	            value: function _sendEstimation(event) {
	                if (!this.props.flip) {
	                    var card = event.currentTarget.dataset['card'];
	                    this.props.saveVote(card);
	                    socket.emit('make_vote', { 'user_id': USER_ID, 'card': card, 'room': ROOM });
	                }
	            }
	        }]);

	        return CardBox;
	    })(React.Component);

	    var IssueNavbar = (function (_React$Component6) {
	        _inherits(IssueNavbar, _React$Component6);

	        function IssueNavbar() {
	            _classCallCheck(this, IssueNavbar);

	            _get(Object.getPrototypeOf(IssueNavbar.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(IssueNavbar, [{
	            key: 'render',
	            value: function render() {
	                return React.createElement(
	                    'div',
	                    { className: 'issue-bar' },
	                    React.createElement(
	                        'button',
	                        { className: this._checkActiveBtn('active'), onClick: this.props.setSlide.bind(this, 'active') },
	                        'Active issue'
	                    ),
	                    React.createElement(
	                        'button',
	                        { className: this._checkActiveBtn('accept'), onClick: this.props.setSlide.bind(this, 'accept') },
	                        'Vote menu'
	                    ),
	                    React.createElement(
	                        'button',
	                        { className: this._checkActiveBtn('completed'), onClick: this.props.setSlide.bind(this, 'completed') },
	                        'Estimated issue'
	                    ),
	                    React.createElement(
	                        'button',
	                        { className: this._checkActiveBtn('all'), onClick: this.props.setSlide.bind(this, 'all') },
	                        'All issue list'
	                    )
	                );
	            }
	        }, {
	            key: '_checkActiveBtn',
	            value: function _checkActiveBtn(slide) {
	                return slide == this.props.activeSlide ? "btn btn-info" : "btn";
	            }
	        }]);

	        return IssueNavbar;
	    })(React.Component);

	    var CommentBox = (function (_React$Component7) {
	        _inherits(CommentBox, _React$Component7);

	        function CommentBox() {
	            _classCallCheck(this, CommentBox);

	            _get(Object.getPrototypeOf(CommentBox.prototype), 'constructor', this).call(this);
	            this.state = {
	                'comments': chatLog
	            };
	        }

	        _createClass(CommentBox, [{
	            key: 'componentWillMount',
	            value: function componentWillMount() {
	                this._addNewComment();
	            }
	        }, {
	            key: 'render',
	            value: function render() {
	                var comments = this._getComments();
	                return React.createElement(
	                    'div',
	                    { className: 'col-md-12 chat-box' },
	                    React.createElement(CommentForm, { addComment: this._sendComment.bind(this) }),
	                    React.createElement(
	                        'div',
	                        { className: 'comment-box' },
	                        ' ',
	                        comments,
	                        ' '
	                    )
	                );
	            }
	        }, {
	            key: '_addNewComment',
	            value: function _addNewComment() {
	                var _this5 = this;

	                socket.on('add_new_comment', function (newComment) {
	                    _this5.setState({ comments: _this5.state.comments.concat([newComment]) });
	                });
	            }
	        }, {
	            key: '_sendComment',
	            value: function _sendComment(user, body) {
	                socket.emit('add_comment', { user: user, body: body, 'room': ROOM });
	            }
	        }, {
	            key: '_getComments',
	            value: function _getComments() {
	                return this.state.comments.slice().reverse().map(function (comment) {
	                    return React.createElement(Comment, {
	                        user: comment.user,
	                        body: comment.body,
	                        key: comment.id });
	                });
	            }
	        }]);

	        return CommentBox;
	    })(React.Component);

	    var CommentForm = (function (_React$Component8) {
	        _inherits(CommentForm, _React$Component8);

	        function CommentForm() {
	            _classCallCheck(this, CommentForm);

	            _get(Object.getPrototypeOf(CommentForm.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(CommentForm, [{
	            key: 'render',
	            value: function render() {
	                var _this6 = this;

	                var sendIcon = React.createElement('i', { className: 'glyphicon glyphicon-share-alt' });
	                return React.createElement(
	                    'form',
	                    { onSubmit: this._handleSubmit.bind(this) },
	                    React.createElement(
	                        'div',
	                        { className: 'input-group' },
	                        React.createElement('input', { className: 'form-control form-group', placeholder: 'Type your comment there', ref: function (input) {
	                                return _this6._body = input;
	                            } }),
	                        React.createElement(
	                            'div',
	                            { className: 'input-group-btn' },
	                            React.createElement(
	                                'button',
	                                { className: 'btn btn-info', type: 'submit' },
	                                'Post comment ',
	                                sendIcon,
	                                ' '
	                            )
	                        )
	                    )
	                );
	            }
	        }, {
	            key: '_handleSubmit',
	            value: function _handleSubmit(event) {
	                event.preventDefault();
	                var body = this._body.value;
	                if (body) {
	                    this.props.addComment(USER, body);
	                    this._body.value = '';
	                }
	            }
	        }]);

	        return CommentForm;
	    })(React.Component);

	    var Comment = (function (_React$Component9) {
	        _inherits(Comment, _React$Component9);

	        function Comment() {
	            _classCallCheck(this, Comment);

	            _get(Object.getPrototypeOf(Comment.prototype), 'constructor', this).apply(this, arguments);
	        }

	        _createClass(Comment, [{
	            key: 'render',
	            value: function render() {
	                return React.createElement(
	                    'div',
	                    { className: 'comment' },
	                    React.createElement(
	                        'p',
	                        null,
	                        this.props.user
	                    ),
	                    React.createElement(
	                        'p',
	                        null,
	                        this.props.body
	                    )
	                );
	            }
	        }]);

	        return Comment;
	    })(React.Component);

	    ReactDOM.render(React.createElement(PokerBox, null), document.getElementById('poker-app'));
	});

/***/ }
/******/ ]);