from flask import copy_current_request_context
from flask_socketio import emit, disconnect, join_room

from app import socketio,db
from app.models import Post

@socketio.on('connect', namespace='/game')
def on_connect():
    emit('log', {'data': 'Connected at server!'})

@socketio.on('disconnect_request')
def on_disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    return emit('log', {'data': 'Disconnected from server!'}, callback=can_disconnect)

@socketio.on('join', namespace='/game')
def on_join(msg):
    join_room(msg['room'])
    emit('log', {'data': 'Joined room: '+msg['room']})
    post_list = Post.query.filter_by(game_id=int(msg['room']))
    emit(
            'render_posts',
            {
                'posts':[p.to_HTML() for p in post_list],
                'clear_all':True
            }
        )


@socketio.on('echo', namespace='/game')
def on_echo(msg):
    emit('log', msg)

@socketio.on('get_all_posts', namespace='/game')
def on_get_all_posts(msg):
    post_list = Post.query.filter_by(game_id=int(msg['gameid']))
    emit('render_posts',
         {
            'posts':[p.to_HTML() for p in post_list]
         },
         room = msg['gameid'],
         broacast = True
    )

@socketio.on('create_post', namespace='/game')
def on_create_post(msg):
    p = Post(
        speaker = msg['speaker'],
        body = msg['body'],
        poster_id = int(msg['posterid']),
        game_id = int(msg['gameid']),
    )
    db.session.add(p)
    db.session.commit()
    emit(
            'render_posts',
            {
                'posts':[p.to_HTML()],
                'clear_all':False
            },
            room = msg['gameid'],
            broacast = True
        )

@socketio.on('set_typing', namespace='/game')
def on_set_typing(msg):
    emit(
            'is_typing',
            msg,
            room = msg['gameid'],
            broadcast = True
        )
