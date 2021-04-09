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

function routeToLoginIfNotLoggedIn() {
    if (!isUserLoggedIn()) {
        window.location.href = `/login?redirect_url=${window.location.href}&utype=ST`
    }
}

function onLoginRoute() {
    if (window.lessonUrl) {
        window.location.href = window.lessonUrl + '?rurl=' + window.lessonUrl;
        window.lessonUrl = null;
    } else if (window.callbackFunction && window.callbackParams) {
        if (window.callbackFunction.name === 'submitTeacherReview') {
            const {review, rate, recommendations} = window.callbackParams;
            window.callbackFunction(review, rate, recommendations);
        } else {
            window.callbackFunction(window.callbackParams.event);
        }
        window.callbackFunction = null;
        window.callbackParams = null;
    } else {
        window.location.href = window.location.href + '?rurl=' + window.location.href;
    }
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
    document.cookie = cookieName + "=" + cookieValue + `;domain=${sessionCookieDomain};path=/;secure`;
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

function isUserLoggedIn() {
    const token = getCookie('auth_token');
    return Boolean(token);
}

function openInNewTab(url) {
    window.open(url, '_blank').focus();
}
/*** End of Utilities *****/

function initializeCommon() {
    $('.sidebar-toggle').click( function() {
        $(".wrapper-main").toggleClass("sidebar-collapse");
    } );

    $('.close-btn').click( function() {
        $(".wrapper-main").toggleClass("sidebar-collapse");
    } );

    $('.videoButton').click( function() {
        $(".add-video-link").toggleClass("show");
    } );


    $('.video-slide .owl-carousel').owlCarousel({
        loop:true,
        margin:50,
        nav:true,
        responsive:{
            0:{
                items:1
            },

            1000:{
                items:2
            }
        }
    })

    $('.lessions-slide-wrap .owl-carousel').owlCarousel({
        loop:true,
        margin:20,
        nav:true,
        responsive:{
            0:{
                items:1
            },
            991:{
                items:2
            },
            1280:{
                items:3
            }
        }
    })
}

function initializeTeacherRating() {
    $("#teacherstar1").hover(function() {
        $('#teacherstar1')[0].src = ratingFilled;
        $('#teacherstar2')[0].src = ratingBlank;
        $('#teacherstar3')[0].src = ratingBlank;
        $('#teacherstar4')[0].src = ratingBlank;
        $('#teacherstar5')[0].src = ratingBlank;
        $('#rating')[0].value = 1;
    });
    $("#teacherstar2").hover(function() {  
        $('#teacherstar1')[0].src = ratingFilled;
        $('#teacherstar2')[0].src = ratingFilled;
        $('#teacherstar3')[0].src = ratingBlank;
        $('#teacherstar4')[0].src = ratingBlank;
        $('#teacherstar5')[0].src = ratingBlank;
        $('#rating')[0].value = 2;
    });
    $("#teacherstar3").hover(function() {  
        $('#teacherstar1')[0].src = ratingFilled;
        $('#teacherstar2')[0].src = ratingFilled;
        $('#teacherstar3')[0].src = ratingFilled;
        $('#teacherstar4')[0].src = ratingBlank;
        $('#teacherstar5')[0].src = ratingBlank;
        $('#rating')[0].value = 3;
    });
    $("#teacherstar4").hover(function() {  
        $('#teacherstar1')[0].src = ratingFilled;
        $('#teacherstar2')[0].src = ratingFilled;
        $('#teacherstar3')[0].src = ratingFilled;
        $('#teacherstar4')[0].src = ratingFilled;
        $('#teacherstar5')[0].src = ratingBlank;
        $('#rating')[0].value = 4;
    });
    $("#teacherstar5").hover(function() {  
        $('#teacherstar1')[0].src = ratingFilled;
        $('#teacherstar2')[0].src = ratingFilled;
        $('#teacherstar3')[0].src = ratingFilled;
        $('#teacherstar4')[0].src = ratingFilled;
        $('#teacherstar5')[0].src = ratingFilled;
        $('#rating')[0].value = 5;
    });
}


/**
 * Submit Teacher Review API
 * @param {*} review 
 * @param {*} rate 
 * @param {*} recommendations 
 */
function submitTeacherReview(review, rate, recommendations) {
    routeToLoginIfNotLoggedIn();
    const token = getCookie('auth_token');
    $.ajax(`${baseUrl}/api/teacher/review/`, {
        type: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            "review": review,
            "rate": rate,
            "recommendations": recommendations,
            "teacher_id": teacherId,
        }),
        success: function (data, status, xhr) {
            hideModal('writeReview');
            window.location.reload();
        },
        error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while submitting review', errorMessage)
        }
    });
}


