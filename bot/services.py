from bot.models import CustomUser, Expenses, Category, ExpenseResult
from django.db.models import Sum
from datetime import datetime
import calendar
import json
from django.conf import settings
from django.db import transaction
from linebot.models import (
    TextSendMessage,
    QuickReply,
    QuickReplyButton,
    FlexSendMessage,
    MessageAction,
    PostbackAction,
)
import requests
from django.urls import reverse
from django.db.models.functions import Coalesce
from django.db.models import Value

# 訊息事件：若已綁定帳號，則依照訊息內容回應；否則進行資料綁定
def MsgEvent(user_id, msg):
    user = CustomUser.objects.filter(line_id=user_id).first()
    if user:
        username = user.username
        if "綁定"in msg.upper():
            msg_return = LinkUser(user_id)
        # elif "明細" in msg.upper():
        #     if "今日" in msg.upper() or "今天" in msg.upper():
        #         date_from = datetime.now().date()
        #         date_to = datetime.now().date()
        #     else:
        #         now = datetime.now()
        #         date_from = datetime(now.year, now.month, 1)
        #         date_to = datetime(
        #             now.year, now.month, calendar.monthrange(now.year, now.month)[1]
        #         )
        #     msg_return = GetDetMsg(username, date_from, date_to)
        elif "統計" in msg.upper():
            now = datetime.now()
            date_from = datetime(now.year, now.month, 1)
            date_to = datetime(
                now.year, now.month, calendar.monthrange(now.year, now.month)[1]
            )
            msg_return = GetAggMsg(username, date_from, date_to)
        else:
            data = ChkInputMsg(msg)
            if data.result:
                c_list = GetCategory(username, data.type)
                items = []
                for i in c_list:
                    data.type = i["c_type"]
                    data.c_id = i["c_id"]
                    item = QuickReplyButton(
                        action=PostbackAction(
                            label=i["c_name"], data=json.dumps(data.__dict__)
                        )
                    )
                    items.append(item)
                msg_return = TextSendMessage(
                    text="請選擇消費分類", quick_reply=QuickReply(items)
                )
            else:
                msg_return = TextSendMessage(text="輸入格式錯誤！")
    else:
        msg_return = LinkUser(user_id)
    return msg_return


def ChkInputMsg(msg):
    if msg[0] == "+":
        type = "+"
        msg = msg[1:]
    else:
        type = "-"
    input_list = msg.strip().split()
    if len(input_list) == 2:
        if IsFloat(input_list[0]):
            amount = int(input_list[0])
            desc = input_list[1]
        elif IsFloat(input_list[1]):
            amount = int(input_list[1])
            desc = input_list[0]
        # 需再判斷收入or支出
        return ExpenseResult(True, type, amount, desc)
    else:
        return ExpenseResult(False)


def IsFloat(str):
    s = str.split(".")
    if len(s) > 2:
        return False
    else:
        for si in s:
            if not si.isdigit():
                return False
        return True


def GetCategory(username, c_type):
    c_set = Category.objects.filter(username=username, c_type=c_type).values(
        "c_id", "c_type", "c_name"
    )
    if c_set.count() > 0:
        return list(c_set)
    else:
        raise Exception("No Category.")


def AddExpensesLog(model):
    try:
        with transaction.atomic():
            Expenses.objects.create(
                username=model.username,
                category=model.category,
                e_date=model.e_date,
                e_type=model.e_type,
                e_amount=model.e_amount,
                e_desc=model.e_desc,
            )
            return True
    except Exception:
        return False



def GetExpenseDetail(username, date_from, date_to):
    result = Expenses.objects.filter(
        username=username, e_date__range=[date_from, date_to]
    ).values().order_by("-e_date") # 按日期排序
    return list(result)


def GetExpenseAgg(username, e_type, date_from, date_to):
    result = (
            Expenses.objects.values("category_id")
            .filter(username=username, e_type=e_type, e_date__range=[date_from, date_to])
            .annotate(amount_sum=Sum("e_amount"))
        )
    return list(result)

