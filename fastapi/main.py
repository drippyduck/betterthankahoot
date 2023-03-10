from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import uuid
import pandas as pd
import xlsxwriter
import mysql.connector
import time
import asyncio

valid = ["1","2","3","4","5","6","7","8","9"]

def sanitize(word):
    
    s=""

    for elem in word.replace(" ",""):
        if elem.strip() in valid:
            s+=elem.strip()

    return s

mydb = mysql.connector.connect(host="localhost",user="root",password="root")

mycursor = mydb.cursor()

mycursor.execute("USE quiz;")

def get_question(id):
    mycursor.execute(f"SELECT * FROM questions WHERE id = {sanitize(id)};")
    print(id)
    res = mycursor.fetchone()
    j = {"content":res[1],"a":res[2],"b":res[3],"c":res[4],"d":res[5]}
    return j

def get_all_questions():
    mycursor.execute(f"SELECT * FROM questions;")
    return mycursor.fetchall()

def insert_question(content,a,b,c,d,answer):
    mycursor.execute(f"INSERT INTO `questions`(`content`, `a`, `b`, `c`, `d`, `answer`) VALUES ('{str(content)}','{str(a)}','{str(b)}','{str(c)}','{str(d)}','{str(answer)}')")

rates = {
    "a": 0,
    "b": 0,
    "c": 0,
    "d": 0
}

n_per_group = 2

groups = {
    "a" : n_per_group,
    "b" : 0,
    "c" : 0
}

g2 = ["a","b","c","d","f"]

ids2 = {"test1":{"id":"40","name":"test1","last":"tester1","score":0,"code":"111111","group":"a"},
       "test2":{"id":"41","name":"test2","last":"tester2","score":10,"code":"111111","group":"a"},
       "test3":{"id":"42","name":"test3","last":"tester3","score":20,"code":"111111","group":"a"},
       "test4":{"id":"43","name":"test4","last":"tester4","score":30,"code":"111111","group":"a"},
       "test5":{"id":"44","name":"test5","last":"tester5","score":40,"code":"111111","group":"a"}}

ids = {"test1":{"id":"40","name":"ewq123ewq","last":"alewq123ewq123","score":0,"code":"111111","group":"a"},
       "test2":{"id":"41","name":"ewq123ewq","last":"alewq123ewq123","score":0,"code":"111112","group":"a"}}

codes = []

id=1
stat=0

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_group():
    global groups

    if groups["a"] == 0:
        return "n"
    else:
        groups["a"] -= 1
        return "a"


@app.get("/")
async def root():
    return {"message": "Hello"}

@app.get("/api/startTimer")
async def start_timer():
    global stat
    
    for i in range(10):
        stat=10-i
        await asyncio.sleep(1)

    stat=0
    return {"success":"true"}

@app.get("/api/getRows")
async def get_rows():
    mycursor.execute(f"SELECT COUNT(*) FROM questions;")
    res = mycursor.fetchone()
    return {"number":res}

def fetch_user(code):
    mycursor.execute(f"SELECT first,last FROM players WHERE code LIKE '{code.upper()}';")
    res = mycursor.fetchone()
    return {"first":res[0],"last":res[1]}

@app.post("/api/register")
async def create_cookie(request: Request):
    global id
    j = await request.json()
    code = j["code"]
    l = fetch_user(code)

    cookie = str(uuid.uuid4())
    ids[cookie] = {"id":str(id),"name":l["first"],"last":l["last"],"score":0,"code":code,"group":get_group()}
    id+=1
    return {"cookie_name":"sessionID","value":f"{cookie}"}


@app.post("/api/getProfile")
async def send_test(request: Request):
    j = await request.json()
    return {"id": ids[j["sessionID"]]["id"], "name": ids[j["sessionID"]]["name"],"last": ids[j["sessionID"]]["last"], "score": ids[j["sessionID"]]["score"], "group": ids[j["sessionID"]]["group"]}


@app.get("/api/getQuestion")
async def send_quest(id: str):
    global rates
    rates = {"a": 0,"b": 0,"c": 0,"d": 0}
    return get_question(id)


@app.get("/api/getRates")
async def get_rate():
    return rates

@app.get("/api/getReset")
def get_reset():
    global groups
    global ids
    global id
    global n_per_group

    groups = {"a":n_per_group,"b":0,"c":0,"d":0}
    ids={}
    codes.clear()
    id=1

    return {"success":"true"}

@app.get("/api/getUsers")
async def get_names():
    l = {}
    i = 0

    for elem in ids:
        name = ids[elem]["name"]
        last = ids[elem]["last"]
        group = ids[elem]["group"]
        l[f"{i}"] = {"name":name,"last":last,"group":group}
        i+=1

    return l


