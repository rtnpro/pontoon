// remap jQuery to $
(function($) {

  $(function() {
  	
	// Prepare iframe size and resize it with window
    $('#source').height($(document).height() - $('#pontoon').height());
    $(window).resize(function () {
      $('#source').height($(document).height() - $('#pontoon').height());
    });

    // Resizable
	var mouseMoveHandler = function(e) {
	  var initial = e.data.initial,
          u = Math.min(Math.max(initial.uHeight + (e.pageY - initial.offTop), initial.min), initial.max),
          b = Math.min(Math.max(initial.bHeight - (e.pageY - initial.offTop), initial.min), initial.max);
      initial.up.height(u);
      initial.below.height(b);

      $('#iframe-cover').height(initial.up.height()); // iframe fix
    };
    var mouseUpHandler = function(e) {
      $(document)
        .unbind('mousemove', mouseMoveHandler)
        .unbind('mouseup', mouseUpHandler);

      $('#iframe-cover').hide(); // iframe fix
      if (e.data.initial.below.height() === 0) {
      	$('#pontoon').removeClass('opened');
      } else {
      	$('#pontoon').addClass('opened');
      }
    };
	$('#logo').bind('mousedown', function(e) {
      e.preventDefault();

      var up = $('#source'),
          below = $('#entitylist'),
          data = {
            up: up,
            below: below,
            uHeight: up.height(),
            bHeight: below.height(),
            offTop: e.pageY,
            min: 0,
            max: $(document).height()
          };

      // iframe fix: Prevent iframes from capturing the mousemove events during a drag
      $('#iframe-cover').show().height(up.height());

      $(document)
        .bind('mousemove', { initial: data }, mouseMoveHandler)
        .bind('mouseup', { initial: data }, mouseUpHandler);
    });

	// Load iframe contents
    var website = window.location.search.split("?url=")[1] || "";
    if (website.length > 0) {
      $('#intro').slideUp("fast", function() {
        // TODO: use real URLs
        $('#source').attr('src', /* website */ 'projects/testpilot');
        $('#pontoon .url').val(/* website */ 'projects/testpilot');
      });

      $('#source').unbind("load.pontoon").bind("load.pontoon", function() {
        // Quit if website not specified
        if (!$(this).attr('src')) {
          return;
        }
        // Initialize Pontoon
        Pontoon.init(this.contentDocument, document);
      });
        
    } else {
	    // Empty iframe if cached
	    $("#source").attr("src", "about:blank");
  	}

    // Load website into iframe
    $('.url').keypress(function (e) {
      var code = (e.keyCode ? e.keyCode : e.which);
      if (code === 13) {
      	window.location.search = "url=projects/testpilot";
      }
    });

  });

}(this.jQuery));

// usage: log('inside coolFunc',this,arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function() {
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if (this.console) {
    console.log(Array.prototype.slice.call(arguments));
  }
};

// catch all document.write() calls
(function(doc) {
  var write = doc.write;
  doc.write = function(q) {
    log('document.write(): ', arguments);
    if (/docwriteregexwhitelist/.test(q)) {
      write.apply(doc,arguments);
    }
  };
}(document));