# 取得明細訊息 (加總有bug)
def GetDetMsg(username, date_from, date_to):
    result = GetExpenseDetail(
        username, date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")
    )
    items = []
    total_amount = 0
    for i in result:
        total_amount += int(i["e_amount"])
        item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": i["e_date"].strftime("%Y/%m/%d"),
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                },
                {
                    "type": "text",
                    "text": Category.objects.get(c_id=i["category_id"]).c_name,
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                    "margin": "md",
                },
                {
                    "type": "text",
                    "text": "NT$ " + f"{i['e_amount']:,}",
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                    "margin": "md",
                    "align": "center",
                },
                {
                    "type": "text",
                    "text": 'none' if (i["e_desc"] is None or i["e_desc"] == "") else i["e_desc"],
                    "size": "sm",
                    "color": "#555555",
                    "align": "start",
                    "margin": "md",
                },
            ],
        }
        items.append(item)

    msg_return = FlexSendMessage(
        alt_text="收支明細",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "收支明細",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "sm",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "NT$ " + f"{total_amount:,}",
                                "size": "xxl",
                                "color": "#555555",
                                "flex": 0,
                                "weight": "bold",
                            },
                            {
                                "type": "text",
                                "size": "xxl",
                                "color": "#555555",
                                "align": "end",
                                "weight": "bold",
                                "text": "Total",
                            },
                        ],
                    },
                    {
                        "type": "text",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True,
                        "text": date_from.strftime("%Y/%m/%d")
                        + " ~ "
                        + date_to.strftime("%Y/%m/%d"),
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": items,
                    },
                ],
            },
            "styles": {"footer": {"separator": True}},
        },
    )
    return msg_return

# 取得統計訊息
def GetAggMsg(username, date_from, date_to):
    expense_result = GetExpenseAgg(username, "-", date_from, date_to)
    income_result = GetExpenseAgg(username, "+", date_from, date_to)
    total_expense = 0
    total_income = 0
    income_items = [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "收入",
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                }
            ],
        }
    ]
    for i in income_result:
        total_income += int(i["amount_sum"])
        item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": Category.objects.get(c_id=i["category_id"]).c_name,
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                },
                {
                    "type": "text",
                    "text": "NT$ " + f"{int(i['amount_sum']):,}",
                    "size": "sm",
                    "color": "#111111",
                    "align": "end",
                },
            ],
        }
        income_items.append(item)
    expense_items = [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "支出",
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                }
            ],
        }
    ]
    for i in expense_result:
        total_expense += int(i["amount_sum"])
        item = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": Category.objects.get(c_id=i["category_id"]).c_name,
                    "size": "sm",
                    "color": "#555555",
                    "flex": 0,
                },
                {
                    "type": "text",
                    "text": "NT$ " + f"{int(i['amount_sum']):,}",
                    "size": "sm",
                    "color": "#111111",
                    "align": "end",
                },
            ],
        }
        expense_items.append(item)
    items = income_items + [{"type": "separator", "margin": "xxl"}] + expense_items
    msg_return = FlexSendMessage(
        alt_text="收支統計",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "收支統計",
                        "weight": "bold",
                        "color": "#1DB446",
                        "size": "sm",
                    },
                    {
                        "type": "text",
                        "text": "收入",
                        "weight": "bold",
                        "size": "md",
                        "margin": "md",
                    },
                    {
                        "type": "text",
                        "text": "NT$ " + f"{total_income:,}",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "md",
                    },
                    {
                        "type": "text",
                        "text": "支出",
                        "weight": "bold",
                        "size": "md",
                        "margin": "md",
                    },
                    {
                        "type": "text",
                        "text": "NT$ " + f"{total_expense:,}",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "md",
                    },
                    {
                        "type": "text",
                        "text": date_from.strftime("%Y/%m/%d")
                        + " ~ "
                        + date_to.strftime("%Y/%m/%d"),
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xxl",
                        "spacing": "sm",
                        "contents": items,
                    },
                    {"type": "separator", "margin": "xxl"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "收支",
                                "size": "xs",
                                "color": "#aaaaaa",
                                "flex": 0,
                            },
                            {
                                "type": "text",
                                "text": "NT$ " + f"{total_income-total_expense:,}",
                                "color": "#aaaaaa",
                                "size": "xs",
                                "align": "end",
                            },
                        ],
                    },
                ],
            },
            "styles": {"footer": {"separator": True}},
        },
    )
    return msg_return


