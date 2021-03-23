// ****** Utilities ******

/**
 * Show a specific modal using modal id
 * @param {String} modalName 
 * @param {Boolean} hide 
 */
function showModal(modalName, hide) {
    hideAll();
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
    const token = getCookie('auth_token');
    $.ajax('/api/teacher/review/', {
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
            closeModal('writeReview');
        },
        error: function (jqXhr, textStatus, errorMessage) {
            // Todo: Show Error Message on UI
            console.log('Error while submitting review', errorMessage)
        }
    });
}


/**
 * On Proceed Clicked,
 * Validate Input and Go to Step 2
 */
function handleReviewSubmit() {
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



function init() {
    initializeCommon();
    initializeTeacherRating();
    $('#submitReview').click(handleReviewSubmit)
}
  
init();
