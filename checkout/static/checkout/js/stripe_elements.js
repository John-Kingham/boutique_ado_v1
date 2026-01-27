/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

let stripePublicKey = $("#id_stripe_public_key").text().slice(1, -1);
let clientSecret = $("#id_client_secret").text().slice(1, -1);
let stripe = Stripe(stripePublicKey);
let elements = stripe.elements();
let bootstrapDangerColour = "#dc3545";
let cardStyle = {
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
let stripeCard = elements.create("card", { style: cardStyle });
stripeCard.mount("#card-element");

// Display or remove payment card error messages
stripeCard.addEventListener("change", (event) => {
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
  stripeCard.update({ disabled: true });
  $("#submit-button").attr("disabled", "disabled");
  $("#payment-form").fadeToggle(100);
  $("#loading-overlay").fadeToggle(100);
  let saveInfo = Boolean($("#id-save-info").attr("checked"));
  let csrfToken = $(`input[name="csrfmiddlewaretoken"]`).val();
  let postData = {
    csrfmiddlewaretoken: csrfToken,
    client_secret: clientSecret,
    save_info: saveInfo,
  };
  let url = "/checkout/cache_checkout_data/";
  $.post(url, postData)
    .done(() => {
      stripe
        .confirmCardPayment(clientSecret, {
          payment_method: {
            card: stripeCard,
            billing_details: {
              name: paymentForm.full_name.value.trim(),
              phone: paymentForm.phone_number.value.trim(),
              email: paymentForm.email.value.trim(),
              address: {
                line1: paymentForm.street_address1.value.trim(),
                line2: paymentForm.street_address2.value.trim(),
                city: paymentForm.town_or_city.value.trim(),
                country: paymentForm.country.value.trim(),
                state: paymentForm.county.value.trim(),
              },
            },
          },
          shipping: {
            name: paymentForm.full_name.value.trim(),
            phone: paymentForm.phone_number.value.trim(),
            address: {
              line1: paymentForm.street_address1.value.trim(),
              line2: paymentForm.street_address2.value.trim(),
              city: paymentForm.town_or_city.value.trim(),
              country: paymentForm.country.value.trim(),
              postal_code: paymentForm.postcode.value.trim(),
              state: paymentForm.county.value.trim(),
            },
          },
        })
        .then((result) => {
          if (result.error) {
            $(document.getElementById("card-errors")).html(`
          <span class="icon" role="alert">
            <i class="fas fa-times"></i>
          </span>
          <span>${result.error.message}</span>`);
            stripeCard.update({ disabled: false });
            $("#submit-button").removeAttr("disabled");
            $("#payment-form").fadeToggle(100);
            $("#loading-overlay").fadeToggle(100);
          } else {
            if (result.paymentIntent.status === "succeeded") {
              paymentForm.submit();
            }
          }
        });
    })
    .fail(() => {
      location.reload();
    });
});
