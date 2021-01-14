// ****** Event Handlers ****** 

function handleLCS3Proceed() {
  let isValid = true;
  $('#coverImageError').hide();
  $('#videoLinkError').hide();
  // const coverImage = $('#coverImage')[0].value;
  const videoLink = $('#videoLink')[0].value;
  // if (!coverImage) {
  //   $('#coverImageError').text('Please Provide Cover Image');
  //   $('#coverImageError').show()
  //   isValid = false;
  // }
  if (!videoLink) {
    $('#videoLinkError').text('Please Provide Video Link');
    $('#videoLinkError').show()
    isValid = false;
  }
  if (isValid) {
    console.log('submitting');
    $("#step3").submit();
  }
}


function handleAvailabilityTypeSelect(event) {
  $("#publicButton").removeClass('selected');
  $("#privacyButton").removeClass('selected');
  $(event.target).addClass('selected');
  $("#is_private").val(event.currentTarget.dataset.privacy);
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */

  $('#publicButton').click(handleAvailabilityTypeSelect);
  $('#privacyButton').click(handleAvailabilityTypeSelect);
  /*
      Step2 Time Slot Selection
  */
  $('#lcs3Proceed').click(handleLCS3Proceed);
}

init();