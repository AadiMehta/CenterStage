/**
 * Hide all Modals
 */
function hideAll() {
  $(".modal").map((index, modalEl) => {
    $(`#${modalEl.id}`).modal("hide");
  });
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
  $(`#${modalName}`).modal("toggle");
  $(`#${modalName}`).modal("show");
}

/**
 * Hide a specific modal using modal id
 * @param {String} modalName
 */
function hideModal(modalName) {
  $(`#${modalName}`).modal("toggle");
  $(`#${modalName}`).modal("hide");
}

/**
 * Set Cookie in the browser
 */
function setCookie(cname, cvalue, exMins) {
  var d = new Date();
  d.setTime(d.getTime() + exMins * 60 * 1000);
  var expires = "expires=" + d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
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
  var ca = document.cookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

/**
 * Disconnect Stripe Account handler
 */
function handleStripeDisconnectAccount(event) {
  const token = getCookie("auth_token");
  $.ajax("/api/payments/remove/", {
    type: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    data: JSON.stringify({
      payment_type: "STRIPE",
    }),
    success: function (data, status, xhr) {
      location.reload();
    },
    error: function (jqXhr, textStatus, errorMessage) {
      alert("err");
    },
  });
}

function checkInputs() {
  let isValid = true;
  // trim to remove the whitespaces
  const dob = document.querySelector("#dataOfBirth");
  const address = document.querySelector("#address");
  const city = document.querySelector("#city");
  const postalCode = document.querySelector("#postalCode");
  const state = document.querySelector("#state");
  const country = document.querySelector("#country");
  const currency = document.querySelector("#currency");
  const bankAccountNo = document.querySelector("#bankAccountNumber");
  const ifscCode = document.querySelector("#ifscCode");
  const accountHolderName = document.querySelector("#accountHolderName");
  const personalID = document.querySelector("#personalID");

  if (dob.value.trim() === "") {
    setErrorFor(dob, "Date of Birth can not be blank");
    isValid = false;
  } else {
    setSuccessFor(dob);
  }

  if (address.value.trim() === "") {
    setErrorFor(address, "addres cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(address);
  }

  if (city.value.trim() === "") {
    setErrorFor(city, "city cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(city);
  }

  if (postalCode.value.trim() === "") {
    setErrorFor(postalCode, "postalCode cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(postalCode);
  }

  if (state.value.trim() === "") {
    setErrorFor(state, "state cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(state);
  }

  if (country.value.trim() === "") {
    setErrorFor(country, "please select country");
    isValid = false;
  } else {
    setSuccessFor(country);
  }

  if (currency.value.trim() === "") {
    setErrorFor(currency, "please select country");
    isValid = false;
  } else {
    setSuccessFor(currency);
  }


  if (bankAccountNo.value.trim() === "") {
    setErrorFor(bankAccountNo, "bankAccountNo cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(bankAccountNo);
  }

  if (ifscCode.value.trim() === "") {
    setErrorFor(ifscCode, "ifscCode cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(ifscCode);
  }

  if (accountHolderName.value.trim() === "") {
    setErrorFor(accountHolderName, "accountHolderName cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(accountHolderName);
  }

  if (personalID.value.trim() === "") {
    setErrorFor(personalID, "personalID cannot be blank");
    isValid = false;
  } else {
    setSuccessFor(personalID);
  }

  return isValid;
}

function setErrorFor(input, message) {
  // const formControl = input.parentElement;
  // const small = formControl.querySelector('small');
	// formControl.className = 'form-control error';
	// small.innerText = message;
  $(".paymentAddFormError").text("* all fields are required");
  $(".paymentAddFormError").show();
}

function setSuccessFor(input) {
  // const formControl = input.parentElement;
  // formControl.className = "form-control success";
}

function onSubmitPaymentClick(event) {
  const paymentForm = $("#paymentAddForm");

  const dob = $("#dataOfBirth")[0].value;
  const address = $("#address")[0].value;
  const city = $("#city")[0].value;
  const postalCode = $("#postalCode")[0].value;
  const state = $("#state")[0].value;
  const country = $("#country")[0].value;
  const currency = $("#currency")[0].value;
  const bankAccountNo = $("#bankAccountNumber")[0].value;
  const ifscCode = $("#ifscCode")[0].value;
  const accountHolderName = $("#accountHolderName")[0].value;
  const personalID = $("#personalID")[0].value;

  const isFormValid = checkInputs();

  if (isFormValid) {
    const token = getCookie("auth_token");
    $.ajax("/api/payments/add/", {
      type: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      data: JSON.stringify({
        dob: dob,
        personalID: personalID,
        address: address,
        city: city,
        postalCode: postalCode,
        state: state,
        country: country,
        currency: currency,
        bankAccountNo: bankAccountNo,
        ifscCode: ifscCode,
        accountHolderName: accountHolderName,
      }),
      success: function (data, status, xhr) {
        document.getElementById("paymentAddForm").reset();
        console.log("payment added successfully");
        $(".paymentAddFormError").text("payment added successfully");
        $(".paymentAddFormError").show();
        hideModal("connectStipeModal");
        window.location.reload();
      },
      error: function (jqXhr, textStatus, errorMessage) {
        // Todo: Show Error Message on UI
        $(".paymentAddFormError").text("Error while adding payment account");
        $(".paymentAddFormError").show();
        console.log("Error while adding payment account", errorMessage);
      },
    });
  }
}

// birth date mask
var dateInputMask = function dateInputMask(elm) {
  elm.addEventListener("keypress", function (e) {
    if (e.keyCode < 47 || e.keyCode > 57) {
      e.preventDefault();
    }

    var len = elm.value.length;

    // If we're at a particular place, let the user type the slash
    // i.e., 12/12/1212
    if (len !== 1 || len !== 3) {
      if (e.keyCode == 47) {
        e.preventDefault();
      }
    }

    // If they don't add the slash, do it for them...
    if (len === 2) {
      elm.value += "/";
    }

    // If they don't add the slash, do it for them...
    if (len === 5) {
      elm.value += "/";
    }
  });
};

const dateInput = document.querySelector("#dataOfBirth");
dateInputMask(dateInput);

function init() {
  $("#btnSubmit").click(onSubmitPaymentClick);
  $("#stripeDisconnectConfirmed").click(handleStripeDisconnectAccount);
  $("#btnDisconnectStripe").click(() => showModal("disconnectStripeModal"));
  $("#btnConnectStripe").click(() => showModal("connectStipeModal"));
}

init();
