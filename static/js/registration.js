$(function () {
    $("#id_password1").change(function () {
        let passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,16}$/;
        if (!passwordRegex.test($("#id_password1").val())) {
            $('#pwd-errMsg').text("密碼需介於 8-16 碼需有 1 個以上英文字且有 1 個以上數字");
        } else {
            $('#pwd-errMsg').text("");
        }
    });

    $("#id_password2").change(function () {
        chkPwd($("#id_password1").val(), $("#id_password2").val());
    });

    $('#register-form').submit(function (event) {
        event.preventDefault();
        if (isValidate()) {
            $.ajax({
                type: "POST",
                async: false,
                url: api_registration,
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                data: $("#register-form").serialize(),
                success: function (response) {
                    if (response.success) {
                        alert("註冊成功 請至信箱確認註冊");
                        window.location.href = home_url;
                    } else {
                        alert(response.errors);
                    }
                },
                error: function (xhr, status, error) {
                    console.error("發生錯誤:" + error);
                }
            });
        }
    });
});

function isAccExist() {
    let flag = false
    $.ajax({
        type: "POST",
        async: false,
        url: api_chkAcc,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: $("#register-form").serialize(),
        success: function (response) {
            if (!response.success) {
                alert(response.errors);
                flag = true
            }
        },
        error: function (xhr, status, error) {
            console.error("系統發生錯誤:" + error);
            flag = true
        }
    });
    return flag
}

function chkPwd(pwd1, pwd2) {
    if (pwd1 && pwd2) {
        if (pwd1 !== pwd2) {
            $("#pwd2-errMsg").text("密碼 與 確認密碼 不一致");
            return false;
        } else {
            $("#pwd2-errMsg").text("");
        }
    } else {
        return false;
    }
    return true;
}

function isValidate() {
    let flag = true;
    if ($("#id_username").val().length == 0) {
        $("#username-errMsg").text("請輸入Email");
        flag = false;
    } else if (isAccExist()) {
        flag = false;
    }
    if (!chkPwd($("#id_password1").val(), $("#id_password2").val())) {
        flag = false;
    }
    return flag;
}