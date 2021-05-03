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
    const lessonLanguage = $('#lessonLanguage')[0];
    var selectedLanguages = [...lessonLanguage.options]
                      .filter(option => option.selected)
                      .map(option => option.value);
    const lessonType = $('#lessonType .selected')[0].dataset.lessonType;
    $('#languages').val(JSON.stringify(selectedLanguages));
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
    if (lessonNoOfParticipants<1) {
      $('#lessonNoOfParticipantsError1').text('Number of participants must be greater than zero.');
      $('#lessonNoOfParticipantsError1').show();
      isValid = false;
    }
    if (lessonLanguage === 'none') {
      $('#lessonLanguageError').text('Please Select Lesson Language');
      $('#lessonLanguageError').show()
      isValid = false;
    }
    if (!lessonType) {
      $('#lessonTypeError').text('Please Select Lesson Type');
      $('#lessonTypeError').show()
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
  // let paymentAccount = $("#step1").data('paymentAccount') === 'True'? true : false;
  // let zoomLinked = $("#step1").data('zoomLinked')  === 'True'? true : false;
  
  $('#lcs1Proceed').click(handleLCS1Proceed);
  $('#singleSession').click(handleLessonTypeSelect);
  $('#multiSession').click(handleLessonTypeSelect);
  $('#ongoingSession').click(handleLessonTypeSelect);
  $('#lessonNoOfParticipants').change((event) => {
    const currEle = $('#lessonNoOfParticipants');
    const value = event.target.value;
    const errorEle = $('#lessonNoOfParticipantsError1');
    let lessonType = $('#lessonType');
    errorEle.hide();

    if(value < 1 || value == ""){
      errorEle.text('Number of participants must be greater than 0.');
      errorEle.show();
      lessonType.val('');
    } else if (value == 1) {
      lessonType.val('ONE_ON_ONE');
      errorEle.hide();
    } else if (value >= 2) {
      $('#lessonType').val('GROUP');
      const output = value > 200 ? 200 : value;
      currEle.val(output);
      errorEle.hide();
    }

  })

}

init();