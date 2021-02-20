""" Serves a game and waits for guest to play online """

import uuid
import logging
from flask import Flask, request, Response
from functools import wraps

CURRENT_SESSION = None

def serve(game, host='0.0.0.0', port=8799):
    """ Serve the server """
    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    def get_session():
        """ Returns user session id """
        try:
            return request.args['session']
        except:
            return None

    def requires_session(f):
        """ Middleware for requiring session in some routes """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if CURRENT_SESSION is None or get_session() != CURRENT_SESSION:
                return Response('invalid session', status=403)
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/connect')
    def connect():
        global CURRENT_SESSION

        # check session already started
        if CURRENT_SESSION is not None:
            return Response('session currently started', status=401)

        # get user confirmation
        try:
            guest_name = request.args['name']
            if game.guest_color == 'white':
                game.white_player = guest_name
            else:
                game.black_player = guest_name
        except:
            guest_name = 'Unknow'
        if input(
            'User `' + guest_name + '` wants to play. Do you accept? [y/n] '
        ) not in ('y', 'Y'):
            print('Rejected.')
            return Response('Rejected', status=403)

        # by setting this prop to True, main thread will know that guest was connected and starts the game
        game.guest_connected = True

        # generate the session id
        CURRENT_SESSION = str(uuid.uuid4())
        return CURRENT_SESSION

    @app.route('/me')
    @requires_session
    def me():
        return game.guest_color

    @app.route('/render')
    @requires_session
    def render():
        # render the game and turn
        output = game.turn + '\n' + game.render()
        if game.is_end:
            # game is finished
            output += '\n' + ('Checkmate!' + (' ' * (len(game.ROW_SEPARATOR)-10)))
            output += '\n' + (game.winner + ' won!' + (' ' * (len(game.ROW_SEPARATOR)-10)))
        return output

    @app.route('/command')
    @requires_session
    def command():
        # put the command on the game object
        if 'cmd' not in request.args.keys():
            return Response('missing `cmd` argument', status=401)
        if request.args['cmd'].strip().lower() == 'back':
            return Response('command `back` is disabled for guest', status=401)
        game.guest_ran = game.run_command(request.args['cmd'])
        return game.guest_ran

    print('Serving on ' + host + ':' + str(port))
    print('Others can join this game by running `tchess --connect ' + host + ':' + str(port) + '`')

    app.run(host, port)
