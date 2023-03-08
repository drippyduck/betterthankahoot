import websockets, threading, asyncio
from queue import Queue
import random, sys, requests, os, json, time
import mysql.connector

q = Queue()

CLIENTS = set()
WORD = ''
count = 0
ready=False
sent=False
answered=True
index = 0
question_per_round = 1
final_q = 1
GROUPS = ["a","b","c","d"]
domain=sys.argv[1]
limit = int(str(json.loads(requests.get(f"http://{domain}:8000/api/getRows").text)["number"])[1:-1])
questions = []

mydb = mysql.connector.connect(host="localhost",user="root",password="root")

mycursor = mydb.cursor()

mycursor.execute("USE quiz;")

basic = {
    "command":"",
    "question":""
}

def add_question(r):
    global q
    global questions
    l=[]
    i = 0

    mycursor.execute(f"SELECT id FROM questions WHERE category = '{GROUPS[index]}';")

    for elem in mycursor.fetchall():
        l.append(str(elem[0]))

    print("Questions: "+str(l))

    while i<r:
        elem = str(random.choice(l))

        if elem not in questions:
            print(f"Added question {elem}")
            q.put(elem)
            questions.append(elem)
            i+=1

def reset():
    global WORD
    global basic
    global count
    global CLIENTS
    global ready
    global sent
    global index
    global question_per_round
    global GROUPS
    global q
    global questions
    global answered

    requests.get(f"http://{domain}:8000/api/getReset")
                    
    ready=False
    sent=False
    answered=True
    count=0
    basic["command"] = "close"
    WORD=str(basic)
    basic = {
        "command":"",
        "question":""
    }
    index=0
    with q.mutex: q.queue.clear()
    questions.clear()


def start_timer():
    global sent
    global answered
    
    requests.get(f"http://{domain}:8000/api/startTimer")
    print("FInished timwer")
    sent=False
    answered=True

def input_loop():
    global WORD
    global basic
    global count
    global CLIENTS
    global ready
    global sent
    global index
    global question_per_round
    global GROUPS
    global answered

    while True:
        print("0: Ready\n1: Send question / Get winners \n2:Show board\n4: Reset\n5: Start")
        c=input(">> ")

        if c == "0" and not ready:

                basic["command"] = "ready"
                basic["group"] = GROUPS[index]
                WORD=str(basic)

                print(f"Current Group: {GROUPS[index]}")

                add_question(question_per_round)

                ready=True
                answered=True

        elif c == "4":
            reset()

            basic["command"] = "reset"
            basic["count"] = len(CLIENTS)
            WORD=str(basic)

        else:
            if ready:
                if c == "1" and answered:
                    if not q.empty():

                        basic["command"] = "go"
                        basic["question"] = str(q.get())
                        basic["group"] = GROUPS[index]
                        WORD=str(basic)

                        print(f"Sent question to group {GROUPS[index]}")
                        sent=True
                        answered=False

                    else:
                        try:

                            w = list(json.loads(requests.get(f"http://{domain}:8000/api/getWinner?group={GROUPS[index]}").text)["winners"])

                            #print(f"{w} : {len(w)}")
                            
                            if (len(w) > 30 and GROUPS[index] == "a") or (len(w) > 15 and GROUPS[index] == "b") or (len(w) > 5 and GROUPS[index] == "c") or (len(w) > 1 and GROUPS[index] == "d"):
                                print("More questions!!")
                                add_question(1)

                                if GROUPS[index] == "d":
                                    basic["command"] = "final"
                                else:
                                    basic["command"] = "win"

                                WORD = str(basic)
                                ready=True

                            else:

                                print(f"Queue is empty and we can move to next round!")

                                if GROUPS[index] == "d":
                                    basic["command"] = "final"
                                else:
                                    basic["command"] = "win"

                                basic["group"] = GROUPS[index]
                                WORD=str(basic)

                                ready=False
                                index += 1

                        except:

                            print("Empty group")
                            ready=False
                            index += 1

                elif c == "2":
                    
                    basic["command"] = "board"
                    WORD=str(basic)


                elif c == "5" and not answered:

                    if not sent:
                        print("Question not sent!")
                    else:
                        basic["command"] = "start"
                        basic["group"] = GROUPS[index]
                        WORD=str(basic)

                        time.sleep(1)
                        threading.Thread(target=start_timer).start()

                else:
                    print("Not ready!")

                    
async def broadcast(message):
    global WORD
    global basic

    for websocket in CLIENTS.copy():
        try:
            await websocket.send(message)
        except websockets.ConnectionClosed:
            CLIENTS.remove(websocket)

            basic["command"] = "new"
            basic["count"] = len(CLIENTS)

            WORD=str(basic)

            await broadcast(WORD)
        
    WORD=''

async def handler(websocket):
    global WORD
    global count

    CLIENTS.add(websocket)

    basic["command"] = "new"
    basic["count"] = len(CLIENTS)

    WORD=str(basic)

    try:
        await websocket.wait_closed()
    except:
        CLIENTS.remove(websocket)

        basic["command"] = "new"
        basic["count"] = len(CLIENTS)

        WORD=str(basic)

async def full():
    while True:
        await asyncio.sleep(1)
        await broadcast(WORD)



async def main():
    async with websockets.serve(handler, domain, 5555):
        await full()

if __name__ == "__main__":
    threading.Thread(target=input_loop).start()
    asyncio.run(main())
