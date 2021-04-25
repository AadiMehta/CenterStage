function loadDoc() {
  
    setInterval(function(){
      const token = getCookie('auth_token');
      console.log("in count");
      $.ajax('api/notification_count', {
      type: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8;'
      },
      success: function (data, status, xhr) {
        console.log("success")
        console.log(data.count)
        document.getElementById("notificationCount").textContent = data.count;
      },
      error: function (jqXhr, textStatus, errorMessage) {
       
      }
  });},1000);
}
// loadDoc();