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

// ****** End of Utilities ******

// ****** API Handlers ******

// ****** End of API Handlers ****** 

function showSelectedSlots() {
  const dateSlot = $('#selectDateSlotpicker')[0].value;
  const timeSlot = $('#timeSlot')[0].value;
  const setToAllSessions = $('#check')[0].checked;
  const sessions = [];
  const timeSlots = lessonTimeSlots.replaceAll("'", '"');
  const parsedTimeSlots = JSON.parse(timeSlots);
  if (timeSlots && setToAllSessions) {
    $('#sessionWrapper').empty()
    for (var slot of parsedTimeSlots) {
      $('#sessionWrapper').append(`<div class="next-session-row">
      <button type="button" class="edit-btn"><img src="images/edit.png" alt="" /></button>
      <h5>Session ${slot[2]}</h5>
      <div class="sessionDayDate">
          <i><img src="images/time_date.png" alt="" /></i> ${slot[3]}
      </div>
      <div class="row">
          <div class="col-md-6">
              <div class="form-group">
                  <label>Start Time</label>
                  <div class="content-area">
                      ${slot[0]}
                  </div>
              </div>
          </div>
          <div class="col-md-6">
              <div class="form-group">
                  <label>End Time</label>
                  <div class="content-area">
                      ${slot[1]}
                  </div>
              </div>
          </div>
      </div>
  </div>`);
    }
  } else if (timeSlot) {
    $('#sessionWrapper').empty()
    const slot = parsedTimeSlots[Number(timeSlot) - 1];
    $('#sessionWrapper').append(`<div class="next-session-row">
      <button type="button" class="edit-btn"><img src="images/edit.png" alt="" /></button>
      <h5>Session No ${slot[2]}</h5>
      <div class="sessionDayDate">
          <i><img src="images/time_date.png" alt="" /></i> ${slot[3]}
      </div>
      <div class="row">
          <div class="col-md-6">
              <div class="form-group">
                  <label>Start Time</label>
                  <div class="content-area">
                      ${slot[0]}
                  </div>
              </div>
          </div>
          <div class="col-md-6">
              <div class="form-group">
                  <label>End Time</label>
                  <div class="content-area">
                      ${slot[1]}
                  </div>
              </div>
          </div>
      </div>
  </div>`); 
  }
}

function handleProceedBooking() {
  let isValid = true;
  $('#dateSlotError').hide();
  $('#timeSlotError').hide();
  const dateSlot = $('#selectDateSlotpicker')[0].value;
  const timeSlot = $('#timeSlot')[0].value;
  if (!dateSlot) {
    $('#dateSlotError').text('Please Select Date');
    $('#dateSlotError').show()
    isValid = false;
  }
  if (timeSlot === 'none') {
    $('#timeSlotError').text('Please Select Time Slot');
    $('#timeSlotError').show()
    isValid = false;
  }
  if (isValid) {
    showSelectedSlots();
    showModal('modal2');
  }
}

function handleConfirmBooking() {
  $("#preview").submit();
}

function handleConfirmPayment() {
  $("#payment").submit();
}

function handlePaymentTypeSelection(event) {
  console.log(event);
  const {paymentType} = event.target.dataset;
  $('#paymentType')[0].value = paymentType;
}

// ****** Event Handlers ****** 


// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  if (lessonDateSlots) {
    var array = lessonDateSlots;
    $("#selectDateSlotpicker").datepicker({
      minDate: 0,
      beforeShowDay: function(date){
        var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
        return [ array.indexOf(string) !== -1 ]
      }
    });
  }
  $('#proceedBooking').click(handleProceedBooking);
  $('#comfirmBooking').click(handleConfirmBooking);
  $('#comfirmPayment').click(handleConfirmPayment);
  $('.payment-type').change(handlePaymentTypeSelection);

}

init();