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
$("input[type='url']").change(function() {
  let input = $(this)
  let value = input.val();

  value.trim();

  if (!(value.match("^http"))) {
    value = "http://" + value;
  }

  input.val(value);
})

// form fix for date picker on mac
$("input[type='date']").attr("placeholder", "Format as YYYY-MM-DD");