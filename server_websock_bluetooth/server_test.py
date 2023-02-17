import websockets, threading, asyncio
from queue import Queue
import random, sys, requests, os, json, time

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
GROUPS = ["a","d"]
domain=sys.argv[1]
limit = int(str(json.loads(requests.get(f"http://{domain}:8000/api/getRows").text)["number"])[1:-1])
questions = []

basic = {
    "command":"",
    "question":""
}


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


def add_question(r):
    global q
    global questions

    i = 0

    while i<r:
        elem = str(random.randint(1,limit))

        if elem not in questions:
            print(f"Added question {elem}")
            q.put(elem)
            questions.append(elem)
            i+=1

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

            if index >= len(GROUPS):
                reset()

                basic["command"] = "ready"
                basic["group"] = GROUPS[index]
                WORD=str(basic)

                print(f"Current Group: {GROUPS[index]}")

                if GROUPS[index] == "d":
                    add_question(final_q)
                else:
                    add_question(question_per_round)

                ready=True
                answered=True

            else:
                basic["command"] = "ready"
                basic["group"] = GROUPS[index]
                WORD=str(basic)

                print(f"Current Group: {GROUPS[index]}")

                add_question(question_per_round)

                ready=True

        elif c == "4":
            reset()

        else:
            if ready:
                if c == "1" and answered:
                    if not q.empty():

                        basic["command"] = "go"
                        basic["question"] = str(q.get())
                        basic["group"] = GROUPS[index]
                        WORD=str(basic)

                        sent=True
                        answered=False

                    else:
                        try:

                            w = requests.get(f"http://{domain}:8000/api/getWinner?group={GROUPS[index]}").text
                            
                            print(w)
                            
                            if (len(list(json.loads(w)["winners"])) > 30 and GROUPS[index] == "a") or (len(list(json.loads(w)["winners"])) > 15 and GROUPS[index] == "b") or (len(list(json.loads(w)["winners"])) > 5 and GROUPS[index] == "c"):
                                print("More questions!!")
                                add_question(1)

                            else:

                                id = list(json.loads(w)['winners'])
                                print(f"Queue is empty and we have a winner with id {id}!")

                                if GROUPS[index] == "d":
                                    basic["command"] = "final"
                                else:
                                    basic["command"] = "win"

                                basic["group"] = GROUPS[index]
                                basic["id"] = str(list(id))
                                WORD=str(basic)

                                print(WORD)

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
                        requests.get(f"http://{domain}:8000/api/startTimer")
                        sent=False
                        answered=True

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
