from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from bot.func import *

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, PostbackEvent, UnfollowEvent, TextSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


# Create your views here.
def index(request):
    test = "建置成功"
    return render(request, "test.html", {"res": test})


@csrf_exempt
def callback(request):
    if request.method == "POST":
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            msg_return = ""
            if isinstance(event, MessageEvent):
                try:
                    user_id = event.source.user_id
                    msg = event.message.text.strip()
                    msg_return = MsgEvent(user_id, msg)
                    line_bot_api.reply_message(event.reply_token, msg_return)
                except Exception:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text="系統發生錯誤")
                    )

            if isinstance(event, PostbackEvent):
                try:
                    user_id = event.source.user_id
                    postback_str = event.postback.data
                    msg_return = PstBkEvent(user_id, postback_str)
                    line_bot_api.reply_message(event.reply_token, msg_return)
                except Exception:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text="系統發生錯誤")
                    )

            if isinstance(event, UnfollowEvent):
                user_id = event.source.user_id
                UnfolwEvent(user_id)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
