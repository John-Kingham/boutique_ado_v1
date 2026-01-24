/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

let stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
let clientSecret = $("#id_client_secret").text().slice(1, -1);
// @ts-ignore (can't get stripe types working!)
let stripe = Stripe(stripePublicKey);
let elements = stripe.elements();
let bootstrapDangerColour = "#dc3545";
let style = {
  base: {
    color: "#000",
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: "antialiased",
    fontSize: "16px",
    "::placeholder": {
      color: "#aab7c4",
    },
  },
  invalid: {
    color: bootstrapDangerColour,
    iconColor: bootstrapDangerColour,
  },
};
let card = elements.create("card", { style: style });
card.mount("#card-element");

// Display or remove payment card error messages
card.addEventListener("change", (event) => {
  let errorDiv = document.getElementById("card-errors");
  if (event.error) {
    $(errorDiv).html(`
      <span class="icon" role="alert">
        <i class="fas fa-times"></i>
      </span>
      <span>${event.error.message}</span>
    `);
  } else {
    errorDiv.textContent = "";
  }
});

// Handle form submission
let paymentForm = document.getElementById("payment-form");
paymentForm.addEventListener("submit", (event) => {
  event.preventDefault();
  card.update({ disabled: true });
  $("#submit-button").attr("disabled", "disabled");
  $("#payment-form").fadeToggle(100);
  $("#loading-overlay").fadeToggle(100);
  stripe
    .confirmCardPayment(clientSecret, { payment_method: { card: card } })
    .then((result) => {
      if (result.error) {
        $(document.getElementById("card-errors")).html(`
                <span class="icon" role="alert">
                  <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`);
        card.update({ disabled: false });
        $("#submit-button").removeAttr("disabled");
        $("#payment-form").fadeToggle(100);
        $("#loading-overlay").fadeToggle(100);
      } else {
        if (result.paymentIntent.status === "succeeded") {
          // @ts-expect-error (as the form var isn't cast to a HTMLForm type)
          paymentForm.submit();
        }
      }
    });
});
