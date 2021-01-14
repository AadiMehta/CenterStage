

  
// ****** Event Handlers ****** 


function handleLCS3Proceed() {
    $("#step3").submit();
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
    $('#lcs2Proceed').click(handleLCS2Proceed);
  }
  
  init();