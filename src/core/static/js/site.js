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

  if (!(value.match("^http"))) {
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