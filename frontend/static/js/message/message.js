let currentRecipient = '';
let chatInput = $('#chat-input');
let chatButton = $('#btn-send');
let userList = $('#user-list');
let messageList = $('#msgs');
let messageContacts = [];
let userProfileImage = "";
let recipientProfileImage = "";
let recipientName = "";

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

function updateUserList() {
    console.log("in user list");
    const token = getCookie('auth_token');
    $.ajax('/api/message/contacts/',{
      type: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
       success: function (data, status, xhr) {
        console.log(data);
        messageContacts = data;
        console.log(messageContacts);
        userList.children('.user').remove();
        for (let i = 0; i < data['active'].length; i++) {
            const date = new Date(data['active'][i]['last_message']['timestamp']).toString().substring(0,10);
            const userItem = `<li class="user contact">
                                  <div class="profimg-name">
                                    <div class="profimg-rounded"><img class="profile-pic" src=${data['active'][i]['profile']['profile_image']} alt=""></div>
                                    <div class="prof-name">
                                      <h4 class="prof-name-header">${data['active'][i]['first_name']}</h4>
                                      <span class="user-email" style="display:none">${data['active'][i]['email']}</span>
                                      <span class="user-name" style="display:none">${data['active'][i]['first_name']}</span>
                                      <span class="user-bio" style="display:none">${data['active'][i]['profile']['bio']}</span>
                                      <span class="user-image" style="display:none">${data['active'][i]['profile']['profile_image']}</span>
                                      <div class="msg-text-time">
                                        <span class="msg-text">${data['active'][i]['last_message']['body']}</span><span class="msg-time">${date}</span>
                                        </div>
                                    </div>
                                  </div>
                               </li>`
            // userItem.addEventListener('click', hide, false);
            // const userItem = `<a class="list-group-item user">${data[i]['username']}</a>`;
            $(userItem).appendTo('#user-list');
        }
        for (let i = 0; i < data['inactive'].length; i++) {
            console.log(data['inactive']);
            const userItem = `<li class="user" style="display:none">
                                  <div class="profimg-name">
                                    <div class="profimg-rounded"><img class="profile-pic" src=${data['inactive'][i]['profile']['profile_image']} alt=""></div>
                                    <div class="prof-name">
                                      <h4 class="prof-name-header">${data['inactive'][i]['first_name']}</h4>
                                      <span class="user-email" style="display:none">${data['inactive'][i]['email']}</span>
                                      <span class="user-name" style="display:none">${data['inactive'][i]['first_name']}</span>
                                      <span class="user-bio" style="display:none">${data['inactive'][i]['profile']['bio']}</span>
                                      <span class="user-image" style="display:none">${data['inactive'][i]['profile']['profile_image']}</span>
                                      <div class="msg-text-time">
                                        <span class="msg-text">${data['inactive'][i]['last_message']}</span><span class="msg-time">22:34 PM</span>
                                        </div>
                                    </div>
                                  </div>
                               </li>`
            // userItem.addEventListener('click', hide, false);
            // const userItem = `<a class="list-group-item user">${data[i]['username']}</a>`;
            $(userItem).appendTo('#user-list');
        }
        for (let i = 0; i < messageContacts.length; i++) {
           if (messageContacts[i]['email'] == currentUser){
               userProfileImage = messageContacts[i]['profile_image'];
               break;
           }
       }
        $('.user').click(function () {
            console.log("user clicked");
            userList.children('.active').removeClass('active');
            let selected = event.currentTarget;
            console.log(selected);
            $(selected).addClass('active');
            console.log(selected);
            let emailElement = selected.getElementsByClassName("user-email");
            let nameElement = selected.getElementsByClassName("user-name");
            let bioElement = selected.getElementsByClassName("user-bio");
            let profileImageElement = selected.getElementsByClassName("profile-pic");
            console.log(profileImageElement[0].src);
            setCurrentRecipient(nameElement[0].textContent,bioElement[0].textContent,emailElement[0].textContent,profileImageElement[0].src);
        });
        var userListContainer = document.getElementById('user-list');
        var firstContact = userListContainer.getElementsByClassName('user').item(0);
        firstContact.click();
    },
    error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while Creating paid meeting', errorMessage)
      }

    });
}

       