function recommendTeacher(event) {
    routeToLoginIfNotLoggedIn();
    const {recomType} = event.target.dataset;
    const recomTypeCountEl = $(`#${recomType}_COUNT`);
    let {recomCount} = recomTypeCountEl[0].dataset;
    recomCount = Number(recomCount || 0);
    const token = getCookie('auth_token');
    $.ajax(`${baseUrl}/api/teacher/recommend/`, {
        type: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            "teacher_id": teacherId,
            "recommendation_type": recomType
        }),
        success: function (data, status, xhr) {
            if (data.action === 'removed') {
                event.target.innerText = 'Recommend'
                recomCount -= 1;
            } else {
                event.target.innerText = 'Recommended'
                recomCount += 1;
            }
            recomTypeCountEl.attr(`data-recom-count`, recomCount);
            recomTypeCountEl.text(`(${recomCount} Recommendations)`);
        },
        error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while submitting recommendation', errorMessage)
        }
    });
}

function handleFollowTeacher(event) {
    restrictWithoutLogin()
    const token = getCookie('auth_token');
    $.ajax(`${baseUrl}/api/teacher/follow/`, {
        type: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            "teacher_id": teacherId,
        }),
        success: function (data, status, xhr) {
            if (data.action === 'removed') {
                event.target.innerText = 'Follow'
            } else {
                event.target.innerText = 'Followed'
            }
        },
        error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while follow api', errorMessage)
        }
    });
}

function handleLikeTeacher(event) {
    routeToLoginIfNotLoggedIn();
    const token = getCookie('auth_token');
    $.ajax(`${baseUrl}/api/teacher/like/`, {
        type: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            "teacher_id": teacherId,
        }),
        success: function (data, status, xhr) {
            console.log(event.target)
            if (data.action === 'removed') {
                $('#likeTeacherTempText').text('Like');
            } else {
                $('#likeTeacherTempText').text('Liked');
            }
        },
        error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while like api', errorMessage)
        }
    });
}

/**
 * On Proceed Clicked,
 * Validate Input and Go to Step 2
 */
function handleReviewSubmit(event) {
    routeToLoginIfNotLoggedIn();
    let isValid = true;
    $('#ratingError').hide();
    $('#reviewError').hide();
    const rating = $('#rating')[0].value;
    const review = $('#review')[0].value;
    const recommendations = [];
    if ($('#lessonQuality')[0].checked) {
        recommendations.push('LESSON_QUALITY')
    }
    if ($('#lessonContent')[0].checked) {
        recommendations.push('LESSON_CONTENT')
    }
    if ($('#lessonStructure')[0].checked) {
        recommendations.push('LESSON_STRUCTURE')
    }
    if ($('#teacherHelpfulness')[0].checked) {
        recommendations.push('TEACHER_HELPFULNESS')
    }
    if ($('#teacherCommunication')[0].checked) {
        recommendations.push('TEACHER_COMMUNICATION')
    }
    if ($('#teacherKnowledge')[0].checked) {
        recommendations.push('TEACHER_KNOWLEDGE')
    }
      
    if (!rating) {
      $('#ratingError').text('Please Provide Rating');
      $('#ratingError').show()
      isValid = false;
    }
    if (!review) {
        $('#reviewError').text('Please Provide Review');
        $('#reviewError').show()
        isValid = false;
    }
    if (isValid) {
        submitTeacherReview(review, rating, recommendations);
    }
}

