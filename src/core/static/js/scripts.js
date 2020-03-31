(function ($) {
$(document).ready(function(){
    $(".field-article").addClass("hide");
    $(".field-header_title").addClass("hide");
    $(".field-header_subtitle").addClass("hide");
    $(".field-header_image").addClass("hide");

    $(".field-header #id_header").change(function () {
        var value = $(this).val();

        if (value == 'full') {
            $(".field-header_title").show("slow").removeClass("hide");
            $(".field-header_subtitle").show("slow").removeClass("hide");
        } else {
            $(".field-header_title").hide("slow").addClass("hide");
            $(".field-header_subtitle").hide("slow").addClass("hide");
        }

        if (value == 'image') {
            $(".field-header_image").show("slow").removeClass("hide");
        } else {
            $(".field-header_image").hide("slow").addClass("hide");
        }
    }).change();
});
})(jQuery);