function drawMessage(message) {
    let position = 'left';
    console.log("in draw message");
    const date = new Date(message.timestamp).toString().substring(0,10);
    console.log(message.user);
    console.log(currentUser);
    // for (let a of document.getElementById('user-list').getElementsByClassName("user")) {
    //           console.log(a);
    //           let usr = a.getElementsByClassName("user-email");
    //           console.log(usr[0].textContent);
    //           if (message.user === currentUser) {
    //               if (usr[0].textContent==currentUser) {
    //                 let profile_image_element = a.getElementsByClassName("user-image");
    //                 var profile_image = profile_image_element[0].textContent;
    //                 break;
    //             }
    //         }

    //           else {
    //           if (usr[0].textContent==message.user) {
    //             let profile_name_element = a.getElementsByClassName("user-name");
    //             var profile_name = profile_name_element[0].textContent;
    //             console.log(profile_image);
    //             break;
    //         }
    //           }
    //    }
    if (message.user === currentUser) {
       // for (let i = 0; i < messageContacts.length; i++) {
       //     if (messageContacts[i]['email'] == currentUser){
       //         var profile_image = messageContacts[i]['profile_image'];
       //         break;
       //     }
       // }
       const messageItem = `<li>
                  <div class="messages-row messages-child message">
                <div class="profimg-name">
                  <div class="profimg-rounded"><img src=${userProfileImage} alt=""></div>
                  <div class="prof-name">
                    <div class="msg-activity-row">
                      <h4>You</h4> <time>${date}</time>
                    </div> 
                    
                    <div class="chat-row">
                      ${message.body}
                    </div>
                  </div>
                </div>
              </div>
              </li>`;
    // const messageItem = `
    //         <li class="message ${position}">
    //             <div class="avatar">${message.user}</div>
    //                 <div class="text_wrapper">
    //                     <div class="text">${message.body}<br>
    //                         <span class="small">${date}</span>
    //                 </div>
    //             </div>
    //         </li>`;
    $(messageItem).appendTo('#msgs');
    }
    else {
       //  for (let i = 0; i < messageContacts.length; i++) {
       //     if (messageContacts[i]['email'] == message.user){
       //         var profile_name = messageContacts[i]['name'];
       //         var profile_image = messageContacts[i]['profile_image'];
       //         break;
       //     }
       // }
        console.log("in messages");
        // const date = new Date(message.timestamp);
        const messageItem = `<li> 
                <div class="messages-row message">
                <div class="profimg-name">
                  <div class="profimg-rounded"><img src="${recipientProfileImage}" alt=""></div>
                  <div class="prof-name">
                    <div class="msg-activity-row">
                      <h4>${recipientName}</h4> <time>${date}</time>
                    </div> 
                    
                    <div class="chat-row">
                    ${message.body}
                      </div>
                  </div>
                </div>
              </div> 
              </li>`;

    $(messageItem).appendTo('#msgs');
    }


}

function getConversation(recipient) {
    console.log("in converstaion");
    $('#msgs').empty();
    const token = getCookie('auth_token');
    $.ajax(`/api/messages/message/?target=${recipient}`, {
      type: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
        success: function (data) {
        console.log("request complete");
        console.log(data);
        // $('#msgs').children('.message').remove();
        for (let i = data['results'].length - 1; i >= 0; i--) {
            drawMessage(data['results'][i]);
        }
        $('#msgs').animate({scrollTop: messageList.prop('scrollHeight')});
     },
        error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while Creating paid meeting', errorMessage)
      }
    });

}

