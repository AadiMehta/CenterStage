
// ****** Utilities ******

  /**
   * Check if Subdomain starts with alphabet and has no symbols
   * @param {String} subDomain 
   */
  function validateSubdomain(subDomain) {
    return /^[a-zA-Z]*/.test(subDomain) && !/[!@#$%^&*()_+]/.test(subDomain);
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
  

  function goToLessonSchedule(lessonName, lessonDescription, lessonNoOfParticipants, lessonLanguage, lessonType) {
      const token = getCookie('auth_token');
      const csrftoken = getCookie('csrftoken');
      $.ajax('/lesson/schedule', {
        type: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({
          "lesson_name": lessonName,
          "lesson_description": lessonDescription,
          "lesson_no_of_participants": lessonNoOfParticipants,
          "lesson_language": lessonLanguage,
          "lesson_type": lessonType
        }),
        success: function (data, status, xhr) {
          // setCookie("__cld_key", data.cached_key, 1);
          // window.location.href = "/lesson/schedule";
        },
      });
  }
  
  // ****** End of API Handlers ****** 
  
  
  // ****** Event Handlers ****** 
  
  /**
   * On Proceed Clicked,
   * Validate Input and Go to Step 2
   */
  function handleLCS1Proceed() {
      let isValid = true;
      $('#lessonNameError').hide();
      $('#lessonDescriptionError').hide();
      $('#lessonNoOfParticipantsError').hide();
      $('#lessonLanguageError').hide();
      $('#lessonTypeError').hide();
      const lessonName = $('#lessonName')[0].value;
      const lessonDescription = $('#lessonDescription')[0].value;
      const lessonNoOfParticipants = $('#lessonNoOfParticipants')[0].value;
      const lessonLanguage = $('#lessonLanguage')[0].value;
      const lessonType = $('#lessonType .selected')[0].dataset.lessonType;
      if (!lessonName) {
        $('#lessonNameError').text('Please Provide Lesson Name');
        $('#lessonNameError').show()
        isValid = false;
      }
      if (!lessonDescription) {
        $('#lessonDescriptionError').text('Please Provide Lesson Description');
        $('#lessonDescriptionError').show()
        isValid = false;
      }
      if (lessonNoOfParticipants === 'none') {
        $('#lessonNoOfParticipantsError').text('Please Select Number of participants');
        $('#lessonNoOfParticipantsError').show()
        isValid = false;
      }
      if (lessonLanguage === 'none') {
        $('#lessonLanguageError').text('Please Select Lesson Language');
        $('#lessonLanguageError').show()
        isValid = false;
      }
      if (!lessonType) {
        $('#lessonLanguageError').text('Please Select Lesson Type');
        $('#lessonLanguageError').show()
        isValid = false;
      }
      if (isValid) {
        //goToLessonSchedule(lessonName, lessonDescription, lessonNoOfParticipants, lessonLanguage, lessonType);
        // Go to Step 2
        $("#step1").submit();
      }
  }

  function handleLCS2Proceed() {
    $("#step2").submit();
  }

  function handleLCS3Proceed() {
    $("#step3").submit();
  }

  function handleLCS4Proceed() {
    $("#step4").submit();
  }

  function handleLessonTypeSelect(event) {
    $('#singleSession').removeClass('selected');
    $('#multiSession').removeClass('selected');
    $('#ongoingSession').removeClass('selected');
    $(event.target).addClass('selected');
    $("#no_of_sessions").val(event.currentTarget.dataset.lessonType);
  }

  function handleLessonTimeSlotTypeSelect(event) {
    $("#flexible-time-slot").removeClass('selected');
    $("#fixed-time-slot").removeClass('selected');
    $(event.target).addClass('selected');
    $("#slot_type").val(event.currentTarget.dataset.slotType);
  }
  // ****** End of Event Handlers ****** 
  
  function init() {
    /**
     * Init Function to add event handlers
     */
  
    $('#lcs1Proceed').click(handleLCS1Proceed);
    $('#singleSession').click(handleLessonTypeSelect);
    $('#multiSession').click(handleLessonTypeSelect);
    $('#ongoingSession').click(handleLessonTypeSelect);

    /*
        Step2 Time Slot Selection
    */
    $('#lcs2Proceed').click(handleLCS2Proceed);
    $('#flexible-time-slot').click(handleLessonTimeSlotTypeSelect);
    $('#fixed-time-slot').click(handleLessonTimeSlotTypeSelect);

    $('#lcs3Proceed').click(handleLCS3Proceed);
    $('#lcs4Proceed').click(handleLCS4Proceed);
  }
  
  init();