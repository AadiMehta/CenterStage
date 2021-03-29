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

function getClassName(userType, className) {
  if (userType === 'student') {
    return `#${userType}${className}`
  }
  return `#${className}`;
}

// ****** End of Utilities ******

// ****** API Handlers ******

/**
 * Send OTP to Phone Number API
 * @param {Number} phoneNumber 
 */
function sendOtpAPI(userType, phoneNumber) {
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
        $(getClassName(userType, 'OTPButtonError')).text("Phone no. not registered with us!")
        $(getClassName(userType, 'OTPButtonError')).show()
        console.log('Error while sending OTP', errorMessage)
      }
    });
}

/**
 * Verify OTP 
 * @param {Number} phoneNumber 
 * @param {String, Number} otp 
 */
function verifyOtpAPI(userType, phoneNumber, otp) {
    $.ajax('/api/otp/verify/', {
      type: 'POST',
      data: {
        "phone_no": phoneNumber,
        "otp": otp
      },
      success: function (data, status, xhr) {
        setCookie("auth_token", data.token, 1);
        hideModal('modalOTP');
        hideModal('modalLogin');
        location.reload();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $(getClassName(userType, 'otpCodeError')).text("Invalid OTP entered!")
        $(getClassName(userType, 'otpCodeError')).show()
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

/**
 * Signup API for new User
 * @param {String} firstName 
 * @param {String} lastName 
 * @param {Number} phoneNo 
 * @param {String} emailId 
 * @param {String} password 
 */
function signUpAPI(userType, firstName, lastName, phoneNo, emailId, password) {
    $.ajax(`/api/${userType}/register/`, {
      type: 'POST',
      data: {
        "email": emailId,
        "password": password,
        "first_name": firstName,
        "last_name": lastName,
        "phone_no": phoneNo
      },
      success: function (data, status, xhr) {
        if (userType === 'student') {
          window.location.href = "/student/onboarding";
        } else {
          window.location.href = "/teacher/onboarding";
        }
      },
      error: function (jqXhr, textStatus, errorMessage) {
        if (jqXhr["responseJSON"]["email"] != null) {
            $(getClassName(userType, 'SignUpButtonError')).text(jqXhr["responseJSON"]["email"][0])
        }
        else if (jqXhr["responseJSON"]["phone_no"] != null) {
            $(getClassName(userType, 'SignUpButtonError')).text(jqXhr["responseJSON"]["phone_no"][0])
        }
        else {
            $(getClassName(userType, 'SignUpButtonError')).text("Email/Phone no already registered!")
        }
        $(getClassName(userType, 'SignUpButtonError')).show()
        console.log('Error while signup: ', jqXhr)
        // hideModal('modalSignup');
      }
    });
}

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
function loginAPI(userType, emailId, password) {
    $.ajax('/api/login/', {
      type: 'POST',
      data: {
        "user_type": userType,
        "username": emailId,
        "password": password
      },
      success: function (data, status, xhr) {
        hideModal('modalOTP');
        hideModal('modalLogin');
        location.reload();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $(getClassName(userType, 'SignInButtonError')).text("Unable to login with given credentials. Please try again!")
        $(getClassName(userType, 'SignInButtonError')).show()
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
    let { userType } = event.target.dataset;
    if (!userType) {
      userType = 'teacher'
    }

    $(getClassName(userType, 'loginCountryCodeError')).hide()
    $(getClassName(userType, 'loginPhoneNumberError')).hide()
    const countryCode = $(getClassName(userType, 'loginCountryCode'))[0].value;
    const phoneNumber = $(getClassName(userType, 'loginPhoneNumber'))[0].value;
    if (countryCode === 'none') {
        $(getClassName(userType, 'loginCountryCodeError')).text('Please select country code');
        $(getClassName(userType, 'loginCountryCodeError')).show()
        isValid = false;
    }
    if (phoneNumber && !isPhoneNumberValid(phoneNumber)) {
        $(getClassName(userType, 'loginPhoneNumberError')).text('Please add valid phone number');
        $(getClassName(userType, 'loginPhoneNumberError')).show()
        isValid = false;
    }
    if (isValid) {
        sendOtpAPI(userType, `${countryCode}${phoneNumber}`)
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
    let { userType } = event.target.dataset;
    if (!userType) {
      userType = 'teacher'
    }

    const phoneNumber = window.sentOTPtoPhoneNumber;
    const otp = $('.otp-input').toArray().map((input) => input.value).join('');
    if (otp.length !== 6) {
        $(getClassName(userType, 'otpCodeError')).text('Please provide valid OTP');
        isValid = false;
    }
    if (isValid) {
        verifyOtpAPI(userType, phoneNumber, otp);
    }
}

/**
 * On Signup Button is Clicked
 * Validate all the required Fields
 * Show validation errors if inValid
 * If valid: Hit Signup API
 */
function onSignUpClicked (event) {
    let isValid = true;
    let { userType } = event.target.dataset;
    if (!userType) {
      userType = 'teacher'
    }

    $(getClassName(userType, 'signUpFirstNameError')).hide()
    $(getClassName(userType, 'signUpLastNameError')).hide()
    $(getClassName(userType, 'signUpCountryCodeError')).hide()
    $(getClassName(userType, 'SignUpPhoneNumberError')).hide()
    $(getClassName(userType, 'SignUpEmailError')).hide()
    $(getClassName(userType, 'SignUpPasswordError')).hide()
    const firstName = $(getClassName(userType, 'signUpFirstName'))[0].value;
    const lastName = $(getClassName(userType, 'signUpLastName'))[0].value;
    const countryCode = $(getClassName(userType, 'signUpCountryCode'))[0].value;
    const phoneNumber = $(getClassName(userType, 'signUpPhoneNumber'))[0].value;
    const emailId = $(getClassName(userType, 'signUpEmail'))[0].value;
    const password = $(getClassName(userType, 'signUpPassword'))[0].value;
    if (!firstName) {
        $(getClassName(userType, 'signUpFirstNameError')).text('Please provide First Name');
        $(getClassName(userType, 'signUpFirstNameError')).show()
        isValid = false;
    }
    if (!lastName) {
        $(getClassName(userType, 'signUpLastNameError')).text('Please provide Last Name');
        $(getClassName(userType, 'signUpLastNameError')).show()
        isValid = false;
    }
    if (countryCode === 'none') {
        $(getClassName(userType, 'signUpCountryCodeError')).text('Please select country code');
        $(getClassName(userType, 'signUpCountryCodeError')).show()
        isValid = false;
    }
    if (phoneNumber && !isPhoneNumberValid(phoneNumber)) {
        $(getClassName(userType, 'SignUpPhoneNumberError')).text('Please add valid phone number');
        $(getClassName(userType, 'SignUpPhoneNumberError')).show()
        isValid = false;
    }
    if (!emailId) {
        $(getClassName(userType, 'SignUpEmailError')).text('Please provide email');
        $(getClassName(userType, 'SignUpEmailError')).show()
        isValid = false;
    }
    if (!password) {
        $(getClassName(userType, 'SignUpPasswordError')).text('Please provide password');
        $(getClassName(userType, 'SignUpPasswordError')).show()
        isValid = false;
    }

    if (isValid) {
        signUpAPI(userType, firstName, lastName, `${countryCode}${phoneNumber}`, emailId, password)
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
    let { userType } = event.target.dataset;
    if (!userType) {
      userType = 'teacher'
    }

    $(getClassName(userType, 'loginEmailError')).hide()
    $(getClassName(userType, 'loginPasswordError')).hide()
    const emailId = $(getClassName(userType, 'loginEmail'))[0].value;
    const password = $(getClassName(userType, 'loginPassword'))[0].value;
    if (!emailId) {
        $(getClassName(userType, 'loginEmailError')).text('Please provide email');
        $(getClassName(userType, 'loginEmailError')).show()
        isValid = false;
    }
    if (!password) {
        $(getClassName(userType, 'loginPasswordError')).text('Please provide password');
        $(getClassName(userType, 'loginPasswordError')).show()
        isValid = false;
    }

    if (isValid) {
        loginAPI(userType, emailId, password)
    }
}

/**
 * Open SignUp Modal on bottom signup text clicked
 * @param {Object} event 
 */
function openSignupModal (event) {
    event.preventDefault();
    showModal('modalSignup', true);
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
 * Open SignUp Modal on bottom signup text clicked
 * @param {Object} event 
 */
function openStudentSignupModal (event) {
  event.preventDefault();
  showModal('modalStudentSignup', true);
}

/**
* Open Login Modal on bottom login text clicked
* @param {Object} event 
*/
function openStudentSignInModal (event) {
  event.preventDefault();
  showModal('modalStudentLogin', true);
}

/**
 * Init OTP Input to focus on next input on 
 * key events
 */
function initOTPInput() {
    $(".otp-input").keydown(function () {
        let value = $(this).val();
        console.log('keydown', value.length > 1)
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


function initHomePage () {
  $(window).on('load', function(){
    // Please run it with window.onload, not with document.ready
    initSmoothScrolling('.block','smoothscroll');
  });
  
  function initSmoothScrolling(container,animation){
    /*
     * @param {String} container Class or ID of the animation container
     * @param {String} animation Name of the animation, e.g. smoothscroll
     */
     var sliderWidth = 0;	
     var animationWidth = 0;	
     var sliderHeight = $('>div>div:first-of-type',container).outerHeight(false);
   
     $('>div>div', container).each(function(){				
       animationWidth += $(this).outerWidth(false);		
     });
     
     // detect number of visible slides
     var slidesVisible = $(container).width() / $('>div>div:first-of-type',container).outerWidth(false);	
     slidesVisible = Math.ceil(slidesVisible);
   
     // count slides to determine animation speed
     var slidesNumber = $('>div>div', container).length;
     var speed = slidesNumber*2;
     
   // append the tail	
     $('>div>div',container).slice(0,slidesVisible).clone().appendTo($('>div',container));	
   
     // Detect the slider width with appended tail
     $('>div>div', container).each(function(){
       sliderWidth += $(this).outerWidth(false);
     });
   
     // set slider dimensions
     $('>div',container).css({'width':sliderWidth,'height':sliderHeight});
     
   // Insert styles to html
     $("<style type='text/css'>@keyframes "+animation+" { 0% { margin-left: 0px; } 100% { margin-left: -"+animationWidth+"px; } } "+$('>div>div:first-of-type',container).selector+" { -webkit-animation: "+animation+" "+speed+"s linear infinite; -moz-animation: "+animation+" "+speed+"s linear infinite; -ms-animation: "+animation+" "+speed+"s linear infinite; -o-animation: "+animation+" "+speed+"s linear infinite; animation: "+animation+" "+speed+"s linear infinite; }</style>").appendTo("head");	
   
     // restart the animation (e.g. for safari & ie)	
     var cl = $(container).attr("class");
     $(container).removeClass(cl).animate({'nothing':null}, 1, function () {
       $(this).addClass(cl);
     });
  }
  
  // Cache selectors
  var lastId,
  topMenu = $(".navbar-nav"),
  topMenuHeight = topMenu.outerHeight()+1,
  // All list items
  menuItems = topMenu.find("a"),
  // Anchors corresponding to menu items
  scrollItems = menuItems.map(function(){
      var item = $($(this).attr("href"));
      if (item.length) { return item; }
  });
     
  // Bind click handler to menu items
  // so we can get a fancy scroll animation
  menuItems.click(function(e){
    var href = $(this).attr("href"),
        offsetTop = href === "#" ? 0 : $(href).offset().top-topMenuHeight+1;
    $('html, body').stop().animate({ 
        scrollTop: offsetTop
    }, 1000);
    e.preventDefault();
  });
    
  // Bind to scroll
  $(window).scroll(function(){
    // Get container scroll position
    var fromTop = $(this).scrollTop()+topMenuHeight;
    
    // Get id of current scroll item
    var cur = scrollItems.map(function(){
      if ($(this).offset().top < fromTop)
        return this;
    });
    // Get the id of the current element
    cur = cur[cur.length-1];
    var id = cur && cur.length ? cur[0].id : "";
    
    if (lastId !== id) {
        lastId = id;
        // Set/remove active class
        menuItems
          .parent().removeClass("active")
          .end().filter("[href=#"+id+"]").parent().addClass("active");
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
  $('#startTeachingSignUp').click(openSignupModal);
  $('#startTeachingSignUp1').click(openSignupModal);
  $('#startTeachingSignUp2').click(openSignupModal);
  $('#startTeachingSignUp3').click(openSignupModal);
  
  $('#openSignUpButton').click(openSignupModal);
  $('#openSignInButton').click(openSignInModal);
  $('#signUpButton').click(onSignUpClicked);
  $('#signInButton').click(onSignInClicked);
  $('#getOTPButton').click(onGetOTPClicked);
  $('#verifyOTPButton').click(onVerifyOTPClicked);

  $('#openStudentSignUpButton').click(openStudentSignupModal);
  $('#openStudentSignInButton').click(openStudentSignInModal);
  $('#studentSignUpButton').click(onSignUpClicked);
  $('#studentSignInButton').click(onSignInClicked);
  $('#studentGetOTPButton').click(onGetOTPClicked);
  $('#studentVerifyOTPButton').click(onVerifyOTPClicked);

  $('#finalInput').change(onVerifyOTPClicked);
  initOTPInput();
  initHomePage();
}

init();

