
/**
 * Hide all Modals
 */
function hideAll() {
  $('.modal').map((index, modalEl) => {
      $(`#${modalEl.id}`).modal('hide');
  })
}

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
  $(`#${modalName}`).modal('toggle');
  $(`#${modalName}`).modal('hide');
}  

function redirectToDashboard() {
  // var counter = 5;
  // var timeInterval = setInterval(function(){
  //     $("#redirectionMessage").text(`Redirecting to dashboard in ${counter} seconds`);
  //     counter = counter - 1;
  //     if(counter <= 0) {
  //         window.location.href = '/dashboard';
  //     }
  // }, 1000)
  window.location.href = '/dashboard/notes';
}


function init() {
  /**
   * Init Function to add event handlers
   */
  showModal('shareModal', true);
  $('#shareModal').on('hidden.bs.modal', function () {
    redirectToDashboard();
  })
  $('#startNow').click(() => {
    hideModal('shareModal');
    redirectToDashboard();
  })
}

init();