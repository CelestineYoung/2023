import json
import os

import requests
import re
from bs4 import BeautifulSoup
import urllib.parse
import requests
import base64
from Crypto.Hash import MD5

debug = 0

enc = urllib.parse.urlencode
dec = urllib.parse.unquote

# 返回重做超链接
def get_repeat(homepage_html:str, id) -> str:
    qlist=[]
    result = 0
    soup = BeautifulSoup(homepage_html, "html.parser")
    for t in soup.find_all('li', {'data-exam-id': id}):
        for a in t.find_all('a', {'class': 'repeat'}):
            pattern = r'repeat-url="(.*)"'
            result = re.search(pattern,str(a))
            print(result.group(1))
    if result != 0:
        return result.group(1)
    return ""

# 重做考试
def repeat_exam(url:str, cookie:str):
    CSRF = re.search("csrftoken=(\S*);",cookie).group(1)
    header = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie': cookie,
        'X - CSRFToken': CSRF
    }
    post_content = 'csrfmiddlewaretoken=' + CSRF

    repeat_result = requests.post(url,data=post_content,headers=header)

    print("repeating:")
    if repeat_result.status_code == 200:
        print("repeated")
    else:
        print("repeat failed")
    return

# 获取题目网页
# 用于做题和制作题库
def get_question_page(group:str, id:str, cookie:str):
    url = 'https://www.yooc.me/group/'+group+'/exam/'+id+'/detail'

    header = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie': cookie
    }

    q_page = requests.get(url, headers=header).text
    print("getting question:")

    return q_page

# 获取主页
# 用于重新考试
def get_home_page(group:str, id:str, cookie:str):
    url = 'https://www.yooc.me/group/'+group+'/exams'

    header = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie': cookie
    }

    h_page = requests.get(url, headers=header).text
    print("getting home page:")
    return h_page

# 提交答案
def auto_post(group:str, id:str, cookie:str, filename:str):
    if not os.path.exists(filename):
        os.system(f"touch {filename}")
        with open(filename, "w") as f:
            f.write("{}")
    with open(filename,"r") as f:
        qlib = json.load(f)

    content = get_question_page(group, id, cookie)
    qlist = []
    ans = []
    soup = BeautifulSoup(content, "html.parser")
    for t in soup.find_all('div', {'class': 'exam-detial-container'}):
        for a in t.find_all('div', {'class': 'question-board'}):
            # 题目id
            qid = re.search(r'id="question-(\d*)">', str(a)).group(1)
            qlist.append(qid)
            if debug:
                print(qid)
            # 题目内容
            try:
                question = a.find_all('p', {'class': 'q-cnt crt'})[1].get_text()
            except Exception:
                question = ""
            question = MD5.new(question.encode("utf-8")).digest()
            question = base64.b64encode(question).decode()
            if debug:
                print(question)
            ans.append(answer(qlib, qid, question))
    ans = str(ans).replace(' ', '').replace('\'', '\"')
    post_exam(group,id,cookie,ans)

# 答题
def answer(qlib, qid, question):
    if question in qlib.keys():
        raw_ans = qlib[question]
    else:
        raw_ans = []
    ans = []
    if 'A' in raw_ans:
        ans.append("0")
    if 'B' in raw_ans:
        ans.append("1")
    if 'C' in raw_ans:
        ans.append("2")
    if 'D' in raw_ans:
        ans.append("3")
    if 'E' in raw_ans:
        ans.append("4")
    if 'F' in raw_ans:
        ans.append("5")
    if ans == []:
        ans = ["0"]
    fixed_ans = {"1":ans}
    ans = {qid:fixed_ans}
    return ans

# 提交考试
def post_exam(group:str, id:str, cookie:str, content:str):
    url = 'https://www.yooc.me/group/'+group+'/exam/'+id+'/answer/submit'
    CSRF = re.search("csrftoken=(\S*);",cookie).group(1)
    header = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cookie': cookie,
        'X-CSRFToken': CSRF
    }
    post_content = 'srfmiddlewaretoken=' + CSRF + '&'
    pre_ans = {"answers":content}
    if debug:
        print(dec(enc(pre_ans)))
    post_content = post_content + str(enc(pre_ans)) + '&type=0&auto=0'

    repeat_result = requests.post(url,data=post_content,headers=header)
    print("submitting:")
    print(repeat_result.text)
    return

# 组织题库
def add_qlib(group:str ,id:str ,cookie:str):
    content = get_question_page(group, id, cookie)
    soup = BeautifulSoup(content, "html.parser")
    qlib = {}
    for t in soup.find_all('div', {'class': 'exam-detial-container'}):
        for a in t.find_all('div', {'class': 'question-board'}):
            # 题目id
            id = re.search(r'id="question-(\d*)">', str(a)).group(1)
            if debug:
                print(id)
            # 题目内容
            if a.find_all('p', {'class': 'q-cnt crt'}) != []:
                question = a.find_all('p', {'class': 'q-cnt crt'})[1].get_text()
                ans = a.find_all('div', {'class': 'the-ans crt'})[0].find_all('p')[0].get_text()
            elif a.find_all('p', {'class': 'q-cnt fls'}) != []:
                question = a.find_all('p', {'class': 'q-cnt fls'})[1].get_text()
                ans = a.find_all('div', {'class': 'the-ans fls'})[0].find_all('p')[0].get_text()
            else:
                question = ""
                ans = a.find_all('div', {'class': 'the-ans crt'})
                if ans == []:
                    ans = a.find_all('div', {'class': 'the-ans fls'})
                ans = ans[0].find_all('p')[0].get_text()
            ans = re.findall("正确答案：(.*)",ans)[0].split("、")
            if debug:
                print(question)
            question = MD5.new(question.encode("utf-8")).digest()
            question = base64.b64encode(question).decode()
            if debug:
                print(question)
                print(ans)
            qlib[question] = ans
    return qlib

def make_qlib(group:str ,id:str ,cookie:str, filename=None):
    if filename == None:
        filename = id
    if not os.path.exists(filename):
        os.system(f"touch {filename}")
    with open(filename,"r") as f:
        qlib = json.load(f)
    new_qlib = add_qlib(group, id, cookie)
    new_keys = list(new_qlib.keys())
    for new_key in new_keys:
        if new_key not in qlib.keys():
            print(new_key)
            qlib[new_key] = new_qlib[new_key]
    with open(filename,"w") as f:
        json.dump(qlib,f)

if __name__ == "__main__":
    cookie = "" # 把cookie扔进去
    group = "6022858" # 注意修改组号
    id = "345711" # 考试号码
    data = "345701" # 别乱动
    auto_post(group, id, cookie, data)
    '''
    print("[auto doing]")
    auto_post(group, id, cookie, id)
    for i in range(100):
        print("[make qlib]")
        make_qlib(group,id,cookie)
        with open(id, "r") as f:
            qlib = json.load(f)
            print(f"qlib now has {len(list(qlib.keys()))} questions")
        print("[repeat exam]")
        repeat_exam(get_repeat(get_home_page(group,id,cookie),id),cookie)
        print("[auto doing]")
        auto_post(group,id,cookie,id)
    '''
    #debug = 1
    #make_qlib(group,id,cookie,id)