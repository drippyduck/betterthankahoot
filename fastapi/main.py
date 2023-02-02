from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import uuid
import pandas as pd
import xlsxwriter
import mysql.connector

mydb = mysql.connector.connect(host="localhost",user="root",password="")

mycursor = mydb.cursor()

mycursor.execute("USE quiz;")

def get_question(id):
    mycursor.execute(f"SELECT * FROM questions WHERE id = {id};")
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

id=1

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

    while True:
        d = random.choice(list(groups.keys()))
        if groups[d] != 0:
            groups[d] -= 1
            return d


@app.get("/")
async def root():
    return {"message": "Hello"}

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
async def send_quest(id: int):
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



@app.get("/api/changeGroup")
async def change_grp(id: str):
    global ids

    for key in ids:
        if ids[key]["id"] == id:
            ids[key]["group"] = "d"

    return {"success":"true"}


@app.get("/api/getWinner")
async def get_winner(group: str):
    global ids

    winners={"winners":[]}

    max = 0
    for key in ids:
        if ids[key]["score"] > max and ids[key]["group"] == group:
            max = ids[key]["score"]

    for key in ids:
        if ids[key]["score"] == max:
            winners["winners"].append(ids[key]["id"])

    if len(winners["winners"]) == 1:
        tmp_id = winners["winners"][0]

        for key in ids:
            if ids[key]["id"] == tmp_id:
                if ids[key]["group"] != "d":
                    ids[key]["group"] = "d"
                    ids[key]["score"] = 0
                
    return winners
    

@app.post("/api/submitAnswer")
async def send_answer(request: Request):
    global rates
    
    j = await request.json()
    
    q = int(j["question"])
    mycursor.execute(f"SELECT answer FROM questions WHERE id = {q};")

    if j["answer"] == mycursor.fetchone()[0]:
        ids[j["sessionID"]]["score"] += int(j["score"])

    if j["answer"] == "a":
        rates["a"] += 1
    elif j["answer"] == "b":
        rates["b"] += 1
    elif j["answer"] == "c":
        rates["c"] += 1
    elif j["answer"] == "d":
        rates["d"] += 1

    return {"success":"true"}

@app.get("/api/getUser")
async def get_user(id: str):
    for key in ids:
        if ids[key]["id"] == id:
            return {"name":ids[key]["name"],"score":ids[key]["score"]}

    return {"name":""}
