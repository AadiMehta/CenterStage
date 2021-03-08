
// ****** Utilities ******

/**
 * Check if Subdomain starts with alphabet and has no symbols
 * @param {String} subDomain 
 */
function validateSubdomain(subDomain) {
  return /^([a-zA-Z0-9]+[\w\-]+[a-zA-Z0-9]+)$/.test(subDomain);
}

/**
 * Debounce Method for handling Input
 * @param {Function} func 
 * @param {Number} wait 
 * @param {Boolean} immediate 
 */
function debounce(func, wait, immediate) {
  var timeout;
  return function() {
    var context = this, args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

/**
 * Read Uploaded File URL
 * @param {Element} input 
 */
function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function(e) {
      $('#profileImage').attr('src', e.target.result);
      $('#profileImageDataURl').attr('src', e.target.result);
    }
    reader.readAsDataURL(input.files[0]);
  }
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
 * Check if SubDomain is available
 * @param {Event} event 
 */
function checkSubdomainAvailability(event) {
  const subDomain = event.target.value;
  const token = getCookie('auth_token');

  if (!validateSubdomain(subDomain)) {
    $('#onboardingPageNameError').text('Minimum length of subdomain should be 3 characters and can only include \'-\' and \'_\'');
    $('#onboardingPageNameError').show()
    return;
  }

  $.ajax('/api/teacher/subdomain/availability/', {
    type: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json; charset=utf-8;'
    },
    data: JSON.stringify({
      "subdomain": subDomain
    }),
    success: function (data, status, xhr) {
      window.subdomainValid = true;
      $('#onboardingPageNameError').hide();
    },
    error: function (jqXhr, textStatus, errorMessage) {
      window.subdomainValid = false;
      $('#onboardingPageNameError').hide();
      $('#onboardingPageNameError').text('Subdomain not available');
      $('#onboardingPageNameError').show()
    }
  });
}

/**
 * Create Teacher Profile
 * @param {String} profession
 * @param {String} bio
 * @param {String} subDomain 
 */
function createTeacherProfile(profession, bio, subDomain, profileUrl) {
    const token = getCookie('auth_token');
    if (profileUrl == null) {
      $.ajax('/api/teacher/profile/', {
        type: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: JSON.stringify({
          "profession": profession,
          "bio": bio,
          "subdomain": subDomain
        }),
        success: function (data, status, xhr) {
          window.location.href = "/onboarding/accounts";
        },
        error: function (jqXhr, textStatus, errorMessage) {
          // Todo: Show Error Message on UI
          console.log('Error while creating teacher profile', errorMessage)
          // window.location.href = "/onboarding/step2";
        }
      });
    } else {
      $.ajax('/api/teacher/profile/', {
        type: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: JSON.stringify({
          "profile_image": profileUrl,
          "profession": profession,
          "bio": bio,
          "subdomain": subDomain
        }),
        success: function (data, status, xhr) {
          window.location.href = "/teacher/onboarding/accounts";
        },
        error: function (jqXhr, textStatus, errorMessage) {
          // Todo: Show Error Message on UI
          console.log('Error while creating teacher profile', errorMessage)
          // window.location.href = "/onboarding/step2";
        }
      });
    }
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

// ****** End of API Handlers ****** 


// ****** Event Handlers ****** 

/**
 * On Proceed Clicked,
 * Validate Input and Hit Create Teacher Profile API
 */
function onProceedButtonClicked () {
    let isValid = true;
    let isProfileUrl = true;
    $('#onboardingProfessionError').hide()
    $('#onboardingBioError').hide()
    $('#onboardingPageNameError').hide()
    $('#onboardingProfileImageError').hide()
    const profileUrl = $('#profileImageDataURl')[0].src;
    const profession = $('#onboardingProfession')[0].value;
    const bio = $('#onboardingBio')[0].value;
    const subDomain = $('#onboardingPageName')[0].value;
    if (profileUrl === 'data:image/jpeg;base64') {
//      $('#onboardingProfileImageError').text('Please select profile image');
//      $('#onboardingProfileImageError').show()
        isProfileUrl = false
    }
    if (!profession) {
        $('#onboardingProfessionError').text('Please provide profession name');
        $('#onboardingProfessionError').show()
        isValid = false;
    }
    if (!bio) {
        $('#onboardingBioError').text('Please provide bio');
        $('#onboardingBioError').show()
        isValid = false;
    }
    if (!subDomain && validateSubdomain(subDomain)) {
        $('#onboardingPageNameError').text('Please provide page name');
        $('#onboardingPageNameError').show()
        isValid = false;
    }
    if (isValid && window.subdomainValid) {
        if (isProfileUrl) {
            createTeacherProfile(profession, bio, subDomain, profileUrl)
        } else {
            createTeacherProfile(profession, bio, subDomain)
        }
    }
}

/**
 * On Stage 2, proceed button clicked
 * Route to stage 3
 */
function onProceed2ButtonClicked () {
    window.location.href = "/teacher/onboarding/intro-video";
}

/**
 * On Stage 3, finish button clicked
 * Route to teacher dashboard
 */
function onFinish3ButtonClicked () {
    window.location.href = "/dashboard/lessons";
}

/**
 * Connect Zoom Account Handler
 */
function handleZoomConnectAccount () {
  const {redirectUri} = event.target.dataset;
  const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=mAkYlnKISSCqOgSJPIxCCA&redirect_uri=${redirectUri}`;
  openWindow(url, 'Authorize Zoom', 600, 700, 1);
}

function openImageSelector () {
  $('#profileImageUpload').trigger('click');
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  $("#profileImageUpload").change(function() {
    readURL(this);
  });

  $('#onboardingPageName').keyup(debounce(checkSubdomainAvailability, 500));
  $('#profileImageContainer').click(openImageSelector);
  $('#onboardingProceed').click(onProceedButtonClicked);
  $('#onboarding2Proceed').click(onProceed2ButtonClicked);
  $('#onboarding3Finish').click(onFinish3ButtonClicked);
  $('#disconnectZoomAccount').click(handleZoomDisconnectAccount);
  $('#connectZoomAccount').click(handleZoomConnectAccount);
}

init();