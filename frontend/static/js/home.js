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
        console.log('Error while sending OTP', errorMessage)
      }
    });
}

/**
 * Signup API for new User
 * @param {String} firstName 
 * @param {String} lastName 
 * @param {Number} phoneNo 
 * @param {String} emailId 
 * @param {String} password 
 */
function signUpAPI(firstName, lastName, phoneNo, emailId, password) {
    $.ajax('/api/teacher/register/', {
      type: 'POST',
      data: {
        "email": emailId,
        "password": password,
        "first_name": firstName,
        "last_name": lastName,
        "phone_no": phoneNo
      },
      success: function (data, status, xhr) {
        setCookie("auth_token", data.token, 1);
        window.location.href = "/onboarding";
      },
      error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while signup', errorMessage)
        // hideModal('modalSignup');
      }
    });
}

/**
 * Login API
 * @param {String} emailId 
 * @param {String} password 
 */
function loginAPI(emailId, password) {
    $.ajax('/api/login/', {
      type: 'POST',
      data: {
        "username": emailId,
        "password": password
      },
      success: function (data, status, xhr) {
        setCookie("auth_token", data.token, 1);
        hideModal('modalOTP');
        hideModal('modalLogin');
        location.reload();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        alert('Error while login');
        console.log('Error while Login', errorMessage)
        hideModal('modalLogin');
      }
    });
}
// ****** End of API Handlers ****** 


// ****** Event Handlers ****** 

/**
 * On Get OTP Clicked,
 * Validate Input and Hit Send OTP API
 */
function onGetOTPClicked () {
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
    }
}

/**
 * On Verify OTP Clicked,
 * Validate Input and Hit Verify OTP API
 */
function onVerifyOTPClicked () {
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
 * On Signup Button is Clicked
 * Validate all the required Fields
 * Show validation errors if inValid
 * If valid: Hit Signup API
 */
function onSignUpClicked () {
    let isValid = true;
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

/**
 * On Login Button is Clicked
 * Validate all the required Fields
 * Show validation errors if inValid
 * If valid: Hit Login API
 */
function onSignInClicked () {
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
  $('#getOTPButton').click(onGetOTPClicked);
  $('#verifyOTPButton').click(onVerifyOTPClicked);
  $('#openSignUpButton').click(openSignupModal);
  $('#openSignInButton').click(openSignInModal);
  $('#signUpButton').click(onSignUpClicked);
  $('#signInButton').click(onSignInClicked);
  initOTPInput();
  initHomePage();
}

init();

