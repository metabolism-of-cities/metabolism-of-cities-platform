// generic function to smoothly scroll to an ID
function scrollToID(id){
  $("html,body").animate({
   scrollTop: $("#" + id).offset().top
  }, "slow");
}