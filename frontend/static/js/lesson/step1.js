// ****** Event Handlers ****** 
  
/**
 * On Proceed Clicked,
 * Validate Input and Go to Step 2
 */
function handleLCS1Proceed() {
    let isValid = true;
    $('#lessonNameError').hide();
    $('#lessonDescriptionError').hide();
    $('#lessonNoOfParticipantsError').hide();
    $('#lessonLanguageError').hide();
    $('#lessonTypeError').hide();
    const lessonName = $('#lessonName')[0].value;
    const lessonDescription = $('#lessonDescription')[0].value;
    const lessonNoOfParticipants = $('#lessonNoOfParticipants')[0].value;
    const lessonLanguage = $('#lessonLanguage')[0].value;
    const lessonType = $('#lessonType .selected')[0].dataset.lessonType;
    if (!lessonName) {
      $('#lessonNameError').text('Please Provide Lesson Name');
      $('#lessonNameError').show()
      isValid = false;
    }
    if (!lessonDescription) {
      $('#lessonDescriptionError').text('Please Provide Lesson Description');
      $('#lessonDescriptionError').show()
      isValid = false;
    }
    if (!lessonNoOfParticipants) {
      $('#lessonNoOfParticipantsError').text('Please Select Number of participants');
      $('#lessonNoOfParticipantsError').show()
      isValid = false;
    }
    if (lessonLanguage === 'none') {
      $('#lessonLanguageError').text('Please Select Lesson Language');
      $('#lessonLanguageError').show()
      isValid = false;
    }
    if (!lessonType) {
      $('#lessonLanguageError').text('Please Select Lesson Type');
      $('#lessonLanguageError').show()
      isValid = false;
    }
    if (isValid) {
      $("#step1").submit();
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

  $('#lcs1Proceed').click(handleLCS1Proceed);
  $('#singleSession').click(handleLessonTypeSelect);
  $('#multiSession').click(handleLessonTypeSelect);
  $('#ongoingSession').click(handleLessonTypeSelect);
  $('#lessonNoOfParticipants').change((event) => {
    if (event.target.value > 200) {
      event.target.value = 200;
    }
    if (event.target.value == 2) {
      $('#lessonType')[0].value = 'ONE_ON_ONE';
    } else {
      $('#lessonType')[0].value = 'GROUP';
    }
  })
}

init();