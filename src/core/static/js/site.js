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