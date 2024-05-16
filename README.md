# 記帳平台
## 一、系統功能
### (一) 註冊頁面
- 使用者註冊帳號
- 註冊時，系統寄送驗證帳號連結 email 給使用者
- 點選 email 連結確認註冊

使用者註冊
![image](./readme_assets/registration.png)

註冊驗證信
![image](./readme_assets/reg_confirm_mail.png)

點選註冊驗證信連結，成功註冊
![image](./readme_assets/reg_success.png)

點選註冊驗證信連結，註冊失敗
![image](./readme_assets/reg_fail.png)

### (二) 登入頁面
- 使用者登入帳號

登入
![image](./readme_assets/login.png)

### (三) 明細頁面
- 登入後才能瀏覽此頁面
- 以月份為單位查詢資料
- 新增/編輯/刪除收支資料

搜尋條件預設為今日的月份
![image](./readme_assets/detail.png)

新增/編輯資料
![image](./readme_assets/detail-insert.png)
![image](./readme_assets/detail-update.png)

### (四) 使用者資料設定
- 更改個人資料
- 重設密碼
![image](./readme_assets/user-info.png)

## 使用此專案
示範環境：macOS
### STEP1 clone & cd this folder
```shell
git clone https://github.com/marukomaru777/AccountingLog # clone專案
cd AccountingLog # 切至專案資料夾
```

### STEP2 create virtual environment & install package
```shell
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

### STEP3 migrate database
使用sqlite
```shell
python3 manage.py makemigrations
python3 manage.py migrate
```

### STEP4 設定 `accountingLog/setting.py`
1.`SECRET_KEY`
手動生成
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

```python
SECRET_KEY = "your_generated_secret_key_here"
```

2.`ALLOWED_HOSTS`
設置為本機
```python
ALLOWED_HOSTS = ["127.0.0.1"]
```

3.`LINE_CHANNEL_ACCESS_TOKEN`, `LINE_CHANNEL_SECRET`
至[line developers](https://developers.line.me/console/)取得 channel secret、channel access token

4.`CSRF_TRUSTED_ORIGINS"`
設置為本機
```python
CSRF_TRUSTED_ORIGINS = ["https://*.127.0.0.1"]
```

5.`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
至[gmail app password](https://dev.to/krishnaa192/creating-google-app-password-for-django-project-4oj3)取得 app password
```python
EMAIL_HOST_USER = "your_gmail_account"
EMAIL_HOST_PASSWORD = "your_app_password"
```

6.`WEB_URL`
設置為本機，若欲變更網域，則需要更新此變數
```python
WEB_URL = "https://*.127.0.0.1"
```

設定完成後即可在本機啟動。

### STEP5 修改vs code launch.json
指定port:3000
```json
// launch.json
"args": [
    "runserver",
    "3000", //指定port，若無默認8000
]
```

### STEP6 使用ngrok讓外網連接
1.安裝並啟動 ngrok
[ngrok下載後安裝](https://ngrok.com/download)
```shell
ngrok authtoken <token>
```

指定 port 啟動 ngrok ( `<port>` 需對應 launch.json 所指定的 port)
```shell
ngrok http <port>
```
此時會生成隨機網址，可讓外網連線。

2.修改 `accountingLog/setting.py`
以下修改成 ngrok 生成的網址
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `WEB_URL`

完成後可從外網連線。


**以下未完成**
## 三、系統設計
### (一) 資料庫設計

### (二) APP
- `users`: 使用者相關操作
- `accounting`: 收支記錄相關操作

### (一) 註冊/註銷
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
