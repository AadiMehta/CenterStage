/**
 * Read Uploaded File URL
 * @param {Element} input 
 */
 var developerKey = 'AIzaSyBgJlUke-myaOEwmgfob8ASlFqE3L45TdU';

    // The Client ID obtained from the Google API Console. Replace with your own Client ID.
var clientId = "435993188528-d26m19onhkdg87aq7cu2fu88msv9pkp8.apps.googleusercontent.com"

// Replace with your own project number from console.developers.google.com.
// See "Project number" under "IAM & Admin" > "Settings"
var appId = "435993188528";

// Scope to use to access user's Drive items.
var scope = 'https://www.googleapis.com/auth/drive.readonly';

var pickerApiLoaded = false;
var oauthToken;

function loadPicker() {
    gapi.load('auth', {'callback': onAuthApiLoad});
    gapi.load('picker', {'callback': onPickerApiLoad});
}

function onAuthApiLoad() {
    window.gapi.auth.authorize(
        {
          'client_id': clientId,
          'scope': scope,
          'immediate': false
        },
        handleAuthResult);
    }

function onPickerApiLoad() {
    pickerApiLoaded = true;
    createPicker();
    }

function handleAuthResult(authResult) {
    if (authResult && !authResult.error) {
      oauthToken = authResult.access_token;
      createPicker();
    }
 }

function createPicker() {
    if (pickerApiLoaded && oauthToken) {
      var view = new google.picker.View(google.picker.ViewId.DOCS);
      view.setMimeTypes("image/png,image/jpeg,image/jpg");
      var picker = new google.picker.PickerBuilder()
          .enableFeature(google.picker.Feature.NAV_HIDDEN)
          .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
          .setAppId(appId)
          .setOAuthToken(oauthToken)
          .addView(view)
          .addView(new google.picker.DocsUploadView())
          .setDeveloperKey(developerKey)
          .setCallback(pickerCallback)
          .build();
       picker.setVisible(true);
    }
}

function pickerCallback(data) {
      if (data.action == google.picker.Action.PICKED) {
        var fileId = data.docs[0].id;
        var fileURL = data.docs[0].url;
        $('#driveURL')[0].value = fileURL;
        console.log(fileURL);
      }
  }

function showPickerDialog(){
        loadPicker();
    }

function showModal(modalName, hide) {
  if (hide) {
      hideAll();
  }
  $(`#${modalName}`).modal('toggle');
  $(`#${modalName}`).modal('show');
}



/**
* Hide a specific modal using modal id
* @param {String} modalName 
*/
function hideModal(modalName) {
  $(`#${modalName}`).modal('hide');
}

/**
* Hide all Modals
*/
function hideAll() {
  $('.modal').map((index, modalEl) => {
      $(`#${modalEl.id}`).modal('hide');
  })
}


function getCookie(cname) {
  /**
   * Gets Cookie from cookie name
   */
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}


function addMoreFile(fileName) {
  console.log(fileName);
  const newUploadedFile = $('#referenceUploadedFile').clone();
  const { index } = newUploadedFile.data();
  if (index === 5) {
    return;
  }
  const uploadPlusButton = $("#uploadButton");
  newUploadedFile.insertBefore(uploadPlusButton);
  newUploadedFile.find('button').text(fileName);
  newUploadedFile.removeAttr('id');
  newUploadedFile.show();
  $('#referenceUploadedFile').attr('data-index', index + 1);
}

function uploadFile(file) {
  const token = getCookie('auth_token');
  var form = new FormData();
  form.append('file', file, file.name);
  const fileInfo = {
    name: file.name,
    type: file.type
  }
  $.ajax('/api/note/upload/', {
    method: "POST",
    timeout: 0,
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    processData: false,
    mimeType: "multipart/form-data",
    contentType: false,
    data: form,
    success: function (data, status, xhr) {
      const {url} = JSON.parse(data);
      const uploadedFiles = $('#readingFiles')[0].value;
      let files = []
      if (uploadedFiles) {
        files = JSON.parse(uploadedFiles);
      }
      files.push({
        url,
        ...fileInfo
      })
      $('#readingFiles')[0].value = JSON.stringify(files);
      addMoreFile(fileInfo.name);
      hideModal('uploadFilesModal');
    },
    error: function (jqXhr, textStatus, errorMessage) {
      console.log('Error while uploading file', errorMessage)
    }
  });
}

// ****** Event Handlers ****** 

function handleNTS2Proceed() {
  let isValid = true;
  if (isValid) {
    console.log($("#is_private")[0].value);
    $("#step2").submit();
  }
}


function handleAvailabilityTypeSelect(event) {
  console.log("in public");
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
  $("#uploadFile").on('change', function(event) {
    uploadFile(event.target.files[0])
  });

  $('#nts2Proceed').click(handleNTS2Proceed);
}

init();