function handleViewAllReviews(event) {
    const {shown} = event.target.dataset;
    const isShown = shown === 'true';
    if (isShown) {
        $('.view-all-reviews').hide();
        $('#viewAllReviews').attr("data-shown","false");
    } else {
        $('.view-all-reviews').show();
        $('#viewAllReviews').attr("data-shown","true");
    }
}

function handleBookLesson(event) {
    const {lessonUrl} = event.target.dataset;
    routeToLoginIfNotLoggedIn()
    openInNewTab(lessonUrl);
}


function getClassName(userType, className) {
    return `#${className}`;
}

// ****** API Handlers ******

/**
 * Send OTP to Phone Number API
 * @param {Number} phoneNumber 
 */
function sendOtpAPI(userType, phoneNumber) {
    window.sentOTPtoPhoneNumber = phoneNumber; 
    $.ajax(`${baseUrl}/api/otp/send/`, {
      type: 'POST',
      data: {
          "phone_no": phoneNumber
      },
      success: function (data, status, xhr) {
        hideAll();
        showModal('modalOTPTeacherPage', true);
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
    $.ajax(`${baseUrl}/api/otp/verify/`, {
      type: 'POST',
      data: {
        "phone_no": phoneNumber,
        "otp": otp
      },
      success: function (data, status, xhr) {
        hideModal('modalOTPTeacherPage');
        hideModal('modalLoginTeacherPage');
        onLoginRoute();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $(getClassName(userType, 'otpCodeError')).text("Invalid OTP entered!")
        $(getClassName(userType, 'otpCodeError')).show()
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
function signUpAPI(userType, firstName, lastName, phoneNo, emailId, password) {
    $.ajax(`${baseUrl}/api/${userType}/register/`, {
      type: 'POST',
      data: {
        "email": emailId,
        "password": password,
        "first_name": firstName,
        "last_name": lastName,
        "phone_no": phoneNo
      },
      success: function (data, status, xhr) {
        hideModal('modalSignupTeacherPage');
        onLoginRoute();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        $(getClassName(userType, 'SignUpButtonError')).text("Email/Phone no already registered!")
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
    $.ajax(`${baseUrl}/api/login/`, {
      type: 'POST',
      data: {
        "user_type": userType,
        "username": emailId,
        "password": password
      },
      success: function (data, status, xhr) {
        hideModal('modalOTPTeacherPage');
        hideModal('modalLoginTeacherPage');
        onLoginRoute();
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
      userType = 'student'
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
      userType = 'student'
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
    let userType = 'student';

    console.log(userType);
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
    let userType = 'student';

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
    hideAll();
    $('#modalLoginTeacherPage').on('hidden.bs.modal', function () {
        showModal('modalSignupTeacherPage');
    });
}

/**
 * Open Login Modal on bottom login text clicked
 * @param {Object} event 
 */
function openSignInModal (event) {
    event.preventDefault();
    hideAll();
    $('#modalSignupTeacherPage').on('hidden.bs.modal', function () {
        showModal('modalLoginTeacherPage');
    });
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

//=======Onload Popup==========//
$('.close-small-modal').click( function() {
    $(".modal-onload").toggleClass("hide-popup");
});

function init() {
    initOTPInput();
    initializeCommon();
    initializeTeacherRating();
    $('#submitReview').click(handleReviewSubmit)
    $('.recommend-teacher').click(recommendTeacher)
    $('#viewAllReviews').click(handleViewAllReviews)
    $('#followTeacher').click(handleFollowTeacher)
    $('#likeTeacher').click(handleLikeTeacher)
    $('.book-lesson').click(handleBookLesson)

    $('#openSignUpButton').click(openSignupModal);
    $('#openSignInButton').click(openSignInModal);
    $('#signUpButton').click(onSignUpClicked);
    $('#signInButton').click(onSignInClicked);
    $('#getOTPButton').click(onGetOTPClicked);
    $('#verifyOTPButton').click(onVerifyOTPClicked);
  
    $('#finalInput').change(onVerifyOTPClicked);
}
  
init();

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
