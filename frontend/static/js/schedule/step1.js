// ****** Event Handlers ****** 
  
/**
 * On Proceed Clicked,
 * Validate Input and Go to Step 2
 */
function handleSchedule1Proceed() {
    let isValid = true;
    $('#lessonTopicError').hide();
    $('#inviteesError').hide();
    $('#sessionTypeError').hide();
    const lessonTopic = $('#lessonTopic')[0].value;
    const sessionType = $('#lessonType .selected')[0].dataset.lessonType;    
    const invitees = [];
    $('.invitee-input').map((item, inviteeInput) => {
        if (inviteeInput.value) {
            invitees.push(inviteeInput.value)
        }
    });
    if (!lessonTopic) {
      $('#lessonTopicError').text('Please Provide Lesson Topic');
      $('#lessonTopicError').show()
      isValid = false;
    }
    if (invitees.length === 0) {
      $('#inviteesError').text('Add Atleast One Invitee');
      $('#inviteesError').show()
      isValid = false;
    } else {
      $('#invitees')[0].value = JSON.stringify(invitees);
    }
    if (!sessionType) {
      $('#sessionTypeError').text('Please Select Session Type');
      $('#sessionTypeError').show()
      isValid = false;
    }
    if (isValid) {
      $("#step1").submit();
    }
}

function addMoreInvitee() {
  const newInviteeInput = $('#referenceInviteeInput').clone();
  const { index } = newInviteeInput.data();
  if (index === 5) {
    return;
  }
  const lastInviteeInput = $("#lastInviteeInput");
  if (lastInviteeInput.find('input').val()) {
      newInviteeInput.insertBefore(lastInviteeInput);
      newInviteeInput.find('input').val(lastInviteeInput.find('input').val());
      newInviteeInput.find('input').attr('data-invitee-index', index - 1);
      newInviteeInput.find('input').addClass('invitee-input');
      newInviteeInput.find('input').attr('data-invitee-index', index);
      lastInviteeInput.find('input').val('')
      newInviteeInput.show();
      $('#referenceInviteeInput').attr('data-index', index + 1);    
  }
}

function handleLessonTypeSelect(event) {
  $('#singleSession').removeClass('selected');
  $('#multiSession').removeClass('selected');
  $('#ongoingSession').removeClass('selected');
  $(event.target).addClass('selected');
  $("#no_of_sessions").val(event.currentTarget.dataset.lessonType);
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */

  $('#schedule1Proceed').click(handleSchedule1Proceed);
  $('#singleSession').click(handleLessonTypeSelect);
  $('#multiSession').click(handleLessonTypeSelect);
  $('#ongoingSession').click(handleLessonTypeSelect);
  $('#addMoreInviteeButton').click(addMoreInvitee);
  $('#lastInviteeInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreInvitee();
    }
  });
}

init();