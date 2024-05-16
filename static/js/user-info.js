$(function () {
    $("#id_new_password1").change(function () {
        let passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/;
        if (!passwordRegex.test($("#id_new_password1").val())) {
            $('#new_password1-errMsg').text("密碼需介於 8-16 碼需有 1 個以上英文字且有 1 個以上數字");
        } else {
            $('#new_password1-errMsg').text("");
        }
    });

    $("#id_new_password2").change(function () {
        if ($("#id_new_password1").val() && $("#id_new_password2").val()) {
            if ($("#id_new_password1").val() !== $("#id_new_password2").val()) {
                $("#new_password2-errMsg").text("密碼 與 確認密碼 不一致");
            } else {
                $("#new_password2-errMsg").text("");
            }
        }
    });

    $('#user-form').submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            async: false,
            url: api_save_user,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    alert("個人資料修改成功")
                    location.reload();
                } else {
                    alert(response.errors);
                }
            },
            error: function (xhr, status, error) {
                console.error("發生錯誤:" + error);
            }
        });
    });

    $('#pwd-form').submit(function (event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            async: false,
            url: api_change_pwd,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: $(this).serialize(),
            success: function (response) {
                if (response.success) {
                    alert("密碼修改成功")
                } else {
                    alert(response.errors);
                    $("#id_new_password1").val("");
                    $("#id_new_password2").val("");
                }
                $('#pwd-form').find('input').each(function() {
                    $(this).val("");
                });
            },
            error: function (xhr, status, error) {
                alert(error);
            }
        });
    });
})