@app.get("/api/getLeaderboard")
async def get_rate(group: str):
    global ids

    l={}

    index = g2.index(group)
    index2 = index + 1

    for elem in ids:
        if ids[elem]["group"] == g2[index] or ids[elem]["group"] == g2[index2]:
            id = ids[elem]["id"]
            score = ids[elem]["score"]
            name = ids[elem]["name"]
            last = ids[elem]["last"]
            group = ids[elem]["group"]

            l[id] = {"name":name,"last":last,"score":score,"group":group}

    return sorted(l.items(), key=lambda x: x[1]["score"], reverse=True)


@app.get("/api/getWinner")
async def get_winner(group: str):
    global ids

    winners={"winners":[]}

    if group == "a":
        wanted = 30
    elif group == "b":
        wanted = 15
    elif group == "c":
        wanted = 5
    elif group == "d":
        wanted = 1

    last_score = 0
    
    l={}

    for elem in ids:
        if ids[elem]["group"] == group:
            id = ids[elem]["id"]
            score = ids[elem]["score"]
            name = ids[elem]["name"]

            l[id] = {"name":name,"score":score}

    l = sorted(l.items(), key=lambda x: x[1]["score"], reverse=True)
    new = l
    next = []

    for i in range(len(new)):
                score = l[i][1]["score"]
                    
                if i+1 == wanted:
                    last_score = score
                elif i+1 > wanted and score != last_score:
                    
                    for key in ids:
                        if ids[key]["id"] == str(l[i][0]):
                            ids[key]["group"] = "l"

                    next.append(l[i])

    for elem in next:
        l.remove(elem)

    for elem in list(l):
        winners["winners"].append(elem)
        
    if( group=="d" and len(list(l)) == 1):

        for elem in ids:
            for e in list(l):
                if ids[elem]["id"] == e[0]:
                    ids[elem]["group"] = "f"
                    ids[elem]["score"] = 0

    elif( group=="c" and len(list(l)) <= 5):

        for elem in ids:
            for e in list(l):
                if ids[elem]["id"] == e[0]:
                    ids[elem]["group"] = "d"
                    ids[elem]["score"] = 0

    elif( group=="b" and len(list(l)) <= 15):

        for elem in ids:
            for e in list(l):
                if ids[elem]["id"] == e[0]:
                    ids[elem]["group"] = "c"
                    ids[elem]["score"] = 0

    elif( group=="a" and len(list(l)) <= 30):

        for elem in ids:
            for e in list(l):
                if ids[elem]["id"] == e[0]:
                    ids[elem]["group"] = "b"
                    ids[elem]["score"] = 0
                
    
    return winners
    

@app.post("/api/submitAnswer")
async def send_answer(request: Request):
    global rates
    global stat
    
    j = await request.json()
    
    q = int(j["question"])
    mycursor.execute(f"SELECT answer FROM questions WHERE id = {q};")

    if j["answer"] == mycursor.fetchone()[0]:
        if int(stat)!=10:
            ids[j["sessionID"]]["score"] += int(stat*100)-100
        else:
            ids[j["sessionID"]]["score"] += int(stat*100)

    if j["answer"] == "a":
        rates["a"] += 1
    elif j["answer"] == "b":
        rates["b"] += 1
    elif j["answer"] == "c":
        rates["c"] += 1
    elif j["answer"] == "d":
        rates["d"] += 1

    return {"success":"true"}

@app.get("/api/hxhx")
async def get_answer(code: str, question: str):
    if code == "b0657d3289bae5be59176613e794ae1bf696c7e2ee529058760fe0b17b0d448f":
        q = int(question)
        mycursor.execute(f"SELECT answer FROM questions WHERE id = {q};")
        return {"answer":f"{str(mycursor.fetchone()[0])}"}

@app.post("/api/disconnect")
async def disconnect(request: Request):
    global rates
    global stat
    
    j = await request.json()
    
    q = j["sessionID"]

    for elem in ids.copy():
        if elem == q:
            if ids[elem]["group"] != "f":
                groups[ids[elem]["group"]] += 1
            codes.remove(ids[elem]["code"])
            del ids[elem]

    return {"success":"true"}

@app.get("/api/checkName")
async def get_user(name: str):
    if len(name) > 12:
        return {"success":"false"}

    for key in ids:
        if ids[key]["name"] == name:
            return {"success":"false"}

    return {"success":"true"}

@app.get("/api/checkCode")
async def check_code(code: str):
    global codes

    mycursor.execute(f"SELECT first,last FROM players WHERE code LIKE '{code.upper()}';")
    res = mycursor.fetchone()
    if res and code not in codes:
        codes.append(code)
        return {"success":"true"}
    else:  
        return {"success":"false"}

@app.get("/api/getUser")
async def get_user(id: str):
    for key in ids:
        if ids[key]["id"] == id:
            return {"name":ids[key]["name"],"score":ids[key]["score"],"group":ids[key]["group"]}

    return {"name":""}
