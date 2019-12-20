import codecs
from bs4 import BeautifulSoup
from konlpy.tag import Twitter
import urllib.request
import os, re, json, random
from selenium import webdriver

# 마르코프 체인 딕셔너리 만들기 --- (※1)
def make_dic(words):
    tmp = ["@"]
    dic = {}
    for word in words:
        tmp.append(word)
        if len(tmp) < 3: continue
        if len(tmp) > 3: tmp = tmp[1:]
        set_word3(dic, tmp)
        if word == ".":
            tmp = ["@"]
            continue
    return dic


# 딕셔너리에 데이터 등록하기 --- (※2)
def set_word3(dic, s3):
    w1, w2, w3 = s3
    if not w1 in dic: dic[w1] = {}
    if not w2 in dic[w1]: dic[w1][w2] = {}
    if not w3 in dic[w1][w2]: dic[w1][w2][w3] = 0
    dic[w1][w2][w3] += 1


# 문장 만들기 --- (※3)
def make_sentence(dic):
    def word_choice(sel):
        keys = sel.keys()
        return random.choice(list(keys))

    ret = []
    if not "@" in dic: return "no dic"
    top = dic["@"]
    w1 = word_choice(top)
    w2 = word_choice(top[w1])
    ret.append(w1)
    ret.append(w2)
    while True:
        w3 = word_choice(dic[w1][w2])
        ret.append(w3)
        if w3 == ".": break
        w1, w2 = w2, w3
    ret = "".join(ret)

    # 너무 길거나 짧지 않은 문장만을 추려, 네이버 맞춤법 교정기를 이용해 띄어쓰기와 맞춤법 교정 수행
    if len(ret) <= 16 and len(ret) > 5:
        driver = webdriver.Chrome()
        delay = 100
        driver.implicitly_wait(delay)

        driver.get(
            "https://search.naver.com/search.naver?sm=top_sug.pre&fbm=0&acr=1&acq=%EB%84%A4%EC%9D%B4%EB%B2%84+%EB%A7%9E&qdt=0&ie=utf8&query=%EB%84%A4%EC%9D%B4%EB%B2%84+%EB%A7%9E%EC%B6%A4%EB%B2%95+%EA%B2%80%EC%82%AC%EA%B8%B0")

        driver.implicitly_wait(delay)
        driver.find_element_by_xpath("""//*[@id="grammar_checker"]/div[2]/div[1]/div/div[1]/textarea""").send_keys(ret)
        driver.implicitly_wait(delay)
        driver.find_element_by_xpath("""//*[@id="grammar_checker"]/div[2]/div[1]/div/div[2]/button""").click()
        driver.find_element_by_xpath("""//*[@id="grammar_checker"]/div[2]/div[1]/div/div[2]/button""").click()
        driver.implicitly_wait(delay)
        try:
            res=driver.find_element_by_xpath("""//*[@id="grammar_checker"]/div[2]/div[2]/div/div[1]/p/em""").text
            res=res.replace("입력해주세요. ", "")
            res=res.replace("입력해 주세요. ", "")
            res=res.replace("입력해 주세요.", "")
            res=res.replace("입력해주세요.", "")
        except :
            driver.close()
            return ""
        driver.close()


    else:
        res = ""
    # 리턴
    return res

twitter =Twitter()
# 문장 읽어 들이기 --- (※4)
toji_file = "toji.txt"
dict_file = "markov-kids.json"
if not os.path.exists(dict_file):
    sen = ["2BGXXX25.txt", "2BGXXX26.txt", "2BGXXX27.txt", "2CG00002.txt", "2CG00004.txt", "3BG20003.txt",
           "3BG20007.txt", "4BE99001.txt", "BREO0311.txt", "BRGO0342.txt", "BRGO0357.txt", "BRGO0358.txt",
           "BRGO0360.txt"]
    # 동화책 텍스트 파일 읽기
    for sens in sen:
        fp = codecs.open(sens, "r", encoding="utf-16")
        soup = BeautifulSoup(fp, "html.parser")
        # body = soup.select_one("body > text")
        text = soup.getText()
        text = text.replace("…", "")  # 현재 koNLPy가 …을 구두점으로 잡지 못하는 문제 임시 해결
        # 형태소 분석
        malist = twitter.pos(text, norm=True)
        words = []
        for word in malist:
            # 구두점 등은 대상에서 제외(단 마침표는 포함)
            if not word[1] in ["Punctuation"]:
                words.append(word[0])
            if word[0] == ".":
                words.append(word[0])
        # 딕셔너리 생성
        dic = make_dic(words)
        json.dump(dic, open(dict_file, "w", encoding="utf-8"))
else:
    dic = json.load(open(dict_file, "r"))
# 문장 만들기 --- (※6)
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="dcvv9i9812", database="porong")
mycursor=mydb.cursor()
cnt = 0

mycursor.execute("SELECT sentence FROM sentence")
stcs=mycursor.fetchall()
stcss=[]
for i in range(len(stcs)) :
    stcss.append(stcs[i][0])

mycursor.close()
mycursor=mydb.cursor()
make_sentence_max=5

while True:
    sentence = make_sentence(dic)
    mystc=[]
    chk=0
    if len(sentence.split()) <= 5 and len(sentence.split()) > 1:
        if sentence is not '':
            mystc.append(sentence)
            for str in stcss :
                if str==mystc[0] :
                    chk=1
                    break
            if chk==1 :
                continue
            cnt=cnt+1
            print(cnt,"/",make_sentence_max)
            print("저장된 문장 : ",mystc[0])
            stcss.append(sentence)
            mycursor.execute("INSERT INTO sentence (sentence) VALUES (%s)", mystc)
            mydb.commit()
    if cnt is make_sentence_max:
        break
if(mydb.is_connected()) :
    mydb.close()
    mycursor.close()
    print("DB Connection is closed successful")