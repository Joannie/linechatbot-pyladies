# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationMessage, LocationSendMessage,
)

app = Flask(__name__)

handler = WebhookHandler('71eb03c70c4a3d6d0bddbaf12fa055b2') 
line_bot_api = LineBotApi('K6DSSGqndAau6ZcZqXVLAdMRkMFyonvCmQJSZQcU8LP0+PVg8tNlmzU90xsAxJbyXdfmlcOAmCD/6R9lC73P5jQonwqW/VS+7mffLrlE2COwCZU8A+VYXIil/M5dUePXG4+FbNFmAmZ7Dk20BFcE8gdB04t89/1O/w1cDnyilFU=') 

@app.route('/')
def index():
    return "<p>Hello World!</p>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ================= 機器人區塊 Start =================
import random
import json
import requests
place = ""
@handler.add(MessageEvent, message=TextMessage)  # default
def handle_text_message(event):                  # default
    msg = event.message.text #message from user
    global place
    reply = ""

    #運用AI.api來顯示回覆
    session_id ="06784882-5283-4ebc-abbe-0ea2a96326d7"
    client_ac = "d216cdceb5d149f3b6f29c937e2d4348"

    url = "https://api.api.ai/v1/query?query={}&lang=zh-TW&sessionId={}".format(msg,session_id)
    header={
        "Authorization":"Bearer {}".format(client_ac)
    }
    rep = requests.get(url,headers=header)
    html = rep.text
    data = json.loads(html)
    intent = data['result']['metadata']['intentName']
    if(intent == "Ask for Help"):
        place = data['result']['parameters']['police']
        reply = data['result']['speech']
    else:
        keyword_list = ["心情不好","給個鼓勵"]
        good_list = [
                        "一個人走得快，一群人走得遠",
                        "我們也是一群會想放棄的凡人，唯一的差別是，最後我們選擇走下去"
                    ]
        if msg in keyword_list:
            index = random.randint(0,len(good_list)-1)
            print(good_list[index]) #print會印在Heroku log中，不會在line出現
            reply = good_list[index]
        elif msg=="我很滿意你的服務":
            print("希望你有愉快的一天")
            reply = "希望你有愉快的一天"
        # 找尋附近的警察局
        else:
            print("我聽不懂你在說什麼！")
            reply = "我聽不懂你在說什麼！"

    # 針對使用者各種訊息的回覆 Start =========
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply))

    # 針對使用者各種訊息的回覆 End =========

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_msg(event):
    now_lat = event.message.latitude
    now_lng = event.message.longitude

    if(place):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&key=AIzaSyBMU20Fgs3RwDOrJMOS5_NrgoqEtmWQns8&rankby=distance&types=police&language=zh-TW".format(now_lat, now_lng)
        rep = requests.get(url)
        html = rep.text
        data = json.loads(html)
        first = data['results'][0]
        title = first['name']
        address = first['vicinity']
        lat = first['geometry']['location']['lat']
        lng = first['geometry']['location']['lng']
        place_id = first['place_id']
        print('名字:{}'.format(title) + '\n' + '地址:{}'.format(address) + '\n' + '經緯度:{},{}'.format(lat, lng))
        reply = '名字:{}'.format(title) + '\n' + '地址:{}'.format(address) + '\n' + '經緯度:{},{}\n'.format(lat, lng)

        if(place_id):
            url_details = "https://maps.googleapis.com/maps/api/place/details/json?key=AIzaSyBMU20Fgs3RwDOrJMOS5_NrgoqEtmWQns8&placeid={}".format(place_id)
            rep = requests.get(url_details)
            html = rep.text
            data = json.loads(html)
            phone = data['result']['international_phone_number']
            reply += "直接撥打電話報警:{}".format(phone)


        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))


    else:
        reply = "我知道你現在在{}{}，但我不知道你要找什麼".format(now_lat,now_lng,place)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

# ================= 機器人區塊 End =================

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
