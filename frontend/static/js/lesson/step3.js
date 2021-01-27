/**
 * Read Uploaded File URL
 * @param {Element} input 
 */
function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function(e) {
      $('#previewCoverImage').attr('src', e.target.result);
      $('#previewCoverImageDataUrl')[0].value = e.target.result;
    }
    reader.readAsDataURL(input.files[0]);
  }
}

// ****** Event Handlers ****** 

function handleLCS3Proceed() {
  let isValid = true;
  $('#coverImageError').hide();
  $('#videoLinkError').hide();
  if (isValid) {
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
  $("#coverImageUpload").change(function() {
    readURL(this);
  });

  $('#lcs3Proceed').click(handleLCS3Proceed);
}

init();