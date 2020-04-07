window.addEventListener("load", function() {
    (function($) {
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
        } else if(is_vimeo !== -1) {
          video_site.val("vimeo").change();
          console.log("Vimeo link");
        } else {
          embed_code = 0;
          video_site.val("other").change();
          console.log("Other video link");
        }
        $("#id_embed_code").val(embed_code);
      });

      function getYoutubeId(url){
         url = url.split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
         return (url[2] !== undefined) ? url[2].split(/[^0-9a-z_\-]/i)[0] : url[0];
      }
    })(django.jQuery);
});