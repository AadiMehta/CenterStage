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

function handleConfirmPayment() {
  const paymentType = $('#paymentType')[0].value;
  if (paymentType) {
    $("#payment").submit();
  } else {
    $('#paymentMethodError').text('Please select payment method');
    $('#paymentMethodError').show()
    $('#paymentMethod2Error').text('Please select payment method');
    $('#paymentMethod2Error').show()
  }
}

function handlePaymentTypeSelection(event) {
  const {paymentType} = event.target.dataset;
  $('#paymentType')[0].value = paymentType;
}

// ****** Event Handlers ****** 


// ****** End of Event Handlers ****** 

function init() {
  /**
   * Init Function to add event handlers
   */
  $('#confirmPayment').click(handleConfirmPayment);
  $('.payment-type').change(handlePaymentTypeSelection);
}

init();