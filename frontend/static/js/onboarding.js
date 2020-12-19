(function () {

    // ****** Utilities ******

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
     * Create Teacher Profile
     * @param {String} lessonName 
     * @param {String} lessonDescription 
     * @param {String} subDomain 
     */
    function createTeacherProfile(academyName, description, subDomain) {
        const token = getCookie('auth_token');
        $.ajax('/api/teacher/profile/', {
          type: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          data: {
              "academy_name": academyName,
              "description": description,
              "subdomain": subDomain
          },
          success: function (data, status, xhr) {
            window.location.href = "/onboarding/step2";
          },
          error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while creating teacher profile', errorMessage)
            window.location.href = "/onboarding/step2";
          }
        });
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
        $('#onboardingAcademyNameError').hide()
        $('#onboardingDescriptionError').hide()
        $('#onboardingPageNameError').hide()
        const academyName = $('#onboardingAcademyName')[0].value;
        const description = $('#onboardingDescription')[0].value;
        const pageName = $('#onboardingPageName')[0].value;
        if (!academyName) {
            $('#onboardingAcademyNameError').text('Please provide academy name');
            $('#onboardingAcademyNameError').show()
            isValid = false;
        }
        if (!description) {
            $('#onboardingDescriptionError').text('Please provide description');
            $('#onboardingDescriptionError').show()
            isValid = false;
        }
        if (!pageName) {
            $('#onboardingPageNameError').text('Please provide your personal subdomain');
            $('#onboardingPageNameError').show()
            isValid = false;
        }
        if (isValid) {
            createTeacherProfile(academyName, description, pageName)
        }
    }

    /**
     * On Stage 2, proceed button clicked
     * Route to stage 3
     */
    function onProceed2ButtonClicked () {
        window.location.href = "/onboarding/step3";
    }

    /**
     * Connect Zoom Account Handler
     */
    function handleZoomConnectAccount () {
      const {clientId, redirectUri} = event.target.dataset;
      const url = `https://zoom.us/oauth/authorize?response_type=code&client_id=mAkYlnKISSCqOgSJPIxCCA&redirect_uri=${redirectUri}`;
      const token = getCookie('auth_token');
      openWindow(url, 'Authorize Zoom', 600, 700, 1);
    }

    // ****** End of Event Handlers ****** 

    function init() {
      /**
       * Init Function to add event handlers
       */
      $('#onboardingProceed').click(onProceedButtonClicked);
      $('#onboarding2Proceed').click(onProceed2ButtonClicked);
      $('#disconnectZoomAccount').click(handleZoomDisconnectAccount)
      $('#connectZoomAccount').click(handleZoomConnectAccount)
    }
  
    init();
  })();