from flask import copy_current_request_context
from flask_socketio import emit, disconnect, join_room
from flask_login import current_user

from app import socketio,db
from app.models import Post, Game, Chapter, Scene
from app.game.roll_parser import roll_msg

# ---- Helper Functions ----

def _pyobj_to_obj_list(object, result_list, depth, user = None):
    json = {}
    try:
        json['dest_id'] = object.scene.get_inner_HTML_id()
    except AttributeError:
        pass
    try:
        json['dest_id'] = object.chapter.get_inner_HTML_id()
    except AttributeError:
        pass
    json.update({
        "html" : object.to_HTML(user),
        "id" : object.get_outer_HTML_id()
    })
    result_list.append(json)
    if depth > 0:
        child_list = []
        try:
            child_list = object.scenes
        except AttributeError:
            pass
        try:
            child_list = object.posts
        except AttributeError:
            pass
        for c in child_list:
            _pyobj_to_obj_list(c, result_list, depth = depth-1, user = user)
    return

def json_to_object(json):
    model = {"post":Post,"chapter":Chapter,"scene":Scene}[json['type'].lower()]
    return model.query.get(json['objid'])

def generate_obj_list(json_list, user = None):
    """json_list = [json,json,...]
    json = {"objid":int,"type":str,"recursive":bool,depth:int}
      objid: int used by model.query.get() to pull sqlalchemy object
      type: str used to select model type (ie "Post" or "Chapter"),
          insenstitive to case
      depth: interger (or string) specifying what tree depth to recrusively
          pull children from (0 (or "none") -> no children, 1 -> children,
          2 (or "all") -> children of children)
    """
    result_list = []
    for json in json_list:
        depth = json.pop('depth',0)
        try:
            depth = {"none":0,"all":2}[depth]
        except KeyError:
            pass
        _pyobj_to_obj_list(
            json_to_object(json),
            result_list,
            depth,
            user
        )
    return result_list


# --- Socketio Functions ---

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
    obj_list = generate_obj_list(
        [{
            "objid":c.id,
            "type":"Chapter",
            "depth":["none","all"][int(c is game.current_chapter)]
        } for c in game.chapters],
        current_user
    )

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


@socketio.on('create_post', namespace='/game')
def on_create_post(msg):
    if current_user.is_anonymous:
        return
    game = Game.query.get(int(msg['gameid']))
    # Make sure use has post priveleges
    if not game.has_member(current_user):
        return
    scene = game.current_scene
    speaker = msg['speaker']
    # Make sure no one hacks the form to speak for another character
    if not speaker in [c.name for c in current_user.owned_characters]:
        speaker = "Narrator"
    p = Post(
        speaker = speaker,
        body = roll_msg(msg['body']),
        poster_id = current_user.id,
        scene = scene,
    )
    db.session.add(p)
    db.session.commit()
    obj_list = generate_obj_list(
        [{"objid":p.id,"type":"Post","depth":"none"}],
        current_user
    )
    emit(
            'render_objects',
            {
                'object_list':obj_list,
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

@socketio.on('get_children', namespace='/game')
def on_get_children(msg):
    obj_list = generate_obj_list(
        msg['json_list'],
        current_user
    )
    emit(
            'render_objects',
            {
                'object_list':obj_list,
                'clear_all':False,
                'skip_scroll':True
            },
            room = msg['gameid'],
            broacast = False
        )

@socketio.on('get_currents', namespace='/game')
def on_get_currents(msg):
    game = Game.query.get(int(msg['gameid']))
    chapter = game.current_chapter
    scene = game.current_scene
    emit(
        'modify_currents',
        {
            "current_chapter_id":chapter.get_outer_HTML_id(),
            "current_scene_id":scene.get_outer_HTML_id(),
            "current_scene_body_id":scene.get_inner_HTML_id()
        },
        room = msg['gameid']
    )

def set_currents(gameid):
    game = Game.query.get(gameid)
    chapter = game.current_chapter
    scene = game.current_scene
    emit(
        'modify_currents',
        {
            "current_chapter_id":chapter.get_outer_HTML_id(),
            "current_scene_id":scene.get_outer_HTML_id(),
            "current_scene_body_id":scene.get_inner_HTML_id()
        },
        room = str(gameid),
        broadcast = True,
        namespace = '/game'
    )
