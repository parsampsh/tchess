""" Serves a game and waits for guest to play online """

import uuid
import logging
from flask import Flask, request, Response

CURRENT_SESSION = None

def serve(game_object, host='0.0.0.0', port=8799):
    """ Serve the server """
    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route('/connect')
    def connect():
        global CURRENT_SESSION

        # check session already started
        if CURRENT_SESSION is not None:
            return Response('session currently started', status=401)

        # get user confirmation
        # TODO : show name of user
        if input('User wants to play. Do you accept? [y/n] ') not in ('y', 'Y'):
            return Response('Rejected', status=403)

        print('Accepted.')

        game_object.guess_connected = True

        # start the session
        CURRENT_SESSION = str(uuid.uuid4())
        return CURRENT_SESSION

    @app.route('/render')
    def render():
        if CURRENT_SESSION is None:
            return Response('Please start a session first', status=401)

        try:
            if request.args['session'] == CURRENT_SESSION:
                # render the game
                return game_object.render()
            else:
                raise
        except:
            return Response('invalid session', status=401)

    @app.route('/command')
    def command():
        if CURRENT_SESSION is None:
            return Response('Please start a session first', status=401)

        try:
            if request.args['session'] == CURRENT_SESSION:
                # put the command on the game object
                game_object.guess_ran = game_object.run_command(request.args['cmd'])
                return game_object.guess_ran
            else:
                raise ValueError()
        except:
            raise
            return Response('invalid session', status=401)

    print('Serving on ' + host + ':' + str(port))
    print('Others can join this game by running `tchess --connect ' + host + ':' + str(port) + '`')

    app.run(host, port)
