// ****** Event Handlers ****** 
  
/**
 * On Proceed Clicked,
 * Validate Input and Go to Step 2
 */
function handleNTS1Proceed() {
    console.log("in proceed");
    let isValid = true;
    $('#noteNameError').hide();
    $('#noteDescriptionError').hide();
    $('#noteNoOfParticipantsError').hide();
    $('#noteLanguageError').hide();
    $('#noteTypeError').hide();
    const noteName = $('#noteName')[0].value;
    const noteDescription = $('#noteDescription')[0].value;
    const noteLanguage = $('#noteLanguage')[0].value;
    const noteType = $('#noteType .selected')[0].dataset.noteType;
    if (!noteName) {
      $('#noteNameError').text('Please Provide note Name');
      $('#noteNameError').show()
      isValid = false;
    }
    console.log(isValid);
    if (!noteDescription) {
      $('#noteDescriptionError').text('Please Provide note Description');
      $('#noteDescriptionError').show()
      isValid = false;
    }
    console.log(isValid);
    if (noteLanguage === 'none') {
      $('#noteLanguageError').text('Please Select note Language');
      $('#noteLanguageError').show()
      isValid = false;
    }
    console.log(isValid);
    if (!noteType) {
      $('#noteTypeError').text('Please Select note Type');
      $('#noteTypeError').show()
      isValid = false;
    }
    console.log(isValid);
    if (isValid) {
      console.log("proceed eng");
      $("#step1").submit();
      console.log($('#subscriptionType')[0].value)
      console.log("proceed complete");
    }
}

function handleNoteTypeSelect(event) {
  $('#oneTimeSubscription').removeClass('selected');
  $('#weeklySubscription').removeClass('selected');
  $('#monthlySubscription').removeClass('selected');
  $('#annualSubscription').removeClass('selected');
  $(event.target).addClass('selected');
  $("#subscriptionType").val(event.currentTarget.dataset.noteType);
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */

  $('#nts1Proceed').click(handleNTS1Proceed);
  $('#oneTimeSubscription').click(handleNoteTypeSelect);
  $('#weeklySubscription').click(handleNoteTypeSelect);
  $('#monthlySubscription').click(handleNoteTypeSelect);
  $('#annualSubscription').click(handleNoteTypeSelect);
}

init();