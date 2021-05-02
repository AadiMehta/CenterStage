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

const token = getCookie("auth_token");

// ****** End of Utilities ******

// A reference to Stripe.js
var stripe;

// Disable the button until we have Stripe set up on the page
document.querySelector("button").disabled = true;

var create_payment_intent = function () {
  const { lessonId, setToAllSessions, timeSlot } = $("#checkout").data();

  const orderData = {
    lesson_id: lessonId,
    set_to_all_sessions: setToAllSessions === "on" ? true : false,
    time_slot: timeSlot,
  };

  fetch(`/lesson-order/create-payment-intent`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json; charset=utf-8;",
    },
    body: JSON.stringify(orderData),
  })
    .then(function (result) {
      return result.json();
    })
    .then(function (data) {
      return setupElements(data);
    })
    .then(function ({ stripe, card, clientSecret, orderId }) {
      document.querySelector("button").disabled = false;
      document.querySelector(".spinner").classList.add("hidden");
      document.querySelector(".sr-payment-form").classList.remove("hidden");

      // Handle form submission.
      var form = document.getElementById("payment-form");
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        // Initiate payment when the submit button is clicked
        pay(stripe, card, clientSecret, orderId);
      });
    });
};

// Set up Stripe.js and Elements to use in checkout form
var setupElements = function (data) {
  stripe = Stripe(data.publishableKey);
  var elements = stripe.elements();
  var style = {
    base: {
      color: "#32325d",
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: "antialiased",
      fontSize: "16px",
      "::placeholder": {
        color: "#aab7c4",
      },
    },
    invalid: {
      color: "#fa755a",
      iconColor: "#fa755a",
    },
  };

  var card = elements.create("card", { style: style });
  card.mount("#card-element");

  return {
    stripe: stripe,
    card: card,
    clientSecret: data.clientSecret,
    orderId: data.orderId,
  };
};

/*
 * Calls stripe.confirmCardPayment which creates a pop-up modal to
 * prompt the user to enter extra authentication details without leaving your page
 */
var pay = function (stripe, card, clientSecret, orderId) {
  changeLoadingState(true);

  // Initiate the payment.
  // If authentication is required, confirmCardPayment will automatically display a modal
  stripe
    .confirmCardPayment(clientSecret, {
      payment_method: {
        card: card,
      },
    })
    .then(function (result) {
      if (result.error) {
        // Show error to your customer
        showError(result.error.message);
      } else {
        // The payment has been processed!
        orderComplete(clientSecret, orderId);
      }
    });
};

/* ------- Post-payment helpers ------- */

/* Shows a success / error message when the payment is complete */
var orderComplete = function (clientSecret, orderId) {
  stripe.retrievePaymentIntent(clientSecret).then(function (result) {
    const paymentIntentJson = result.paymentIntent;
    $("#id_order_id").val(orderId);
    const lessonId = $("#checkout").data('lessonId');

    const postData = {
      order_id: orderId,
      payment_intent_json: paymentIntentJson,
    };

    fetch("/lesson-order/payment-complete", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json; charset=utf-8;",
      },
      body: JSON.stringify(postData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Success:", data);
        changeLoadingState(false);
        $("#checkout").submit();
      })
      .catch((error) => {
        console.error("Error:", error);
        changeLoadingState(false);
        $.confirm({
          title: "Encountered an error!",
          content: 'Lesson Booking Failed, Contact support for further assistance',
          type: "red",
          typeAnimated: true,
          buttons: {
            close: {
              text: "Close",
              btnClass: "btn-red",
              action: function () {
                window.location = `/lesson/${lessonId}/book`;
              },
            },
          },
        });
      });

    document.querySelector(".sr-payment-form").classList.add("hidden");

    document.querySelector(".sr-result").classList.remove("hidden");
    setTimeout(function () {
      document.querySelector(".sr-result").classList.add("expand");
    }, 200);
  });
};

var showError = function (errorMsgText) {
  changeLoadingState(false);
  var errorMsg = document.querySelector(".sr-field-error");
  errorMsg.textContent = errorMsgText;
  setTimeout(function () {
    errorMsg.textContent = "";
  }, 10000);
};

// Show a spinner on payment submission
var changeLoadingState = function (isLoading) {
  if (isLoading) {
    document.querySelector("button").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.querySelector("button").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
};

function init() {
  /**
   * Init Function to add event handlers
   */
  const paymentTypeVal = document.querySelector("#payment_type").value;
  if (paymentTypeVal === "STRIPE") {
    create_payment_intent();
    console.log("payment type" + paymentTypeVal);
  }
}

init();
