$(function () {

});

function deleteData(c_id){
    if (confirm("此類別底下的收支紀錄將一併刪除，確定要刪除嗎？")){
        $.ajax({
            type: "POST",
            async: false,
            url: api_del,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: {
                "c_id": c_id,
            },
            success: function (response) {
                if (response.success) {
                    location.reload();
                } else {
                    alert(response.errors);
                }
            },
            error: function (xhr, status, error) {
                alert("發生錯誤:" + error);
            }
        });
    }
}