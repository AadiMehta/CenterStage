
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
    window.location.href = '/student/dashboard';
  }
  
  
  function init() {
    /**
     * Init Function to add event handlers
     */
    showModal('newmeeting', true);
    $('#newmeeting').on('hidden.bs.modal', function () {
      redirectToDashboard();
    })
  }
  
  init();