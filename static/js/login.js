$(function () {
    $('#login-form').submit(function (event) {
        event.preventDefault();
        if (isValidate()) {
            $.ajax({
                type: "POST",
                async: false,
                url: api_login,
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                data: $(this).serialize(),
                success: function (response) {
                    if (response.success) {
                        window.location.href = url_index;
                    } else {
                        $("#pwd-errMsg").text(response.errors);
                        $("#id_password").val("");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("發生錯誤:" + error);
                }
            });
        }
    });
})

function isValidate() {
    flag = true;
    if ($(`#id_username`).val().length == 0) {
        $("#username-errMsg").text("請輸入Email");
        flag = false;
    }
    if ($(`#id_password`).val().length == 0) {
        $("#pwd-errMsg").text("請輸入密碼");
        flag = false;
    }
    return flag
}