<script type="text/javascript">
$(function(){
  $(".region-bar a").click(function(e){
    e.preventDefault();
    var region = $(this).data("region");

    if ($(this).hasClass("mnca-button")) {
      /* MNCA button is pressed so we remove all regions and only activate this one */
      $(".region-bar a").removeClass("btn-warning");
      $(this).addClass("active");
    } else {
      $(".mnca-button").removeClass("active");
      if ($(this).hasClass("btn-warning")) {
        isActive = true;
      } else {
        isActive = false;
      }

      if (isActive) {
        $(this).removeClass("btn-warning");
      } else {
        $(this).addClass("btn-warning");
      }
    }

    var activated_regions = $(".region-bar a.btn-warning").length;
    if (activated_regions == 6 || activated_regions == 0) {
      /*  Either ALL or NO region activated, so fallback to MNCA */
      $(".region-bar a").removeClass("btn-warning");
      $(".mnca-button").addClass("active");
    }

  });

  $("#current-period").click(function(e){
    e.preventDefault();
    if ($(".period-dropdown").is(":visible")) {
      $(".period-dropdown").slideUp("fast");
      $("#current-period .bi-caret-down").show();
      $("#current-period .bi-caret-up").hide();
    } else {
      $(".period-dropdown").slideDown("fast");
      $("#current-period .bi-caret-down").hide();
      $("#current-period .bi-caret-up").show();
    }
  });

});
</script>
