(function ($) {
$(document).ready(function(){
  $(".field-article").addClass("hide");
  $(".field-header_title").addClass("hide");
  $(".field-header_subtitle").addClass("hide");
  $(".field-header_image").addClass("hide");

  $(".field-header #id_header").change(function () {
    var value = $(this).val();

    if (value == "full") {
      $(".field-header_title").show("fast").removeClass("hide");
      $(".field-header_subtitle").show("fast").removeClass("hide");
    } else {
      $(".field-header_title").hide("fast").addClass("hide");
      $(".field-header_subtitle").hide("fast").addClass("hide");
    }

    if (value == "image") {
      $(".field-header_image").show("fast").removeClass("hide");
    } else {
      $(".field-header_image").hide("fast").addClass("hide");
    }
  }).change();
});
})(jQuery);
