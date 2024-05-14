$(function () {
    $('#login-form').submit(function (event) {
        event.preventDefault();
        if (isValidate()) {
            $.ajax({
                type: "POST",
                async: false,
                url: "{% url 'login' %}",
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                data: $(this).serialize(),
                success: function (response) {
                    if (response.success) {
                        window.location.href = '{% url "detail" %}';
                    } else {
                        alert(response.errors);
                        $("#{{form.password.auto_id}}").val("");
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
    if ($(`#{{form.account.auto_id}}`).val().length == 0) {
        $("#acc-errMsg").val("請輸入Email");
        flag = false;
    }
    if ($(`#{{form.password.auto_id}}`).val().length == 0) {
        $("#pwd-errMsg").val("請輸入密碼");
        flag = false;
    }
    return flag
}