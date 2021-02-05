
/**
 * Hide all Modals
 */
function hideAll() {
  $('.modal').map((index, modalEl) => {
      $(`#${modalEl.id}`).modal('hide');
  })
}

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
  $(`#${modalName}`).modal('toggle');
  $(`#${modalName}`).modal('hide');
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
 * Remove auth_token from cookies and route to main page
 */
function logout() {
  setCookie('auth_token', '', 0)
  document.location.href = '/';
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


/**
 * Connect Zoom Account Handler
 */
function handleZoomConnectAccount () {
  const {redirectUri} = event.target.dataset;
  const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=mAkYlnKISSCqOgSJPIxCCA&redirect_uri=${redirectUri}`;
  openWindow(url, 'Authorize Zoom', 600, 700, 1);
}

/**
 * Disconnect Zoom Account handler
 */
function handleZoomDisconnectAccount (event) {
  const token = getCookie('auth_token');
  $.ajax('/api/profile/zoom/disconnect', {
    type: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    success: function (data, status, xhr) {
      location.reload();
    },
    error: function (jqXhr, textStatus, errorMessage) {
      alert('err')
    }
  });
}

/**
 * Delete Account
 */
function handleDeleteAccount (event) {
  const token = getCookie('auth_token');
  $.ajax('/api/teacher/profile/', {
    type: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    success: function (data, status, xhr) {
      location.reload();
    },
    error: function (jqXhr, textStatus, errorMessage) {
      alert('err')
    }
  });
}

function init() {
  $('#logoutButton').click(() => showModal('logoutConfirmation'));
  $('#logout').click(() => logout());
  $('#disconnectZoomAccount').click(handleZoomDisconnectAccount);
  $('#connectZoomAccount').click(handleZoomConnectAccount);
  $('#deleteAccount').click(handleDeleteAccount);
}

init();