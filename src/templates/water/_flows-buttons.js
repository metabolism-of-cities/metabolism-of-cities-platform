<script type="text/javascript">
$(function(){
  $(".region-bar a").click(function(e){
    e.preventDefault();
    var region = $(this).data("region");

    if (region == "1") {
      /* Eau d'azur button is pressed so we remove all regions and only activate this one */
      $(".region-bar a").removeClass("btn-dark");
      $(this).addClass("btn-dark");
    } else {
      $(".region-bar a[data-region='1']").removeClass("btn-dark");
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
    if (activated_regions == 6 || region == "1") {
      /*  Either ALL or NO region activated, so fallback to Eau d'Azur */
      $(".region-bar a").removeClass("btn-dark");
      $(".region-bar a[data-region='1']").addClass("btn-dark");
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
