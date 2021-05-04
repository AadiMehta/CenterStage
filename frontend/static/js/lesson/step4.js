// ****** Utilities ******

/**
 * Show a specific modal using modal id
 * @param {String} modalName 
 * @param {Boolean} hide 
 */
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

/**
 * Get Cookie by Name
 * @param {String} cname 
 */
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
// ****** End of Utilities ******

// ****** API Handlers ******

/**
 * Upload file
 */
function uploadFile(file) {
  const token = getCookie('auth_token');
  var form = new FormData();
  form.append('file', file, file.name);
  const fileInfo = {
    name: file.name,
    type: file.type
  }
  $.ajax('/api/lesson/upload/', {
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


function handleLCS4Proceed() {
  let isValid = true;
  $('#goalError').hide();
  $('#requirementError').hide();

  const goals = [];
  const requirements = [];
  $('.goal-input').map((item, goalInput) => {
    if (goalInput.value) {
      goals.push(goalInput.value)
    }
  });

  $('.requirement-input').map((item, requirementInput) => {
    if (requirementInput.value) {
      requirements.push(requirementInput.value)
    }
  });

  if (goals.length === 0) {
    $('#goalError').text('Add Atleast One Goal');
    $('#goalError').show()
    isValid = false;
  }
  if (requirements.length === 0) {
    $('#requirementError').text('Add Atleast One Requirement');
    $('#requirementError').show()
    isValid = false;
  }
  if (isValid) {
    $('#goals').val(JSON.stringify(goals));
    $('#requirements').val(JSON.stringify(requirements));
    $("#step4").submit();
  }
}

function addMoreGoal() {
  const newGoalInput = $('#referenceGoalInput').clone();
  const { index } = newGoalInput.data();
  if (index === 5) {
    return;
  }
  const lastGoalInput = $("#lastGoalInput");
  newGoalInput.insertBefore(lastGoalInput);
  newGoalInput.find('input').val(lastGoalInput.find('input').val());
  newGoalInput.find('input').attr('data-goal-index', index - 1);
  newGoalInput.find('input').addClass('goal-input');
  lastGoalInput.find('input').attr('data-goal-index', index);
  lastGoalInput.find('input').val('')
  newGoalInput.show();
  $('#referenceGoalInput').attr('data-index', index + 1);
}

function addMoreRequirement() {
  const newRequirementInput = $('#referenceRequirementInput').clone();
  const { index } = newRequirementInput.data();
  if (index === 5) {
    return;
  }
  const lastRequirementInput = $("#lastRequirementInput");
  newRequirementInput.insertBefore(lastRequirementInput);
  newRequirementInput.find('input').val(lastRequirementInput.find('input').val());
  newRequirementInput.find('input').attr('data-requirement-index', index - 1);
  newRequirementInput.find('input').addClass('requirement-input');
  newRequirementInput.find('input').attr('data-requirement-index', index);
  lastRequirementInput.find('input').val('')
  newRequirementInput.show();
  $('#referenceRequirementInput').attr('data-index', index + 1);
}


function addMoreFile(fileName) {
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

  
// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  $('#addMoreGoalButton').click(addMoreGoal);
  $('#lastGoalInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreGoal();
    }
  });
  $('#addMoreRequirementButton').click(addMoreRequirement);
  $('#lastRequirementInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreRequirement();
    }
  });

  $("#uploadFile").on('change', function(event) {
    uploadFile(event.target.files[0])
  });
  $('#lcs4Proceed').click(handleLCS4Proceed);
}
$(document).keypress(
  function(event){
    if (event.which == '13') {
      event.preventDefault();
    }
});
init();