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
 * Check if phoneNumber is valid
 * @param {Number} phoneNumber 
 */
function isPhoneNumberValid(phoneNumber) {
    var filter = /^((\+[1-9]{1,4}[ \-]*)|(\([0-9]{2,3}\)[ \-]*)|([0-9]{2,4})[ \-]*)*?[0-9]{3,4}?[ \-]*[0-9]{3,4}?$/;
    return filter.test(phoneNumber) && phoneNumber.length === 10
}

/**
 * Set Cookie in the browser
 * @param {String} cookieName 
 * @param {String} value 
 * @param {Number} exdays 
 */
function setCookie(cookieName, value, exdays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var cookieValue = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
    document.cookie = cookieName + "=" + cookieValue;
}

// ****** End of Utilities ******

// ****** API Handlers ******

/**
 * Send OTP to Phone Number API
 * @param {Number} phoneNumber 
 */
function sendOtpAPI(phoneNumber) {
    window.sentOTPtoPhoneNumber = phoneNumber; 
    $.ajax('/api/otp/send/', {
      type: 'POST',
      data: {
          "phone_no": phoneNumber
      },
      success: function (data, status, xhr) {
        showModal('modalOTP', true);
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $('#OTPButtonError').text("Phone no. not registered with us!")
        $('#OTPButtonError').show()
        console.log('Error while sending OTP', errorMessage)
      }
    });
}

/**
 * Verify OTP 
 * @param {Number} phoneNumber 
 * @param {String, Number} otp 
 */
function verifyOtpAPI(phoneNumber, otp) {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get('redirect_url');

    $.ajax('/api/otp/verify/', {
      type: 'POST',
      data: {
        "phone_no": phoneNumber,
        "otp": otp,
        "redirect_url": redirectUrl
      },
      success: function (data, status, xhr) {
        if (redirectUrl) {
          window.location.replace(redirectUrl);
        } else {
          window.location.href = '/';
        }
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $('#otpCodeError').text("Invalid OTP entered!")
        $('#otpCodeError').show()
      }
    });
}


/**
 * Enter key on password field to log in
 * This if for sign in page
 */
document.getElementById("loginPassword")
    .addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("signInButton").click();
    }
});

/**
 * Enter key on get otp field to get otp
 * This if for sign in page
 */
document.getElementById("loginPhoneNumber")
    .addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("getOTPButton").click();
    }
});


function timer(remaining) {
  let timerOn = true;
  var m = Math.floor(remaining / 60);
  var s = remaining % 60;

  m = m < 10 ? '0' + m : m;
  s = s < 10 ? '0' + s : s;
  document.getElementById('timer').innerHTML = m + ':' + s;
  remaining -= 1;

  if(remaining >= 0 && timerOn) {
    setTimeout(function() {
        timer(remaining);
    }, 1000);
    return;
  }

  if(!timerOn) {
    // Do validate stuff here
    return;
  }

  // Do timeout stuff here
  alert('Timeout for otp');
}

/**
 * Login API
 * @param {String} emailId 
 * @param {String} password 
 */
function loginAPI(emailId, password) {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get('redirect_url');
    const userTypeParam = urlParams.get('utype') || 'CR';
    let userType = 'teacher';
    if (userTypeParam === 'ST') {
        userType = 'student';
    }

    $.ajax('/api/login/', {
      type: 'POST',
      data: {
        "user_type": userType,
        "username": emailId,
        "password": password,
        "redirect_url": redirectUrl
      },
      success: function (data, status, xhr) {
        if (redirectUrl) {
          window.location.replace(redirectUrl);
        } else {
          window.location.href = '/';
        }
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $('#SignInButtonError').text("Unable to login with given credentials. Please try again!")
        $('#SignInButtonError').show()
        console.log('Error while Login', errorMessage)
      }
    });
}
// ****** End of API Handlers ****** 


// ****** Event Handlers ****** 

/**
 * On Get OTP Clicked,
 * Validate Input and Hit Send OTP API
 */
function onGetOTPClicked (event) {
    let isValid = true;

    $('#loginCountryCodeError').hide()
    $('#loginPhoneNumberError').hide()
    const countryCode = $('#loginCountryCode')[0].value;
    const phoneNumber = $('#loginPhoneNumber')[0].value;
    if (countryCode === 'none') {
        $('#loginCountryCodeError').text('Please select country code');
        $('#loginCountryCodeError').show()
        isValid = false;
    }
    if (phoneNumber && !isPhoneNumberValid(phoneNumber)) {
        $('#loginPhoneNumberError').text('Please add valid phone number');
        $('#loginPhoneNumberError').show()
        isValid = false;
    }
    if (isValid) {
        sendOtpAPI(`${countryCode}${phoneNumber}`)
        let timerOn = true;
        timer(60);
    }
}

/**
 * On Verify OTP Clicked,
 * Validate Input and Hit Verify OTP API
 */
function onVerifyOTPClicked (event) {
    let isValid = true;

    const phoneNumber = window.sentOTPtoPhoneNumber;
    const otp = $('.otp-input').toArray().map((input) => input.value).join('');
    if (otp.length !== 6) {
        $('#otpCodeError').text('Please provide valid OTP');
        isValid = false;
    }
    if (isValid) {
        verifyOtpAPI(phoneNumber, otp);
    }
}

/**
 * On Login Button is Clicked
 * Validate all the required Fields
 * Show validation errors if inValid
 * If valid: Hit Login API
 */
function onSignInClicked (event) {
    let isValid = true;
    $('#loginEmailError').hide()
    $('#loginPasswordError').hide()
    const emailId = $('#loginEmail')[0].value;
    const password = $('#loginPassword')[0].value;
    if (!emailId) {
        $('#loginEmailError').text('Please provide email');
        $('#loginEmailError').show()
        isValid = false;
    }
    if (!password) {
        $('#loginPasswordError').text('Please provide password');
        $('#loginPasswordError').show()
        isValid = false;
    }

    if (isValid) {
        loginAPI(emailId, password)
    }
}


/**
 * Open Login Modal on bottom login text clicked
 * @param {Object} event 
 */
function openSignInModal (event) {
    event.preventDefault();
    showModal('modalLogin', true);
}

/**
 * Init OTP Input to focus on next input on 
 * key events
 */
function initOTPInput() {
    $(".otp-input").keydown(function () {
        let value = $(this).val();
        if (value.length > 1) {
            $(this).val(value[0]);
        }
    });
    $(".otp-input").keyup(function (e) {
        let value = $(this).val();
        if (value.length > 1) {
            $(this).val(value[0]);
        }
        if(e.keyCode == 8 && value.length === 0) {
            $(this).prev().focus()
        } else if (value.length === 1) {
            $(this).next().focus()
        }
    });
}


//=======Onload Popup==========//
$('.close-small-modal').click( function() {
  $(".modal-onload").toggleClass("hide-popup");
} );

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */  
  $('#signInButton').click(onSignInClicked);
  $('#getOTPButton').click(onGetOTPClicked);
  $('#verifyOTPButton').click(onVerifyOTPClicked);

  $('#finalInput').change(onVerifyOTPClicked);
  initOTPInput();
}

init();

