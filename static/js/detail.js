$(function () {

    // modal
    $('#editModal').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget)
            , title = button.data('title')
            , e_id = button.data('id')
            , modal = $(this);
        modal.find('.modal-title').text(title);
        if (e_id == "insert"){
            clearInsertForm();
            modal.find('#id_e_id').val(e_id);
        }
        else{
            getEditData(e_id, modal);
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
        // getSumDetailData(selected);
        // getDetailData(selected);
    });
    $('#datepicker-search').datepicker('update', (new Date()));
    $('#prev-month-btn').click(function () {
        let current_date = $('#datepicker-search').datepicker('getDate');
        current_date.setMonth(current_date.getMonth() - 1);
        $('#datepicker-search').datepicker('update', current_date);
    });
    $('#next-month-btn').click(function () {
        let current_date = $('#datepicker-search').datepicker('getDate');
        current_date.setMonth(current_date.getMonth() + 1);
        $('#datepicker-search').datepicker('update', current_date);
    });

    // btn
    $('#modal-insert-btn').click(function () {
        saveeditModalData();
    });
});

// 取得右邊花費明細
// function getDetailData(selected) {
//     $.ajax({
//         type: "POST",
//         async: false,
//         url: api_getDetail,
//         headers: { 'X-CSRFToken': getCookie('csrftoken') },
//         data: {
//             "selected_date": selected,
//         },
//         success: function (response) {
//             if (response.success) {
//                 processingData(response.result);
//             } else {
//                 alert(response.errors);
//             }
//         },
//         error: function (xhr, status, error) {
//             alert("發生錯誤:" + error);
//         }
//     });
// }

// 將取得花費明細資料轉為html
function processingData(raw_data) {
    // 創建一個空物件來存放分群後的資料
    let grouped_data = {};

    // 使用迴圈處理每筆資料
    for (let i = 0; i < raw_data.length; i++) {
        let current_item = raw_data[i]; let e_date = current_item.e_date; //
        // 檢查分群是否已經存在，如果不存在，則創建一個新的陣列 
        if (!grouped_data[e_date]) {
            grouped_data[e_date] = {
                data: [], // 每日的資料
                totalValue: 0 // 初始化每日花費總額 0 
            };
        }
        // 將每日資料加入data中
        grouped_data[e_date].data.push(current_item);
        // 更新每日總和 
        if (current_item.e_type == '+') {
            // 替換掉千分逗點
            grouped_data[e_date].totalValue += parseInt(current_item.e_amount.replace(/,/g, ''));
        }
        else {
            grouped_data[e_date].totalValue -= parseInt(current_item.e_amount.replace(/,/g, ''));
        }
    }
    // 對分群後的資料進行排序，依照 e_date 欄位遞減排序 
    let sorted_grouped_data = Object.entries(grouped_data)
        .sort(([dateA], [dateB]) => new Date(dateB) - new Date(dateA))
        .reduce((obj, [date, value]) => {
            obj[date] = value;
            return obj;
        }, {});
    // 遍歷排序後的資料，將每個分群的資料插入容器中
    let container = document.getElementById('daily-detail');
    container.innerHTML = '';
    for (let date_data in sorted_grouped_data) {
        let daily_element = document.createElement('div');
        daily_element.classList.add('col-12', 'row', 'daily-list');

        let summary_element = document.createElement('div');
        summary_element.classList.add('col-12', 'row', 'sum');
        summary_element.innerHTML = `
        <div class="col-4">${date_data}</div>
        <div class="col-8" style="text-align: right;">Total: ${numberComma(grouped_data[date_data].totalValue)}</div>
        `;
        daily_element.appendChild(summary_element);

        for (let item of grouped_data[date_data].data) {
            // 这里的 item 就是数组中的每个对象
            let detail_list_element = document.createElement('div');
            detail_list_element.classList.add('col-12', 'row', 'detail-list');


            let detail_element = document.createElement('div');
            detail_element.classList.add('col-12', 'row', 'detail');

            let html_element = `
                <div class="col-md-2 col-2 d-flex justify-content-center align-items-center icon">
                    <img src="{% static 'img/icon.png' %}" class="img-fluid">
                </div>
                <div class="col-md-5 col-4 description">
                    <div class="col-12 class">${item.category__c_name}</div>
                    <!-- <div class="col-12 tag">tag</div> -->
                    <div class="col-12 info">${item.e_desc}</div>
                </div>
                <div class="col-md-3 col-2 row amount">
                    <p class="col-12 text-right" style="text-align: right;">${item.e_type.replace('+', '')}${item.e_amount}</p>
                </div>
                <div class="col-md-2 col-4 d-flex justify-content-center align-items-center edit-btn">
                    <div class="text-center">
                        <!-- Button trigger modal -->
                        <button type="button" class="btn btn-outline-dark" data-toggle="modal" data-target="#editModal" data-title="編輯" data-id="${item.e_id}">
                            編輯
                        </button>
                        <button class="btn btn-outline-dark" onclick="deleteData(${item.e_id})">
                            刪除
                        </button>
                    </div>
                </div>
            `;
            detail_element.innerHTML = html_element;
            detail_list_element.appendChild(detail_element);
            daily_element.appendChild(detail_list_element);
        }
        container.appendChild(daily_element);
    }
}