function getMessageById(message) {
    console.log("get message id");
    const token = getCookie('auth_token');
    id = JSON.parse(message).message;
    $.ajax(`/api/messages/message/${id}/`, {
          type: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        success: function (data) {
        console.log("in getid");
        console.log(data.user);
        console.log(currentRecipient);
        console.log(currentUser);
        if (data.user === currentRecipient ||
            (data.recipient === currentRecipient && data.user == currentUser)) {
            drawMessage(data);
        }
        else {
          if (data.recipient === currentUser) {
            for (let a of document.getElementById('user-list').getElementsByClassName("user")) {
              console.log(a);
              let usr = a.getElementsByClassName("user-email");
              console.log(usr[0].textContent);
              console.log(data.user);
              if (usr[0].textContent==data.user) {
                not_count = a.getElementsByClassName("prof-name-header")[0].getElementsByClassName("notifaction-badge");
                console.log(not_count);
                if (not_count.length != 0){
                  let count = not_count[0].textContent;
                  count = parseInt(count) + 1;
                  console.log(count);
                  let countStr = `${count}`;
                  console.log(countStr);
                  not_count[0].textContent = countStr;
                }
                else {
                notification = document.createElement("span");
                notification.classList.add('notifaction-badge');
                notification.innerHTML = "1";
                a.getElementsByClassName("prof-name-header")[0].appendChild(notification);
              }
                break;
              }
            }
          }
        }
        messageList.animate({scrollTop: messageList.prop('scrollHeight')});
    },
    error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while Creating paid meeting', errorMessage)
      }
    });
}

// function sendMessage(recipient, body) {
//     const token = getCookie('auth_token');
//     $.post('/api/messages/message/', {
//         headers: {
//             'Authorization': `Bearer ${token}`,
//             'Content-Type': 'application/json'
//           },
//         recipient: recipient,
//         body: body
//     }).fail(function () {
//         alert('Error! Check console!');
//     });
// }


function sendMessage(recipient, body) {
    console.log("in send message")
    const token = getCookie('auth_token');
    $.ajax('/api/messages/message/', {
        type: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        data: JSON.stringify({recipient: recipient,
        body: body
    }),
    success: function (data) {
        console.log("success");
    },
    error: function (jqXhr, textStatus, errorMessage) {
        console.log('Error while Creating paid meeting', errorMessage)
      }
    });
}

function setCurrentRecipient(name,bio,username,profileimage) {
    console.log("in set current recp");
    console.log(profileimage);
    $("#chattitle-user").text(name);
    $("#chattitle-bio").text(bio);
    $("#chattitle-image").attr("src",profileimage);
    currentRecipient = username;
    for (let i = 0; i < messageContacts.length; i++) {
       if (messageContacts[i]['email'] == currentRecipient){
           recipientName = messageContacts[i]['name'];
           recipientProfileImage = messageContacts[i]['profile_image'];
           break;
       }
    }
    getConversation(currentRecipient);
    enableInput();
}


function enableInput() {
    chatInput.prop('disabled', false);
    chatButton.prop('disabled', false);
    chatInput.focus();
}

function disableInput() {
    chatInput.prop('disabled', true);
    chatButton.prop('disabled', true);
}

$(document).ready(function () {
    updateUserList();
    disableInput();

//    let socket = new WebSocket(`ws://127.0.0.1:8000/?session_key=${sessionKey}`);
    const token = getCookie('auth_token');
    var socket = new WebSocket(
        'ws://' + window.location.host +
        '/ws?token='+token)

    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
        if (chatInput.val().length > 0) {
            sendMessage(currentRecipient, chatInput.val());
            chatInput.val('');
        }
    });
    socket.onmessage = function (e) {
        getMessageById(e.data);
    };
    $('#search-contact').on('keyup', function() {
     if (this.value.length > 0) {
         let searchString = this.value.toUpperCase();
         console.log(searchString);
         var userListContainer = document.getElementById('user-list');
         var contacts = userListContainer.getElementsByClassName('user');
         for (i = 0; i < contacts.length; i++) {
             console.log(contacts[i].getElementsByClassName("prof-name-header")[0].textContent.toUpperCase());
             if (contacts[i].getElementsByClassName("prof-name-header")[0].textContent.toUpperCase().indexOf(searchString) > -1 ){
               contacts[i].style.display = "";
             }
             else{
               contacts[i].style.display = "none";
             }
           }
          // do search for this.value here
     }
     else {
         console.log("in search over");
         var userListContainer = document.getElementById('user-list');
         var contacts = userListContainer.getElementsByClassName('user');
         for (i=0; i < contacts.length; i++) {
             if (contacts[i].classList.contains("contact")){
               contacts[i].style.display = "";
           }
             else{
               contacts[i].style.display = "none";
             }

         }
     }
    });
});



