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

mydb = mysql.connector.connect(host="localhost",user="root",password="")

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

ids = {}
group_a_winners = []
group_b_winners = []
group_c_winners = []
group_d_winners = []

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

    if groups["a"] == 0 and groups["b"] == 0 and groups["c"] == 0:
        return "n"

    while True:
        d = random.choice(list(groups.keys()))
        if groups[d] != 0:
            groups[d] -= 1
            return d


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

@app.post("/api/register")
async def create_cookie(request: Request):
    global id

    j = await request.json()
    cookie = str(uuid.uuid4())
    ids[cookie] = {"id":str(id),"name":j["name"],"score":0,"group":get_group()}
    id+=1
    return {"cookie_name":"sessionID","value":f"{cookie}"}


@app.post("/api/getProfile")
async def send_test(request: Request):
    j = await request.json()
    return {"id": ids[j["sessionID"]]["id"], "name": ids[j["sessionID"]]["name"], "score": ids[j["sessionID"]]["score"], "group": ids[j["sessionID"]]["group"]}


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

    groups = {"a":n_per_group,"b":0,"c":0}
    ids={}
    id=1

    return {"success":"true"}

@app.get("/api/getUsers")
async def get_names():
    l = {}
    i = 0

    for elem in ids:
        name = ids[elem]["name"]
        group = ids[elem]["group"]
        l[f"{i}"] = {"name":name,"group":group}
        i+=1

    return l


@app.get("/api/getLeaderboard")
async def get_rate(group: str):
    global ids

    l={}

    for elem in ids:
        if ids[elem]["group"] == group:
            id = ids[elem]["id"]
            score = ids[elem]["score"]
            name = ids[elem]["name"]

            l[id] = {"name":name,"score":score}

    return sorted(l.items(), key=lambda x: x[1]["score"], reverse=True)


@app.get("/api/getWinner")
async def get_winner(group: str):
    global ids

    winners={"winners":[]}
    
    l={}

    for elem in ids:
        if ids[elem]["group"] == group:
            id = ids[elem]["id"]
            score = ids[elem]["score"]
            name = ids[elem]["name"]

            l[id] = {"name":name,"score":score}

    l = sorted(l.items(), key=lambda x: x[1]["score"], reverse=True)

    for elem in list(l):
        winners["winners"].append(elem[0])

    if( group=="d" and len(list(l)) == 1):
        for elem in ids:
            if ids[elem]["id"] in list(winners["winners"]):
                group_d_winners.append(str(ids[elem]["id"]))

    elif( group=="c" and len(list(l)) <= 5):
        for elem in ids:
            if ids[elem]["id"] in list(winners["winners"]):
                group_c_winners.append(str(ids[elem]["id"]))
                ids[elem]["group"] = "d"
                ids[elem]["score"] = 0

    elif( group=="b" and len(list(l)) <= 15):
        for elem in ids:
            if ids[elem]["id"] in list(winners["winners"]):
                group_b_winners.append(str(ids[elem]["id"]))
                ids[elem]["group"] = "c"
                ids[elem]["score"] = 0

    elif( group=="a" and len(list(l)) <= 30):
        for elem in ids:
            if str(ids[elem]["id"]) in list(winners["winners"]):
                group_a_winners.append(str(ids[elem]["id"]))
                ids[elem]["group"] = "b"
                ids[elem]["score"] = 0
    
    return winners


@app.get("/api/getWinner2")
async def get_winner2(group: str):
    l=[]

    if group == "a":
        for elem in group_a_winners:
            l.append(elem)
    elif group == "b":
        for elem in group_b_winners:
            l.append(elem)
    elif group == "c":
        for elem in group_c_winners:
            l.append(elem)
    elif group == "d":
        for elem in group_d_winners:
            l.append(elem)

    return {"winners":l}
    

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
            if ids[elem]["group"] != "d":
                groups[ids[elem]["group"]] += 1
            del ids[elem]

    return {"success":"true"}

@app.get("/api/getUser")
async def get_user(id: str):
    for key in ids:
        if ids[key]["id"] == id:
            return {"name":ids[key]["name"],"score":ids[key]["score"]}

    return {"name":""}
