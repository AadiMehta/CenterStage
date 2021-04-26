// ****** Utilities ******

/**
 * Show a specific modal using modal id
 * @param {String} modalName 
 * @param {Boolean} hide 
 */
function showModal(modalName, hide) {
    hideAll();
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
 * Set Cookie in the browser
 */
function setCookie(cname, cvalue, exMins) {
  var d = new Date();
  d.setTime(d.getTime() + (exMins*60*1000));
  var expires = "expires="+d.toUTCString();  
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
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

function openInNewTab(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

/**
 * Opens Popup window as the current window as parent
 */
function openWindow(url, winName, w, h, scroll){
  LeftPosition = (screen.width) ? (screen.width-w)/2 : 0;
  TopPosition = (screen.height) ? (screen.height-h)/2 : 0;
  settings =
      'height='+h+',width='+w+',top='+TopPosition+',left='+LeftPosition+',scrollbars='+scroll+',resizable'
  window.open(url, winName, settings)
}    

// ****** End of Utilities ******

// ****** API Handlers ******

/**
 * Create Paid Meeting API 
 * @param {String} topic 
 * @param {String} pricePerSessionCurrency 
 * @param {Number} pricePerSession 
 * @param {Array} invitees 
 */
function createPaidMeeting(topic, pricePerSessionCurrency, pricePerSession, invitees) {
    const token = getCookie('auth_token');
    $.ajax('/api/meeting/', {
      type: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        "topic": topic,
        "price_currency": pricePerSessionCurrency,
        "price": pricePerSession,
        "invitees": invitees,
        "meeting_type": "PAID"
      }),
      success: function (data, status, xhr) {
        $('#newmeetingsuccesslink')[0].placeholder = data.meeting.meeting_link;
        showModal('newmeetingsuccess', true);
      },
      error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while Creating paid meeting', errorMessage)
      }
    });
}

/**
 * Create New Free Meeting 
 */
function getNewZoomLinkAndRoute() {
    const token = getCookie('auth_token');
    $.ajax('/api/teacher/zoom/meeting/', {
      type: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({}),
      success: function (data, status, xhr) {
        const {join_url} = data;
        openInNewTab(join_url);
      },
      error: function (jqXhr, textStatus, errorMessage) {
        showModal('zoomnotconnected', true);
        console.log('Error while Creating free meeting', errorMessage)
      }
    });
}
// ****** End of API Handlers ****** 


// ****** Event Handlers ****** 

/**
 * Connect Zoom Account Handler
 */
function handleZoomConnectAccount (event) {
  // const {redirectUri, clientId} = event.target.dataset;
  // console.log(event.target.dataset);
  // const zoomBtn = document.querySelector("#idActionBar");
  // const {redirectUri, clientId} = zoomBtn.dataset;
  // const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}`;
  const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=mAkYlnKISSCqOgSJPIxCCA&redirect_uri=https://centrestage.live/api/profile/zoom/connect`;
  openWindow(url, 'Authorize Zoom', 600, 700, 1);
}



/**
 * On Create Paid Meeting Clicked,
 */
function handleCreateFreeMeeting(event) {
  if (!isZoomLinked) {
    handleZoomConnectAccount(event);
    return;
  }
  getNewZoomLinkAndRoute()
}

/**
 * On Create Paid Meeting Clicked,
 */
function handleCreatePaidMeeting() {
    if (!isZoomLinked) {
      alert('asdasd');
    }
    let isValid = true;
    $('#topicError').hide();
    $('#pricePerSessionError').hide();
    $('#inviteesError').hide();
    const topic = $('#topic')[0].value;
    const pricePerSessionCurrency = $('#pricePerSessionCurrency')[0].value;
    const pricePerSession = $('#pricePerSession')[0].value;
    const invitees = [];
    $('.invitee-input').map((item, inviteeInput) => {
        if (inviteeInput.value) {
            invitees.push(inviteeInput.value)
        }
    });

    if (!topic) {
      $('#topicError').text('Please Provide Topic For The Meeting');
      $('#topicError').show()
      isValid = false;
    }
    if (!pricePerSessionCurrency || !pricePerSession) {
        $('#pricePerSessionError').text('Please Provide Pricing Info For The Meeting');
        $('#pricePerSessionError').show()
        isValid = false;
    }
    if (invitees.length === 0) {
        $('#inviteesError').text('Add Atleast One Invitee');
        $('#inviteesError').show()
        isValid = false;
    }
    if (isValid) {
        createPaidMeeting(topic, pricePerSessionCurrency, pricePerSession, invitees);
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

/**
 * Remove auth_token from cookies and route to main page
 */
function logout() {
  const token = getCookie('auth_token');
  $.ajax('/api/logout/', {
    type: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    success: function (data, status, xhr) {
      setCookie('auth_token', '', 0);
      setCookie('sessionid', '', 0);
      document.location.href = '/';
    },
    error: function (jqXhr, textStatus, errorMessage) {
      alert('err');
    }
  });
}

function handleOpenPaidMeeting(event) {
  if (!isZoomLinked) {
    handleZoomConnectAccount(event);
    return;
  }
  showModal('paidMeeting');
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  $('#addMoreInviteeButton').click(addMoreInvitee);
  $('#lastInviteeInput').keypress(function (e) {
    if (e.which == 13) {
      e.preventDefault();
      e.stopPropagation();
      addMoreInvitee();
    }
  });

  $('.open-zoom-connect').click(handleZoomConnectAccount);
  $('#openPaidMeetingModal').click(handleOpenPaidMeeting);
  $('#createPaidMeeting').click(handleCreatePaidMeeting);
  $('#createFreeMeeting').click(handleCreateFreeMeeting);
  $('#personalCoaching').click(() => {
    showModal('pcoatching');
  })
  $('#continuePersonalCoaching').click(() => {
    showModal('pcoatching2');
  })
  $('#personalCoachingPublish').click(() => {
    showModal('Publish2');
  })
  $('#newmeetingsuccesslinkcopy').click(() => {
    const meetingLink = $('#newmeetingsuccesslink')[0].placeholder;
    window.prompt("Copy to clipboard: Ctrl+C, Enter", meetingLink);
  })
  $('#newmeetingstartmeeting').click(() => {
    const meetingLink = $('#newmeetingsuccesslink')[0].placeholder;
    window.open(meetingLink, "_blank");
  })
  $('#openLogoutPopup').click(() => {
    showModal('logoutConfirmation');
  })
  $('#logout').click(() => logout());
}

init();