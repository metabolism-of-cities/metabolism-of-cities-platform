<script type="text/javascript">

  /*
   * FIRST WE DEFINE SOME FUNCTIONS AND CONSTANTS THAT ARE CALLED LATER, WHEN PARTICULAR
   * EVENTS ARE TRIGGERED
   *
  */

  /* Used to format numbers later on */
  const formatter = new Intl.NumberFormat('fr-FR', {
    maximumFractionDigits: 2
  });

  function errorMessage(message) {
    alert(message);
  }

  function getData() {
    /*  We start by fading out the map and showing a loading icon */
    $("svg").css("opacity", "0.2");
    $(".loading").show();

    /* Let's build the URL */
    category = 3;
    var jsonURL = "/water/ajax/?category=" + category;

    $(".region-bar a.btn-dark").each(function(){
      var region = $(this).data("region");
      jsonURL += "&region=" + region;
    });

    jsonURL += "&date_start=" + $("select[name='date_start']").val() + "&date_end=" + $("select[name='date_end']").val();

    $.getJSON(jsonURL)
    .done(function(response) {
      items = []
      max_flow = 0

      /*  First we get the total value of ALL flows */
      $.each(response, function(key, val) {
        if (val > max_flow) {
          max_flow = val;
        }
      });

      max_width = 10;
      all_flows = [];

      {% for each in flows %}
        all_flows.push({{ each.identifier }});
      {% endfor %}

      $.each(response, function(key, val) {
        fraction = val/max_flow; /* Here we can calculate the flow proportionate to the max_flow */
        width = fraction*max_width; /* This makes the width of THIS flow proportionate to the max */
        $("#path-" + key).show();
        $("#path-" + key).css("stroke-width", width + "px");
        $("#path-" + key).attr("title", formatter.format(val) + " {{ category.unit.symbol }}");
        $("#path-" + key).attr("data-toggle", "tooltip");
        $("#path-" + key).attr("data-placement", "left");
        all_flows = all_flows.filter(item => item !== Number(key));
      });

      /* Whichever flow was NOT included in the ajax response needs to be removed from the map */
      $.each(all_flows, function(index, value) {
        $("#path-" + value).hide();
      });

      $("svg").css("opacity", "1");
      $(".loading").hide();

      $('[data-toggle="tooltip"]').tooltip({container: 'body'});

    })
    .fail(function() {
      errorMessage("Failed to load data. Are you connected to the internet? Please reload the page or try again later.")
    })
  }

  function setDateLabels() {
    start_date = $("select[name='date_start']").val();
    end_date = $("select[name='date_end']").val();
    if (start_date.length == 4 && end_date.length == 4) {
      if (start_date == end_date) {
        /* Start and end dates are both years, and they are the same */
        date_label = start_date;
      } else {
        /* Start and end dates are both years, but they are different */
        date_label = start_date + "-" + end_date;
      }
      $("#title_date").html(date_label);
    } else {
      /* If there are months involved, then we want to show e.g. Jan 2022-Dec 2023 */
      /* To do so, we need to convert this to date objects and then reformat */
      var options = { year: "numeric", month: "short" };

      if (start_date.length == 4) {
        start_date = start_date + "-01-01";
      } else {
        start_date = start_date + "-01";
      }
      start_date = new Date(start_date);
      start_date_label = start_date.toLocaleDateString("fr-FR", options);

      if (end_date.length == 4) {
        end_date = end_date + "-12-01"; /* If a year is selected, then we show 'Dec XXXX' so cast to December date */
      } else {
        end_date = end_date + "-01";
      }
      end_date = new Date(end_date);
      end_date_label = end_date.toLocaleDateString("fr-FR", options);

      if ($("select[name='date_start']").val() == $("select[name='date_end']").val()) {
        date_label = start_date_label;
      } else {
        date_label = start_date_label + "-" + end_date_label;
      }

      $(".title_date").html(date_label);
    }
  }

  /*
   * THESE ARE PARTICULAR EVENTS THAT TRIGGER ACTION
   *
  */


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
    title_region = "";
    if (activated_regions == 6 || region == "1" || activated_regions == 0) {
      /*  Either ALL or NO region activated, so fallback to Eau d'Azur */
      $(".region-bar a").removeClass("btn-dark");
      $(".region-bar a[data-region='1']").addClass("btn-dark");
      $(".map-region").addClass("active-space");
      title_region = "Eau d'Azur";
    } else {
      $(".map-region").removeClass("active-space");
      $(".region-bar a.btn-dark").each(function(){
        var region = $(this).data("region");
        $("#space-"+region).addClass("active-space");
        title_region += $(this).text() + ", ";
      });
      title_region = title_region.substring(0, title_region.length - 2);
    }
    $("#title_region").html(title_region);

    getData();

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

  $("#animate").click(function(){
    if ($(this).is(":checked")) {
      $(".path").css("stroke-dasharray", "1");
    } else {
      $(".path").css("stroke-dasharray", "0");
    }
  });

  $("#changedate").submit(function(e){
    e.preventDefault();
    setDateLabels();
    getData();
  });
</script>

