<script type="text/javascript">
$(function(){
  $(".region-bar a").click(function(e){
    e.preventDefault();
    var region = $(this).data("region");

    if ($(this).hasClass("mnca-button")) {
      /* Eau d'azur button is pressed so we remove all regions and only activate this one */
      $(".region-bar a").removeClass("btn-dark");
      $(this).addClass("active");
    } else {
      $(".mnca-button").removeClass("active");
      if ($(this).hasClass("btn-dark")) {
        isActive = true;
      } else {
        isActive = false;
      }

      if (isActive) {
        $(this).removeClass("btn-dark");
      } else {
        $(this).addClass("btn-dark");
      }
    }

    var activated_regions = $(".region-bar a.btn-dark").length;
    if (activated_regions == 6 || activated_regions == 0) {
      /*  Either ALL or NO region activated, so fallback to MNCA */
      $(".region-bar a").removeClass("btn-dark");
      $(".mnca-button").addClass("active");
      $(".map-region").addClass("active-space");
    } else {
      $(".map-region").removeClass("active-space");
      $(".region-bar a.btn-dark").each(function(){
        var region = $(this).data("region");
        $("#space-"+region).addClass("active-space");
      });
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
