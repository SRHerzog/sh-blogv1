/* eslint-env jquery, browser */

$(function() {
	var regname = document.getElementById('regname');
	var password = document.getElementById('password');

	function createComment(commentId, parentId, newText, userName) {
		return "<article class='comment' id='a" + commentId + "'>\
					<p class='comment-body' id='c" + commentId + "'>" + newText + "</p>\
					<footer class='comment-attrib' id='t" + commentId + "'>posted just now by " + userName + "</footer>\
						<form class='singlebutton edit-comment'\
						id='e" + commentId + "' method='get' action='/editcomment'>\
							<input type='hidden' name='comment_id' value='" + commentId + "'>\
							<input type='hidden' name='parent' value='" + parentId + "'>\
							<input type='submit' value='Edit'>\
						</form>\
						<form class='singlebutton delete-comment'\
						id='d" + commentId + "' method='post' action='/devarecomment'>\
							<input type='hidden' name='comment_id' value='" + commentId + "'>\
							<input type='hidden' name='parent' value='" + parentId + "'>\
							<input type='submit' value='Delete'>\
						</form>\
				</article>";
	}

	// Form validation
	$('#regname').keyup(function() {
		if (regname.validity.patternMismatch) {
			regname.setCustomValidity('Only letters and numbers are allowed.');
			regname.checkValidity();
		} else {
			regname.setCustomValidity('');
		}
	});
	$('.pwform').change(function() {
		if ($('#password').val() !== $('#reenter').val()) {
			$('#reenter').addClass('invalid');
		} else {
			$('#reenter').removeClass('invalid');
		}
	});
	$('#regsubmit').click(function() {
		if ($('#password').val() !== $('#reenter').val()) {
			password.setCustomValidity('Password fields do not match. Please retype them and try again.');
		} else if ($('#password').val().length < 6) {
			password.setCustomValidity('Passwords must be at least six characters long.');
		} else {
			password.setCustomValidity('');
		}
	});

	// Comment post and edit
	$('#comment-form').submit(function(event) {
		event.preventDefault();
		var edit = false;
		var url = null;
		var commentId = null;
		var parentId = $('#post-id').data('post');
		var newText = $('#content').val();
		if ($('#action-edit').length) {
			edit = true;
			url = '/editcomment';
			commentId = $('#action-edit').val();
		} else {
			url = '/newcomment';
		}
		$.ajax({
			method: 'POST',
			url: url,
			data: {
				'comment_id': commentId,
				'parent': parentId,
				'content': newText,
				'js': true,
			},
			dataType: 'text',
			success: function(response) {
				if (response[0] !== '!') {
					if (edit) {
						$('#a' + commentId).show();
						$('.singlebutton').show();
						$('#c' + commentId).html($('#content').val().replace(/\n/g, '<br />'));
						$('#t' + commentId).remove();
						$('#action-edit').remove();
						$('#c' + commentId).after(
							"<footer class='comment-attrib edit' id='t" + commentId + "'>\
								edited just now</footer>");
					} else {
						commentId = response.split(' ')[0];
						var userName = response.split(' ')[1];
						$('#newcomment').after(createComment(commentId, parentId, newText, userName));
					}
					$('#content').val('');
					$('#post-link').text('Post a new comment');
					window.location.hash = '#';
				} else {
					alert('Comment error. Reload the page and try again, or contact admin.');
				}
			},
		});
	});

	/* Edit button: move comment content into form, hide original comment while editing,
	and hide all Edit and Delete buttons while editing */
	$(document).on('submit', 'form.edit-comment', function(event) {
		event.preventDefault();
		var commentId = event.target.id.slice(1);
		$('.singlebutton').hide();
		$('#cancel-edit').data('comment', commentId);
		$('#a' + commentId).hide();
		$('#comment-form').append("<input type='hidden' id='action-edit' value='" + commentId + "'>");
		window.location.hash = '#newcomment';
		$('#post-link').text('Editing your comment:');
		$('#content').val($('#c' + commentId).text());
	});

	// Close edit form, show comment that was being edited, and show Edit and Delete buttons
	$('#cancel-edit').click(function() {
		var commentId = $(this).data('comment');
		$('#a' + commentId).show();
		$('.singlebutton').show();
		$('#content').val('');
		$('#action-edit').remove();
		$('#post-link').text('Post a new comment');
		window.location.hash = '#';
	});

	// Delete comment
	$(document).on('submit', 'form.delete-comment', function(event) {
		event.preventDefault();
		var parentId = $('#post-id').data('post');
		var commentId = event.target.id.slice(1);
		$.ajax({
			method: 'POST',
			url: '/deletecomment',
			data: {
				'comment_id': commentId,
				'parent': parentId,
			},
			dataType: 'text',
			success: function(response) {
				if (response[0] !== '!') {
					$('#a' + commentId).remove();
					window.location.hash = '#';
				} else {
					alert('Comment error. Reload the page and try again, or contact admin.');
				}
			},
		});
	});

	// Like and unlike
	$(document).on('submit', 'form.like', function(event) {
		event.preventDefault();
		var form = $(this);
		var postId = form.data('post');
		var url = form.attr('action');
		var likes = $('#l' + postId).text();
		$.ajax({
			method: 'POST',
			url: url,
			data: {
				'post_id': postId,
			},
			dataType: 'text',
			success: function(response) {
				if (response[0] !== '!') {
					if (url === '/like') {
						$('#l' + postId).text(++likes);
						form.attr('action', '/unlike');
						$('.likebutton.' + postId).val('Unlike');
					} else {
						$('#l' + postId).text(--likes);
						form.attr('action', '/like');
						$('.likebutton.' + postId).val('Like');
					}
				} else {
					alert('Like error. Reload the page and try again, or contact admin.');
				}
			},
		});
	});
});
