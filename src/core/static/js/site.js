// generic function to smoothly scroll to an ID
function scrollToID(id){
  $("html,body").animate({
   scrollTop: $("#" + id).offset().top
  }, "slow");
}

// open and close markdown help box -- here because it's not possible to add jquery to includes
$(".open-markdown-help, .close-markdown-help").click(function() {
  $(".markdown-help").toggle()
})

// form check for urls
$("input[type='url']").attr("placeholder", "Must start with http:// or https://").change(function() {
  let input = $(this)
  let value = input.val();

  value.trim();

  if (value != "" && !(value.match("^http"))) {
    value = "http://" + value;
  }

  input.val(value);
})

// date input helper
// https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
$("input[type='date']").attr({
  placeholder: "Must be in YYYY-MM-DD format",
  title: "Must be in YYYY-MM-DD format",
  pattern: "\\d{4}-\\d{2}-\\d{2}",
});

// For the translation button
$("#translate").change(function(){
    url = encodeURI(window.location.href);
    language = $(this).val();
    window.location = "https://translate.google.com/translate?hl=&sl=en&tl=" + language + "&u=" + url;
});

// generic function to show something when loading slow page
function loadBigPage(content) {
  $(".loading-big-page #loading-content").text(content);
  $("body").addClass("overflow-hidden");
  $(".loading-big-page").addClass("active");
  $(".loading-big-page i").addClass("fa-spin");
}

// all links with this class should show loading feedback
$(".open-big-page").click(function() {
  let content = $(this).data("content");
  loadBigPage(content)
})

// TEMPORARY GEOJSON FOR STOCKS MAP
const brussels = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "muni": "Anderlecht",
        "schauff": 312,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.28741455078125,
              50.86642804992854
            ],
            [
              4.2771148681640625,
              50.81244314781362
            ],
            [
              4.339256286621094,
              50.813961648915885
            ],
            [
              4.3341064453125,
              50.86469456623886
            ],
            [
              4.28741455078125,
              50.86642804992854
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Jette",
        "schauff": 1000,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.28741455078125,
              50.86837814203458
            ],
            [
              4.286041259765625,
              50.86642804992854
            ],
            [
              4.3341064453125,
              50.86469456623886
            ],
            [
              4.378395080566406,
              50.886791655353164
            ],
            [
              4.331703186035156,
              50.90346585160204
            ],
            [
              4.28741455078125,
              50.86837814203458
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Schaerbeek",
        "schauff": 490,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.379081726074219,
              50.88700824161983
            ],
            [
              4.425773620605469,
              50.87336134013673
            ],
            [
              4.450492858886718,
              50.88310953475148
            ],
            [
              4.41925048828125,
              50.90389886806409
            ],
            [
              4.379081726074219,
              50.88700824161983
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Jette",
        "schauff": 90,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.333763122558594,
              50.86447787624557
            ],
            [
              4.39727783203125,
              50.851691383954154
            ],
            [
              4.4213104248046875,
              50.86772812039658
            ],
            [
              4.4254302978515625,
              50.873144690427644
            ],
            [
              4.378395080566406,
              50.886791655353164
            ],
            [
              4.333763122558594,
              50.86447787624557
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Jette",
        "schauff": 1200,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.337882995605469,
              50.829794504314215
            ],
            [
              4.396247863769531,
              50.85147463352982
            ],
            [
              4.334449768066406,
              50.86404449323755
            ],
            [
              4.337882995605469,
              50.829794504314215
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Jette",
        "schauff": 678,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.339942932128906,
              50.813961648915885
            ],
            [
              4.406547546386719,
              50.81482934166636
            ],
            [
              4.410667419433594,
              50.841286227401966
            ],
            [
              4.3952178955078125,
              50.8510411296595
            ],
            [
              4.336509704589844,
              50.830228205617445
            ],
            [
              4.339942932128906,
              50.813961648915885
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "muni": "Jette",
        "schauff": 877,
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              4.411010742187499,
              50.839985419652976
            ],
            [
              4.447059631347655,
              50.835215480984196
            ],
            [
              4.457359313964844,
              50.852558375579136
            ],
            [
              4.422340393066406,
              50.86664473085768
            ],
            [
              4.417920112609863,
              50.865425887530776
            ],
            [
              4.395647048950195,
              50.85082437621345
            ],
            [
              4.410731792449951,
              50.84136752668223
            ],
            [
              4.410560131072998,
              50.84001252018429
            ],
            [
              4.410903453826904,
              50.839985419652976
            ],
            [
              4.411010742187499,
              50.839985419652976
            ]
          ]
        ]
      }
    }
  ]
}
