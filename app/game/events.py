from flask import copy_current_request_context
from flask_socketio import emit, disconnect, join_room

from app import socketio,db
from app.models import Post, Game, Chapter

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
    join_room(msg['gameid'])
    emit('log', {'data': 'Joined room: '+msg['gameid']})
    game = Game.query.get(int(msg['gameid']))
    obj_list = []
    for chapter in game.chapters:
        obj_list.append({"html":chapter.to_HTML()})
        for scene in chapter.scenes:
            obj_list.append({
                "html":scene.to_HTML(),
                "dest_id":chapter.get_inner_HTML_id()
            })
            for post in scene.posts:
                obj_list.append({
                    "html":post.to_HTML(),
                    "dest_id":scene.get_inner_HTML_id()
                })

    emit('render_objects',
         {
            'object_list':obj_list,
            'clear_all':True
         },
         room = msg['gameid'],
         broacast = True
    )


@socketio.on('echo', namespace='/game')
def on_echo(msg):
    emit('log', msg)

# @socketio.on('get_all_posts', namespace='/game')
# def on_get_all_posts(msg):
#     obj_list = []
#     for chapter in Chapter.query.filter_by(game_id=int(msg['gameid'])):
#         obj_list.append({"html":chapter.to_HTML()})
#         for scene in chapter.scenes:
#             obj_list.append({
#                 "html":scene.to_HTML(),
#                 "dest_id":chapter.get_inner_HTML_id()
#             })
#             for post in scene.posts:
#                 obj_list.append({
#                     "html":post.to_HTML(),
#                     "dest_id":scene.get_inner_HTML_id()
#                 })
#
#     emit('render_posts',
#          {
#             'object_list':obj_list,
#             'clear_all':True
#          },
#          room = msg['gameid'],
#          broacast = True
#     )

@socketio.on('create_post', namespace='/game')
def on_create_post(msg):
    scene = Game.query.get(int(msg['gameid'])).current_scene
    p = Post(
        speaker = msg['speaker'],
        body = msg['body'],
        poster_id = int(msg['posterid']),
        scene = scene,
    )
    db.session.add(p)
    db.session.commit()
    emit(
            'render_objects',
            {
                'object_list':[
                    {
                        "html":p.to_HTML(),
                        "dest_id":scene.get_inner_HTML_id()
                    }
                ],
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
