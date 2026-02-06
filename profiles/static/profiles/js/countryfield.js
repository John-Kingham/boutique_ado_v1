// Manage color for the user profile default country input.
let countrySelected = $("#id_default_country").val();
if (!countrySelected) {
  $("#id_default_country").css("color", "#aab7c4");
}
$("#id_default_country").on("change", function () {
  if (!$(this).val()) {
    $(this).css("color", "#aab7c4");
  } else {
    $(this).css("color", "#000");
  }
});
