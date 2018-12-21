# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
from string import punctuation
from operator import itemgetter
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rc
from matplotlib import style
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = ''
slack_client_id = ''
slack_client_secret = ''
slack_verification = ''
sc = SlackClient(slack_token)

def _crawl_naver_keywords(text):

    lists = []
    turn_list = []
    day_list = []
    win_num_list = []
    money_list = []
    people_list = []
    talks = []
    count_list=[]

    if "시작" in text:
        lists.append("1. 회차조회\n2. 예상번호\n3. 번호등록\n4. 종료")

    elif "회차" in text:
        lists.append("몇회차 얻고싶나요?? ex) 250회")

    elif "등록" in text:
        print("번호등록")
        new_list =[]
        new_list.append("숫자 6개 입력해주세요 ex) 2 5 7 13 35 42 .")
        # 한글 지원을 위해 앞에 unicode u를 붙힙니다.
        return u'\n'.join(new_list)

    elif "예상번호" in text:
        new_list = []
        tag_to_views = {}
        with open('db.txt') as my_file:
            for line in my_file:
                # 1 This is Elice. 와 같이, "(줄번호) (내용)" 형식으로 출력합니다.
                for char in punctuation:
                    line = line.replace(char, '').replace("\n", '')
                line = line.split(" ")
                # print(line)
                for tag in line:
                    if tag in tag_to_views:
                        tag_to_views[tag] = tag_to_views[tag] + 1
                    else:
                        tag_to_views[tag] = 1
        # print(tag_to_views)
        # (태그, 인기도)의 리스트 형식으로 변환합니다.
        tag_view_pairs = list(tag_to_views.items())
        top_tag_and_views = sorted(tag_view_pairs, key=itemgetter(1), reverse=True)[:6]

        for i in top_tag_and_views:
            new_list.append(i[0])
        for i in top_tag_and_views:
            count_list.append(i[1])
        final = sorted(new_list)

        #bar_plot(new_list, count_list, '숫자', 'count 수')
        # 한글 지원을 위해 앞에 unicode u를 붙힙니다.
        return u' '.join(final)

    elif "." in text:
        new_list =[]
        new_text = text[13:]
        text = list(new_text.split(' '))
        del text[-1]
        for i in text:
            if int(i) > 45:
                new_list.append("숫자는 1~45이어야 합니다.")
                return u'\n'.join(new_list)
        if len(text) != 6:
            new_list.append("숫자는 6개 입력해야 합니다.")
            return u'\n'.join(new_list)
        text = text.sort()
        f = open("personal_number.txt","a")
        f.write(str(text)+"\n")
        f.close()
        new_list.append("등록 완료!")

        return u'\n'.join(new_list)


    elif "회" in text:
        new_list =[]
        new_text = text[13:]
        real = new_text[:-1]
        int_text = int(real)
        url = "https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo=" + str(int_text)

        # URL 주소에 있는 HTML 코드를 soup에 저장합니다.
        soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

        ##### list_title와 list_nickname append()를 사용하여 원하는 정보를 하나씩 담아 출력합니다. #####

        tmp_num_list = []
        lotto_list = soup.find("div", class_="content_wrap content_winnum_645")
        for turn in lotto_list.find_all("h4"):
            turn_list.append(turn.get_text().strip())

        for day in lotto_list.find_all("p", class_="desc"):
            day_list.append(day.get_text().strip())

        for win_num in lotto_list.find_all("div", class_="nums"):
            for num in win_num.find_all("span"):
                tmp_num_list.append(int(num.get_text().strip()))
        win_num_list.append(tmp_num_list)
        for j, money in enumerate(lotto_list.find("tbody").find("tr").find_all("td")):
            if j == 3:
                money_list.append(money.get_text().strip())

        for k, people in enumerate(lotto_list.find("tbody").find("tr").find_all("td")):
            if k == 2:
                people_list.append(people.get_text().strip())

        assert (len(turn_list) == len(day_list))
        for i in range(len(turn_list)):
            new_list.append("{}{} 당첨 번호 :{} 당첨자 수 : {}, 개인별 당첨금 : {} 입니다.".format(turn_list[i], day_list[i], win_num_list[i],
                                                                             people_list[i], money_list[i]))
        # 한글 지원을 위해 앞에 unicode u를 붙힙니다.
        return u'\n'.join(new_list)

    else:
        lists.append("짐은 정해준 대화만 할줄 안다.")

    # 한글 지원을 위해 앞에 unicode u를 붙힙니다.
    return u'\n'.join(lists)

def scatter_plot(x, y, x_label, y_label):
    font = fm.FontProperties(fname='./NanumBarunGothic.ttf')

    plt.scatter(x, y)
    plt.xlabel(x_label, fontproperties=font)
    plt.ylabel(y_label, fontproperties=font)

    plt.xlim((min(x), max(x)))
    plt.ylim((min(y), max(y)))
    plt.tight_layout()

    plot_filename = 'plot.png'
    plt.savefig(plot_filename)
#    elice_utils.send_image(plot_filename)


def bar_plot(x_ticks, y, x_label, y_label):
    assert (len(x_ticks) == len(y))

    font = fm.FontProperties(fname='./NanumBarunGothic.ttf')

    pos = range(len(y))
    plt.bar(pos, y, align='center')
    plt.xticks(pos, x_ticks, rotation='vertical', fontproperties=font)

    plt.xlabel(x_label, fontproperties=font)
    plt.ylabel(y_label, fontproperties=font)
    plt.tight_layout()

    plot_filename = 'plot.png'
    plt.savefig(plot_filename)
    plt.show()

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>서버 구동중...</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)