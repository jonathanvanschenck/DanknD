var logtag = $("#log")

scrolldown = function() {
  $("html, body").animate({ scrollTop: $(document).height() }, "slow");
};

scrollTo = function(jqelement) {
  $("html, body").animate({ scrollTop: jqelement.offset().top}, "slow")
}

log = function(charname,msgtxt) {
  let newhtml = $("<div>");
  newhtml.toggleClass("post",true)
          .text(charname + ' says: ' + msgtxt);
  logtag.append(newhtml);
  scrolldown();
};

render = function(object_list, clear_all, skip_scroll) {
  if (clear_all) {
    logtag.empty();
  }
  object_list.map(function (d) {
    if ($("#"+d.id).length == 0 || clear_all) {
      let parent = logtag;
      if (d.dest_id) {
        parent = $("#"+d.dest_id);
      }
      parent.append(d.html);
      // Attach click functionality to scenes and chapters
      let regex = d.id.match(/(chapter|scene)-card-id-(\d*)/);
      if (!!regex) {
        $("#"+d.id).on("click", function(event) {
          event.stopPropagation();
          // get all the children
          let body = $(this).children("."+regex[1]+"-card-body");
          let children = body.children();
          // if children aren't loaded (or aren't visible)
          if (children.length == 0) {
            // Attempt to render posts
            socket.emit('get_children',{
              gameid: room_number,
              json_list: [{
                objid:+regex[2],
                type:regex[1],
                depth:1
              }]
            })
          } else {
            // Toggle body state
            body.toggleClass('invisible',!body.hasClass('invisible'));
          }
        });
      } else {
        $("#"+d.id).on("click", function(event) {
          console.log("here");
          event.stopPropagation();
        });
      }
    }
  })
  if (!skip_scroll) {
    // scrolldown();
    scrollTo($(".is_current").last());
  }
};

// Attach roll validity checking
check_roll_validity = function(string) {
  let _string = string.replace(/\s/g,"");
  if (!(_string[0] === "+" || _string[0] === "-")) {
    _string = "+" + _string
  }
  let list = _string.match(/[+](?!0)[1-9]\d*d(?!0)[1-9]\d*|[+][AD]d(?!0)[1-9]\d*|[+-](?!0)[1-9]\d*(?!d)|[=][-]{0,1}\d*$/g);
  if (!list) {
    return false;
  }
  return _string.length === list.join("").length
}
$('#post-body').on('input', function () {
  let body = this;
  let err_msg = [];
  let error = false;
  for (let m of body.value.matchAll(/[{]([^}]*)[}]/g)) {
    console.log(m[1],check_roll_validity(m[1]));
    if (!check_roll_validity(m[1])) {
      error = true;
      err_msg.push("`"+m[1]+"`")
    }
  }
  if (error) {
    body.setCustomValidity("Invalid Roll Types: "+err_msg.join(", "));
  } else {
    body.setCustomValidity("");
  }
});


attemptpost = function() {
  let postForm = $('#post-form')[0];
  if (postForm.checkValidity()) {
    postToServer($('#speaker')[0].value,$('#post-body')[0].value)
    // log($('#speaker')[0].value,$('#post-body')[0].value);
    $('#post-body')[0].value = "";
  }
}


// Socket io stuff
var socket = io("/game");
var room_number = $("#room-number")[0].value;
var user_number = $("#user-number")[0].value;
var user_name = $("#user-name")[0].value;

socket.on('connect', function() {
  socket.emit('join', {gameid: room_number})

  // Allow posts with server connection
  $('#post-button').toggleClass('btn-success',true)
                   .toggleClass('btn-warning',false)
                [0].setCustomValidity('');
});

socket.on('disconnect', function() {
  socket.emit('disconnect_request')

  // Prevent posts without server connection
  $('#post-button').toggleClass('btn-success',false)
                   .toggleClass('btn-warning',true)
                [0].setCustomValidity('Disconnected from Server. . .');

  // Turn off "is typing" Functionality
  $('.is-typing').css("display","none");
});

socket.on('log', function(msg) {
  console.log(msg);
});

socket.on('render_objects', function(msg) {
  render(msg.object_list, msg.clear_all, msg.skip_scroll);
});

socket.on("modify_currents", function(msg) {
  // Turn off old currents
  $(".chapter-card").toggleClass('is_current',false);
  $(".scene-card").toggleClass('is_current',false);
  $(".post-card").toggleClass('is_current',false);

  // Turn on currents
  $("#"+msg.current_chapter_id).toggleClass("is_current",true);
  $("#"+msg.current_scene_id).toggleClass("is_current",true)
  $("#"+msg.current_scene_body_id).children().toggleClass("is_current",true);
});


postToServer = function (speaker,body) {
  socket.emit('create_post', {
    speaker:speaker,
    body:body,
    gameid:room_number,
    posterid:user_number
  })
};


// Is Typing Functionality
$('#post-body').focusin(function() {
  socket.emit("set_typing",{user:user_name,state:true,gameid:room_number})
});
$('#post-body').focusout(function() {
  socket.emit("set_typing",{user:user_name,state:false,gameid:room_number})
});
socket.on('is_typing', function(msg) {
  $("#"+msg.user+"-is-typing").css("display", msg.state ? "inline" : "none")
})
