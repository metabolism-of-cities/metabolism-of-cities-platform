window.addEventListener("load", function() {
  (function($) {
    $(".field-embed_code").css('visibility', 'hidden');
    var url ;
    var embed_code;
    var video_site = $("#id_video_site");
    $("#id_url").keyup(function() {
      url = $(this).val();
      var is_youtube = url.indexOf("youtu");
      var is_vimeo = url.indexOf("vimeo");
      if (is_youtube !== -1) {
        embed_code = getYoutubeId(url);
        video_site.val("youtube").change();
        console.log("Youtube link");
        console.log("ID: "+ embed_code);
      } else if(is_vimeo !== -1) {
        video_site.val("vimeo").change();
        embed_code = getVimeoId(url);
        video_site.val("vimeo").change();
        console.log("Vimeo link");
        console.log("ID: "+ embed_code);
      } else {
        embed_code = "";
        video_site.val("other").change();
        console.log("Other video link");
      }
      $("#id_embed_code").val(embed_code);
    });
    //Fuction to extract youtube video id from the URL
    function getYoutubeId(url){
      url = url.split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
      var id = (url[2] !== undefined) ? url[2].split(/[^0-9a-z_\-]/i)[0] : url[0];
      return id;
    }
    //Fuction to extract vimeo id from the URL
    function getVimeoId(url) {
      var vimeo_Reg = /https?:\/\/(?:www\.)?vimeo.com\/(?:channels\/(?:\w+\/)?|groups\/([^\/]*)\/videos\/|album\/(\d+)\/video\/|)(\d+)(?:$|\/|\?)/;
      var match = url.match(vimeo_Reg);
      if(match){
        return match[3];
      } else {
        return " ";
      }
    }
  })(django.jQuery);
});