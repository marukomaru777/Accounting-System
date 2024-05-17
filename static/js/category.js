$(function () {
    $('#editModal').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget)
            , title = button.data('title')
            , c_id = button.data('id')
            , modal = $(this);
        if (c_id){
            modal.find('.modal-title').text(title);
            if (c_id == "insert"){
                clearInsertForm()
                modal.find('#id_c_id').val(c_id);
            }
            else{
                getEditData(c_id, modal);
            }
        }
        
    })

    // btn
    $('#modal-insert-btn').click(function () {
        saveEditModalData();
    });
});

// 將modal頁面中的輸入框資料清除
function clearInsertForm() {
    $('#id_name').val('');
    $('input[type=radio][name=type]').prop('checked', false);
}

// 取得欲編輯的資料
function getEditData(c_id, modal) {
    $.ajax({
        type: "POST",
        async: false,
        url: api_getEditCategory,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: {
            "c_id": c_id,
        },
        success: function (response) {
            if (response.success) {
                let data = response.result;
                modal.find('input[type=radio][name=type]').filter('[value="' + data.c_type + '"]').prop('checked', true);
                modal.find('#id_c_id').val(data.c_id);
                modal.find('#id_name').val(data.c_name);
            } else {
                alert(response.errors);
            }
        },
        error: function (xhr, status, error) {
            alert("發生錯誤:" + error);
        }
    });
}

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


// 儲存資料
function saveEditModalData() {
    $.ajax({
        type: "POST",
        async: false,
        url: api_saveCategory,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: $("#edit-form").serialize(),
        success: function (response) {
            if (response.success) {
                clearInsertForm();
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