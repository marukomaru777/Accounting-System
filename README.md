## 一、new Django project
### STEP1 create virtual environment & install package
```shell
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

### STEP2 create Django project
```shell
django-admin startproject accountingLog
python manage.py startapp bot
```

### STEP3 line-bot-sdk
至[line developers](https://developers.line.me/console/)取得channel secret、channel access token，放到settings
```python
# settings.py
LINE_CHANNEL_ACCESS_TOKEN = "channel access token"
LINE_CHANNEL_SECRET = "channel secret"
```
```python
# views.py
from linebot import LineBotApi, WebhookParser
from django.conf import settings

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.CHANNEL_SECRET)
```

### STEP4 本機環境使用ngrok讓外網連接
[ngrok下載後安裝](https://ngrok.com/download)
```shell
ngrok authtoken <token>
ngrok http <port>
```

修改vs code launch.json
```json
// launch.json
"args": [
    "runserver",
    "3000", //指定port，若無默認8000
]
```
```python
# settings.py
DEBUG = True # debug模式，程式上線後改False
ALLOWED_HOSTS = ["your host"]
```

### STEP5 部屬到render
[render](https://dashboard.render.com/)
#### django connect to postgresql
settings
```python
import dj_database_url
DATABASES["default"] = dj_database_url.parse(
    "External Database URL"
)
```

#### web service
git中的repo新增requirements.txt檔案，`pip3 freeze > requirements.txt`將環境所安裝套件整理至requirements.txt，另外因為render會用到gunicorn，也需加入requirements.txt中。

在render新增web service，連接github後選擇repo。
setting
Build Command: `pip install -r requirements.txt`
Start Command: `gunicorn <project name>.wsgi`

## 二、需求
記帳: 讓使用者在line上可以快速紀錄花費金額
明細: 查看紀錄明細
統計: 支出、收入，依照分類計算總和、百分比

可在網頁上快速檢視資料、修改分類設定

### (一)註冊/註銷
加入好友後，輸入任一訊息註冊。
PS. 註冊時(user)，自動新增分類(category)
支出: 飲食、繳費、日常、購物、娛樂、其他
收入: 薪水、獎金、兼職、投資、零用錢、其他
封鎖/移除好友後，將所有資料刪除。

### (二)記錄方式: 
#### 支出
輸入 desc amount (desc在前面好像比較符合手機打字)、amount後，跳出分類按鈕歸納
若多次點選分類按鈕會重複新增資料 > session?

#### 收入
輸入+amount desc、+amount後，跳出分類按鈕歸納
若多次點選分類按鈕會重複新增資料 > session?

## 三、資料庫設計
sqlite? postgresql?
### 1.使用者資料(user):
user_id (PK)

### 2.紀錄收支(expenses):
e_id (PK)
user_id (FK user)
c_id (FK category)
e_date: yyyy/MM/dd
e_type: 收入(+)或支出(-)
e_amount
e_desc

### 3.支出分類(category):
c_id (PK)
user_id (FK user)
c_name
c_icon
c_type: 分類屬於收入(+)或支出(-)

## 四、line bot Webhook
```python
from linebot.models.events import (
    MessageEvent,
    PostbackEvent
)
```

### (一)event
[事件說明](https://ithelp.ithome.com.tw/articles/10229773)
[群組相關事件及命令](https://ithelp.ithome.com.tw/m/articles/10270259)
#### 1.MessageEvent
當使用者傳送訊息給Line Bot時，會觸發MessageEvent事件
#### 2.PostbackEvent
[Postback event](https://ithelp.ithome.com.tw/articles/10302926)

### (二)回覆訊息
```python
line_bot_api.reply_message(event.reply_token, message)
```
* 回傳多個訊息，message為list
* 訊息種類分為text, image, location, sticker, audio, vedio, template
* [template](https://ithelp.ithome.com.tw/articles/10282102?sc=pt)
#### 1.文字訊息
```python
TextSendMessage(text = 文字訊息內容)
```
#### 2.選單
```python
TextSendMessage(
    text = "提示文字",
    quick_reply = QuickReply(
        items = [
            QuickReplyButton(action = PostbackAction(label=選單1, data=json.dumps(data.__dict__))),
            QuickReplyButton(action = PostbackAction(label=選單2, data=json.dumps(data.__dict__))),
                ]
            )
        )
```

### 3. 彈性訊息
[Flex Message](https://developers.line.biz/en/docs/messaging-api/using-flex-messages/)
[Flex Message Simulator範本](https://account.line.biz/login?redirectUri=https%3A%2F%2Fdevelopers.line.biz%2Fflex-simulator%2F%3Fstatus%3Dsuccess)
```python
FlexSendMessage(alt_text='YOUR_ALT_TEXT', contents=contents))
```