// 將數字轉成千分位逗號
function numberComma(num){
    let comma=/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g
    return num.toString().replace(comma, ',')
}

// 取得左邊花費總和
// function getSumDetailData(selected) {
//     $.ajax({
//         type: "POST",
//         async: false,
//         url: api_getSumDetail,
//         headers: { 'X-CSRFToken': getCookie('csrftoken') },
//         data: {
//             "selected_date": selected,
//         },
//         success: function (response) {
//             if (response.success) {
//                 processingSumData(response.result, selected);
//             } else {
//                 alert(response.errors);
//             }
//         },
//         error: function (xhr, status, error) {
//             alert("發生錯誤:" + error);
//         }
//     });
// }

// 將取得花費總和資料轉為html
function processingSumData(raw_data, selected_month) {
    let container = document.getElementById('summary-detail');
    container.innerHTML = '';

    let total = 0,
        spend_tot = 0,
        income_tot = 0;

    let ul_element_spend = document.createElement('ul'),
        ul_element_income = document.createElement('ul'),
        span_element_spend = document.createElement('div'),
        span_element_income = document.createElement('div');
    span_element_spend.classList.add('col-12', 'tip');
    span_element_income.classList.add('col-12', 'tip');

    // 顯示各類別的花費總額
    for (let i = 0; i < raw_data.length; i++) {
        let item = raw_data[i],
            li_element = document.createElement('li');

        li_element.innerText = `${item.category__c_name}：${item.e_type&item.total_spent>0 == '-' ? '-' : ''}${item.total_spent}`;
        if (item.e_type == '+'){
            ul_element_income.appendChild(li_element);
            income_tot += parseInt(item.total_spent.replace(/,/g, ''));
        }else{
            ul_element_spend.appendChild(li_element);
            spend_tot += parseInt(item.total_spent.replace(/,/g, ''));
        }
    };
    span_element_income.innerHTML = `收入小計：${numberComma(income_tot)}`;
    span_element_spend.innerHTML = `支出小計：${spend_tot>0 == '-' ? '-' : ''}${numberComma(spend_tot)}`;

    container.appendChild(span_element_income);
    container.appendChild(ul_element_income);
    
    container.appendChild(span_element_spend);
    container.appendChild(ul_element_spend);
    
    total = income_tot - spend_tot;
    container = document.getElementById('summary');
    container.innerHTML = '';
    summary_element = document.createElement('div');
    summary_element.classList.add('col-12', 'tip');
    summary_element.innerHTML = `Total：${numberComma(total)}`;
    container.appendChild(summary_element);
}

// 儲存資料
function saveeditModalData() {
    $.ajax({
        type: "POST",
        async: false,
        url: post_detail,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: $("#edit-form").serialize(),
        success: function (response) {
            if (response.success) {
                let selected = $('#search-text').val();
                getDetailData(selected);
                getSumDetailData(selected);
                clearInsertForm();
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
                    let selected = $('#search-text').val();
                    getDetailData(selected);
                    getSumDetailData(selected);
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