$(function () {
        // modal
        $('#editModal').on('show.bs.modal', function (event) {
            let button = $(event.relatedTarget)
                , title = button.data('title')
                , e_id = button.data('id')
                , modal = $(this);
            if (e_id){
                modal.find('.modal-title').text(title);
                debugger
                if (e_id == "insert"){
                    clearInsertForm();
                    modal.find('#id_e_id').val(e_id);
                }
                else{
                    getEditData(e_id, modal);
                }
            }
            
        })

    // datepicker
    $('#datepicker-search').datepicker({
        format: "yyyy-mm", //設定格式為2019-04
        autoclose: true,//選擇日期後就會自動關閉
        todayHighlight: true,//今天會有一個底色
        clearBtn: false,//清除按钮
        minViewMode: "months", // 選擇月份模式
        startView: "months", // 初始顯示月份模式
        language: 'zh-TW'//中文化
    }).on("change", function () {
        let selected = $('#search-text').val();
        console.log('get data: ' + selected);
    });
    $('#datepicker-search').datepicker('update', dateParam);
    
    $('#prev-month-btn').click(function () {
        let current_date = $('#datepicker-search').datepicker('getDate');
        current_date.setMonth(current_date.getMonth() - 1);
        // $('#datepicker-search').datepicker('update', current_date);
        window.location.href=url_pre_detail;
    });
    $('#next-month-btn').click(function () {
        let current_date = $('#datepicker-search').datepicker('getDate');
        current_date.setMonth(current_date.getMonth() + 1);
        // $('#datepicker-search').datepicker('update', current_date);
        window.location.href=url_next_detail;
    });

    // btn
    $('#modal-insert-btn').click(function () {
        saveeditModalData();
    });
});

// 儲存資料
function saveeditModalData() {
    $.ajax({
        type: "POST",
        async: false,
        url: api_saveExpense,
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

// 刪除花費資料
function deleteData(e_id){
    if (confirm("確定要刪除此筆消費嗎？")){
        $.ajax({
            type: "POST",
            async: false,
            url: api_del,
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: {
                "e_id": e_id,
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

// 取得欲編輯的資料
function getEditData(e_id, modal) {
    $.ajax({
        type: "POST",
        async: false,
        url: api_getEditExpense,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: {
            "e_id": e_id,
        },
        success: function (response) {
            if (response.success) {
                let data = response.result;
                modal.find('input[type=radio][name=type]').filter('[value="' + data.e_type + '"]').prop('checked', true);
                modal.find('#id_e_id').val(data.e_id);
                modal.find('#id_amount').val(data.e_amount);
                modal.find('#id_date').datepicker('update', data.e_date);
                modal.find('#id_desc').val(data.e_desc);
                filterCategoryDdl(data.e_type);
                modal.find('#category-select').selectedIndex = data.category;
            } else {
                alert(response.errors);
            }
        },
        error: function (xhr, status, error) {
            alert("發生錯誤:" + error);
        }
    });
}

// 將modal頁面中的輸入框資料清除
function clearInsertForm() {
    // $('#{{ form.current_user.auto_id }}').val('{{current_user}}');
    $('#id_amount').val('');
    $('#id_desc').val('');
    $('input[type=radio][name=type]').filter('[value="-"]').prop('checked', true);
    $('#category-select').selectedIndex='-';
    filterCategoryDdl('-');
}