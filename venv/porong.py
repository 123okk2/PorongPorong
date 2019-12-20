import codecs
from bs4 import BeautifulSoup
from konlpy.tag import Twitter,Okt
import urllib.request
import os, re, json, random
from selenium import webdriver
from flask import Flask, render_template, redirect, request, url_for
import mysql.connector
import copy

app = Flask(__name__)
#mySQL 연결.
mydb = mysql.connector.connect(host="localhost", user="root", passwd="dcvv9i9812", database="porong")

#커서 생성.
mycursor = mydb.cursor()
mycursor.execute("SELECT sentence FROM sentence")

#fetchall: 모든 데이터를 가져온다.
#fetchone: 첫번째 행의 데이터를 가져온다.
#[0]을 붙이지 않으면 ['...'] 형식으로 출력된다.

#twitter=Twitter()
okt=Okt()
dict_file = "markov-kids.json"
dictionary = mycursor.fetchall()
#dic_list=list(dictionary)
dic_list=[]

for i in range(len(dictionary)):
    dic_list.append(dictionary[i][0])

#내부 코드 부분
dic = json.load(open(dict_file, "r"))

#내부코드 종료

#웹부분.
@app.route('/') # 첫페이지,
def homepage():
    return render_template('porongweb.html')

def shuffle_sentence(sentence): # 문장 리스트 랜덤으로 섞음

    tempSentence = copy.deepcopy(sentence)

    while(True):
        for i in range(1, 20):
            ex1 = random.randrange(0,len(sentence))
            ex2 = random.randrange(0,len(sentence))

            temp = sentence[ex1];
            sentence[ex1] = sentence[ex2];
            sentence[ex2] = temp;
        if(tempSentence !=sentence): break

    return sentence

@app.route('/sentence') # 문장 완성하기
def Ques_sentence():
    sentences = random.choice(dic_list)  # DB에 저장된 문장 중 무작위로 한 문장을 가져온다.
    print(sentences)
    splitted_sentence = sentences.split()  # split(): 해당 문장을 띄어씌기 단위로 나누어 splitted_sentence에 저장.
    print(splitted_sentence)
    shuffle = copy.deepcopy(splitted_sentence)
    shuffle_sentence(shuffle) ####
    print(shuffle)

    splitted_sentence = ''.join(splitted_sentence)
    print(splitted_sentence)
    return render_template('sentenceweb.html', w_answer=splitted_sentence, w_shuffle=shuffle)

@app.route('/blank') # 빈칸 채우기
def Ques_blank():
    sentences = random.choice(dic_list)
    splitted_sentence = sentences.split()

    random.seed()
    num = random.randint(0, len(splitted_sentence) - 1)

    correct_answer = splitted_sentence[num] # 정답
    temp = sentences.replace(correct_answer,'x')
    ques = str.split(temp) # 문제 만들기

    correct_answer=str(correct_answer).replace('.','')
    examples = [correct_answer]

    if num is 1 or 2 or 3 or 4 or 5:
        for i in range(3):
            examples.append(random.choice(list(dic)))

    else: # 첫번쨰 빈칸이 아닐때
        print('진입')
        print('앞단어:',splitted_sentence[num-1])
        sps = okt.pos(splitted_sentence[num-1]) # 터지는 라인
        print('앞조사:',sps)
        print('문제구간 종료')
        sps = sps[len(sps) - 1][0] # 빈칸자리의 앞 단어
        ex_str = dic[sps]  # 빈칸자리의 후보
        #pre_list=[] # 나오면 안되는 단어들
        #for s in ex_str:
        #    pre_list.append(s)

        for i in range(3):
            string = random.choice(list(dic))
            if num != 0: # 빈칸이 문장의 처음이 아닐때
                count = 0 # // 0 : 불가능 // 1: 가능
            for strs in list(ex_str.keys()):
                if string is strs:
                    count = 1
                    break
            if count == 1:
                continue
                #다음에 올 단어후보중 하나이므로 추가
            examples.append(string)

    random.shuffle(examples)
    print('보기:',examples)

    return render_template('blankweb.html',question=ques,list=examples,correct=correct_answer)

if __name__ == '__main__':
    app.debug = True
    #app.run(host='0.0.0.0') # 외부 접속 가능하게 할때
    app.run() #로컬호스트 실험용

#웹 부분 종료