$(function () {
    $('#link-form').submit(function (event) {
        debugger
        event.preventDefault();
        $.ajax({
            type: "POST",
            async: false,
            url: api_link_line,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: $(this).serialize(),
            success: function (response) {
                debugger
                if (response.success) {
                    window.location.href = response.link;
                    $("#link-form").hide();
                    $("#suc-msg").text("綁定成功").show();
                } else {
                    $("#pwd-errMsg").text(response.errors);
                    $("#id_username").val("");
                    $("#id_password").val("");
                }
            },
            error: function (xhr, status, error) {
                console.error("發生錯誤:" + error);
            }
        });
    })
})