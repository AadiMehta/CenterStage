(function () {
  function openWindow(url, winName, w, h, scroll){
    /**
     * Opens Popup window as the current window as parent
     */
    LeftPosition = (screen.width) ? (screen.width-w)/2 : 0;
    TopPosition = (screen.height) ? (screen.height-h)/2 : 0;
    settings =
        'height='+h+',width='+w+',top='+TopPosition+',left='+LeftPosition+',scrollbars='+scroll+',resizable'
    window.open(url, winName, settings)
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

  function handleDisconnectAccount (event) {
    /**
     * Disconnect Zoom Account handler
     */
    const {accountType, clientId, disconnectUrl} = event.target.dataset;
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

  function handleConnectAccount (event) {
    /**
     * Connect Zoom Account Handler
     */
    const {accountType, clientId, redirectUri} = event.target.dataset;
    const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}`;
    const token = getCookie('auth_token');
    openWindow(url, 'Authorize Zoom', 600, 700, 1);
  }

  function init() {
    /**
     * Init Function to add event handlers
     */
    $('#disconnectAccount').click(handleDisconnectAccount)
    $('#connectAccount').click(handleConnectAccount)
  }

  init();
})();