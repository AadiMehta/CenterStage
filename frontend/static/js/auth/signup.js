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
 * Enter key on password field to sign up
 * This if for sign up page
 */
document.getElementById("signUpPassword")
    .addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("signUpButton").click();
    }
});

/**
 * Signup API for new User
 * @param {String} firstName 
 * @param {String} lastName 
 * @param {Number} phoneNo 
 * @param {String} emailId 
 * @param {String} password 
 */
function signUpAPI(firstName, lastName, phoneNo, emailId, password) {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get('redirect_url');
    const userTypeParam = urlParams.get('utype') || 'CR';
    let userType = 'teacher';
    if (userTypeParam === 'ST') {
        userType = 'student';
    }

    $.ajax(`/api/${userType}/register/`, {
      type: 'POST',
      data: {
        "email": emailId,
        "password": password,
        "first_name": firstName,
        "last_name": lastName,
        "phone_no": phoneNo,
        "redirect_url": redirectUrl,
      },
      success: function (data, status, xhr) {        
        if (redirectUrl) {
          window.location.replace(redirectUrl);
        } else {
          window.location.href = '/';
        }
      },
      error: function (jqXhr, textStatus, errorMessage) {
        if (jqXhr["responseJSON"]["email"] != null) {
            $('#SignUpButtonError').text(jqXhr["responseJSON"]["email"][0])
        }
        else if (jqXhr["responseJSON"]["phone_no"] != null) {
            $('#SignUpButtonError').text(jqXhr["responseJSON"]["phone_no"][0])
        }
        else {
            $('#SignUpButtonError').text("Email/Phone no already registered!")
        }
        $('#SignUpButtonError').show()
        console.log('Error while signup: ', jqXhr)
        // hideModal('modalSignup');
      }
    });
}


/**
 * On Signup Button is Clicked
 * Validate all the required Fields
 * Show validation errors if inValid
 * If valid: Hit Signup API
 */
function onSignUpClicked (event) {
    let isValid = true;
    const urlParams = new URLSearchParams(window.location.search);

    $('#signUpFirstNameError').hide()
    $('#signUpLastNameError').hide()
    $('#signUpCountryCodeError').hide()
    $('#SignUpPhoneNumberError').hide()
    $('#SignUpEmailError').hide()
    $('#SignUpPasswordError').hide()
    const firstName = $('#signUpFirstName')[0].value;
    const lastName = $('#signUpLastName')[0].value;
    const countryCode = $('#signUpCountryCode')[0].value;
    const phoneNumber = $('#signUpPhoneNumber')[0].value;
    const emailId = $('#signUpEmail')[0].value;
    const password = $('#signUpPassword')[0].value;
    if (!firstName) {
        $('#signUpFirstNameError').text('Please provide First Name');
        $('#signUpFirstNameError').show()
        isValid = false;
    }
    if (!lastName) {
        $('#signUpLastNameError').text('Please provide Last Name');
        $('#signUpLastNameError').show()
        isValid = false;
    }
    if (countryCode === 'none') {
        $('#signUpCountryCodeError').text('Please select country code');
        $('#signUpCountryCodeError').show()
        isValid = false;
    }
    if (phoneNumber && !isPhoneNumberValid(phoneNumber)) {
        $('#SignUpPhoneNumberError').text('Please add valid phone number');
        $('#SignUpPhoneNumberError').show()
        isValid = false;
    }
    if (!emailId) {
        $('#SignUpEmailError').text('Please provide email');
        $('#SignUpEmailError').show()
        isValid = false;
    }
    if (!password) {
        $('#SignUpPasswordError').text('Please provide password');
        $('#SignUpPasswordError').show()
        isValid = false;
    }

    if (isValid) {
        signUpAPI(firstName, lastName, `${countryCode}${phoneNumber}`, emailId, password)
    }
}

// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */  
  $('#signUpButton').click(onSignUpClicked);
}

init();

