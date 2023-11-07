function linkify(inputText) {
    var replacedText, replacePattern1, replacePattern2, replacePattern3;
  
    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');
  
    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');
  
    //Change email addresses to mailto:: links.
    replacePattern3 = /(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})/gim;
    replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');
  
    return replacedText;
  }
  


$(document).ready(function() {

    var welcomeMessage = function() {
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour + ":" + (minute < 10 ? '0' : '') + minute;
        var botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://i.postimg.cc/L4GnTMNp/UNHLOGO.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' +
            'Hi 🙋, How can I help you today?' +
            '<span class="msg_time">' + str_time + '</span></div></div>';
        $("#messageFormeight").append($.parseHTML(botHtml));
    };

    // Call the welcome message function on page load
    welcomeMessage();

    $("#messageArea").on("submit", function(event) {
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour+":"+minute;
        var rawText = $("#text").val();

        var userHtml = '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' + rawText + '<span class="msg_time_send">'+ str_time + '</span></div><div class="img_cont_msg"><img src="https://i.postimg.cc/SsHrfvnx/graduated.png" class="rounded-circle user_img_msg"></div></div>';
        
        $("#text").val("");
        $("#messageFormeight").append(userHtml);

        $.ajax({
            data: {
                msg: rawText,	
            },
            type: "POST",
            url: "/get",
        }).done(function(response) {

            var sources = response.sources
            var sourceLinksHtml = '';
                Object.keys(sources).forEach(function(key, index) {
                sourceLinksHtml += '<a class="button-33" href="' + sources[key] + '" target="_blank">Source ' + (index + 1) + '</a> ';
                });
            var botResponse = response.data
            botResponse = linkify(botResponse)
            var botHtml = '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://i.postimg.cc/L4GnTMNp/UNHLOGO.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer">' +
                
                botResponse +
                '<br/>' +
                sourceLinksHtml + 
                '<span class="msg_time">' + str_time + '</span></div></div>';
            $("#messageFormeight").append($.parseHTML(botHtml));
            
            $("#messageFormeight").scrollTop($("#messageFormeight")[0].scrollHeight);
        });
        event.preventDefault();
    });
});