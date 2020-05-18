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


// Socket io stuff
var socket = io("/game");
var room_number = $("#room-number")[0].value;

socket.on('connect', function() {
  socket.emit('join', {gameid: room_number})
});

socket.on('disconnect', function() {
  socket.emit('disconnect_request')
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
