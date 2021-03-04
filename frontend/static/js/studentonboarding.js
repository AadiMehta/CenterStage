
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
   * Create Student Profile
   * @param {String} bio
   */
  function createStudentProfile(bio, profileUrl) {
      const token = getCookie('auth_token');
      if (profileUrl == null) {
        $.ajax('/api/student/profile/', {
          type: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: JSON.stringify({
            "bio": bio,
          }),
          success: function (data, status, xhr) {
            window.location.href = "/dashboard";
          },
          error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while creating teacher profile', errorMessage)
          }
        });
      } else {
        $.ajax('/api/student/profile/', {
          type: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: JSON.stringify({
            "profile_image": profileUrl,
            "bio": bio,
          }),
          success: function (data, status, xhr) {
            window.location.href = "/dashboard";
          },
          error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while creating teacher profile', errorMessage)
          }
        });
      }
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
      $('#onboardingBioError').hide()
      $('#onboardingProfileImageError').hide()
      const profileUrl = $('#profileImageDataURl')[0].src;
      const bio = $('#onboardingBio')[0].value;
      if (profileUrl === 'data:image/jpeg;base64') {
  //      $('#onboardingProfileImageError').text('Please select profile image');
  //      $('#onboardingProfileImageError').show()
          isProfileUrl = false
      }
      if (!bio) {
          $('#onboardingBioError').text('Please provide bio');
          $('#onboardingBioError').show()
          isValid = false;
      }
      if (isValid) {
          if (isProfileUrl) {
              createStudentProfile(bio, profileUrl)
          } else {
              createStudentProfile(bio)
          }
      }
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
  
    $('#profileImageContainer').click(openImageSelector);
    $('#onboardingProceed').click(onProceedButtonClicked);
  }
  
  init();