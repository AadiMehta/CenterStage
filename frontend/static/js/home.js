(function () {
    function setCookie(c_name, value, exdays) {
        var exdate = new Date();
        exdate.setDate(exdate.getDate() + exdays);
        var c_value = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
        document.cookie = c_name + "=" + c_value;
    }

    function sendOTP(phoneNumber) {
        window.sentOTPtoPhoneNumber = phoneNumber; 
        $.ajax('/api/otp/send/', {
          type: 'POST',
          data: {
              "phone_no": phoneNumber
          },
          success: function (data, status, xhr) {
            $('#modalOTP').modal('toggle');
            $('#modalOTP').modal('show');
          },
          error: function (jqXhr, textStatus, errorMessage) {
            console.log('Error while sending OTP', errorMessage)
          }
        });
    }    

    function verifyOTP(phoneNumber, otp) {
        $.ajax('/api/otp/verify/', {
          type: 'POST',
          data: {
            "phone_no": phoneNumber,
            "otp": otp
          },
          success: function (data, status, xhr) {
            setCookie("auth_token", data.token, 1);
            $('#modalOTP').modal('toggle');
            $('#modalOTP').modal('hide');
            $('#modalLogin').modal('hide');
          },
          error: function (jqXhr, textStatus, errorMessage) {
            console.log('Error while sending OTP', errorMessage)
          }
        });
    }    


    function isPhoneNumberValid(phoneNumber) {
        var filter = /^((\+[1-9]{1,4}[ \-]*)|(\([0-9]{2,3}\)[ \-]*)|([0-9]{2,4})[ \-]*)*?[0-9]{3,4}?[ \-]*[0-9]{3,4}?$/;
        return filter.test(phoneNumber)
    }

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
            sendOTP(`${countryCode}${phoneNumber}`)
        }
    }

    function onVerifyOTPClicked () {
        let isValid = true;
        const phoneNumber = window.sentOTPtoPhoneNumber;
        const otp = $('.otp-input').toArray().map((input) => input.value).join('');
        if (otp.length !== 6) {
            $('#otpCodeError').text('Please provide valid OTP');
            isValid = false;
        }
        if (isValid) {
            verifyOTP(phoneNumber, otp);
        }
    }

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

    function init() {
      /**
       * Init Function to add event handlers
       */
      $('#getOTPButton').click(onGetOTPClicked);
      $('#verifyOTPButton').click(onVerifyOTPClicked);
      initOTPInput()
    }
  
    init();
  })();