# 新增後點選類別按鈕回傳事件：新增收支紀錄
def PstBkEvent(user_id, postback_str):
    postback_data = json.loads(postback_str)
    model = Expenses(
        username=CustomUser.objects.get(line_id = user_id),
        category=Category.objects.get(c_id=postback_data["c_id"]),
        e_type=postback_data["type"],
        e_amount=postback_data["e_amount"],
        e_desc=postback_data["e_desc"],
        e_date=datetime.now().strftime("%Y-%m-%d"),
    )
    if AddExpensesLog(model):
        c_name = model.category.c_name
        msg_return = FlexSendMessage(
            alt_text="新增結果",  # 聊天列表所顯示的訊息
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "新增成功",
                            "weight": "bold",
                            "color": "#1DB446",
                            "size": "sm",
                        },
                        {
                            "type": "text",
                            "text": "NT$ " + f"{model.e_amount:,}",
                            "weight": "bold",
                            "size": "xxl",
                            "margin": "md",
                        },
                        {
                            "type": "text",
                            "size": "xs",
                            "color": "#aaaaaa",
                            "wrap": True,
                            "text": c_name,
                        },
                        {"type": "separator", "margin": "xxl"},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "xxl",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "日期",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0,
                                        },
                                        {
                                            "type": "text",
                                            "text": model.e_date,
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "end",
                                        },
                                    ],
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "size": "sm",
                                            "color": "#555555",
                                            "flex": 0,
                                            "text": "備註",
                                        },
                                        {
                                            "type": "text",
                                            "text": model.e_desc,
                                            "size": "sm",
                                            "color": "#111111",
                                            "align": "end",
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                "styles": {"footer": {"separator": True}},
            },
        )
    else:
        msg_return = TextSendMessage(text="新增失敗")
    return msg_return


# 取消綁定
def CancelLink(user_id):
    try:
        if CustomUser.objects.filter(line_id=user_id).exists():
            with transaction.atomic():
                user = CustomUser.objects.get(line_id=user_id)
                user.line_id = None
                user.nonce = None
                user.save()
                return True
    except Exception:
        return False


# 帳號綁定
def AccLinkEvent(user_id, nonce):
    try:
        with transaction.atomic():
            user = CustomUser.objects.get(nonce=nonce)
            user.line_id = user_id
            user.save()
            msg_return = LinkUser(user_id)
            return msg_return
    except Exception as e:
        return TextSendMessage(text="綁定失敗，系統發生錯誤：{}".format(e)) 

# 若帳號未進行綁定，則回傳綁定連結；有綁定則回傳取消綁定連結
def LinkUser(user_id):
    if CustomUser.objects.filter(line_id=user_id).exists():
        msg = FlexSendMessage(
            alt_text="帳號已綁定",  # 聊天列表所顯示的訊息
            contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "action": {
                        "type": "uri",
                        "uri": "https://line.me/"
                        },
                        "contents": [
                        {
                            "type": "text",
                            "text": "帳號已綁定",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center"
                        }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#DE8788",
                            "margin": "xxl",
                            "action": {
                            "type": "uri",
                            "label": "取消綁定",
                            "uri": "{url}{view}"
                                        .format(url=settings.WEB_URL, view=reverse('users:cancelLinkToLine', kwargs={'lineId': user_id}))
                            }
                        }
                        ]
                    }
                    }
        )
    else:
        # 構建請求的標頭
        headers = {
            'Authorization': f'Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}'
        }
        # 發送POST請求
        response = requests.post("https://api.line.me/v2/bot/user/{userId}/linkToken".format(userId=user_id), headers=headers)
        # 檢查回應
        if response.status_code == 200:
            # 取得 res token
            link_token = json.loads(response.text)['linkToken']

            msg = FlexSendMessage(
                alt_text="尚未綁定帳號",  # 聊天列表所顯示的訊息
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "action": {
                        "type": "uri",
                        "uri": "https://line.me/"
                        },
                        "contents": [
                        {
                            "type": "text",
                            "text": "尚未綁定帳號",
                            "size": "xl",
                            "weight": "bold",
                            "align": "center"
                        }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#787785",
                            "margin": "xxl",
                            "action": {
                            "type": "uri",
                            "label": "綁定帳號",
                            "uri": "{url}{view}"
                                         .format(url=settings.WEB_URL, view=reverse('users:linkToLine', kwargs={'token': link_token}))
                            }
                        }
                        ]
                    }
                    }
            )
        else:
            msg = TextSendMessage(text="發送API發生問題")
        
    return msg