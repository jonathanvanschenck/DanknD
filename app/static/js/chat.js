var logtag = $("#log")

scrolldown = function() {
  $("html, body").animate({ scrollTop: $(document).height() }, "slow");
};

log = function(charname,msgtxt) {
  let newhtml = $("<div>");
  newhtml.toggleClass("post",true)
          .text(charname + ' says: ' + msgtxt);
  logtag.append(newhtml);
  scrolldown();
};

render = function(html, clear_all) {
  if (clear_all) {
    logtag.empty();
  }
  logtag.append(html);
  scrolldown();
};

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
  socket.emit('join', {room: room_number})

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

socket.on('render_posts', function(msg) {
  render(msg.posts, msg.clear_all);
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
