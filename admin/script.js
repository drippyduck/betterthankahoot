var domain='192.168.11.106'
const ws = new WebSocket(`ws://${domain}:5555`);
var keyword = "b0657d3289bae5be59176613e794ae1bf696c7e2ee529058760fe0b17b0d448f";

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

async function change_state()
{
    if(document.getElementById("main_input").value != '')
    {
        if(document.getElementById("message").style.opacity=="1")
        {
            document.getElementById("message").style.opacity = "0";
            await sleep(500);
        }
        
        document.getElementById("main").style.top = "120%";
        await sleep(500);
        document.getElementById("titles").style.opacity = "0";
        connect_all();
    }
    else
    {
        document.getElementById("alert").innerText = "You have to enter your name!";
        document.getElementById("message").style.opacity = "1";
    }
}

async function update_score(score_arg)
{
    document.getElementById("score").style.opacity = "0";
    await sleep(500);
    document.getElementById("score").innerText = `Score: ${score_arg}`;
    await sleep(500);
    document.getElementById("score").style.opacity = "1";
}

async function update_alert(message)
{
    document.getElementById("main_m2").style.opacity = "0";
    document.getElementById("message").style.opacity = "0";
    await sleep(500);
    document.getElementById("alert").innerText = `${message}`;
    await sleep(500);
    document.getElementById("message").style.opacity = "1";
}

async function update_m2(message)
{
    document.getElementById("timer").style.opacity = "0";
    document.getElementById("message").style.opacity = "0";
    document.getElementById("buttons").style.opacity = "0";
    document.getElementById("main_m2").style.opacity = "0";

    await sleep(500);
    document.getElementById("main_m2").innerText = `${message}`;
    await sleep(500);
    document.getElementById("main_m2").style.opacity = "1";
}

async function spawn_buttons(a,b,c,d)
{
    document.getElementById("leader").style.opacity = "0";

    document.getElementById("a").innerText = `${a}`;
    document.getElementById("b").innerText = `${b}`;
    document.getElementById("c").innerText = `${c}`;
    document.getElementById("d").innerText = `${d}`;

    document.getElementById("buttons").style.opacity = "1";
}

async function update_profile(a,b,c)
{
    document.getElementById("profile").style.opacity = "0";

    document.getElementById("name").innerText = `Name: ${a}`;
    document.getElementById("group").innerText = `Group: ${b}`;
    document.getElementById("score").innerText = `Score: ${c}`;

    document.getElementById("profile").style.opacity = "1";
}

// main.js part

var xhr;
var sentence;
var question;
var canAnswer = false;
let score=0;
let last_score=0;
var c;
var uuid;
var selected=0;
var ready = false;
var group;
var id;
var s=false;
var ans=0;
var winner = '';
var users = [];

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

async function start_timer()
{
    var max = 10;
    document.getElementById("timer").style.backgroundColor = "green";

    for (let step = 0; step < max; step++) 
    {
        document.getElementById("t").innerText = `${max - step}`;
        score=(max-step)*100;
        await sleep(1000);
    }

    document.getElementById("t").innerText = `UP`;
    document.getElementById("timer").style.backgroundColor = "red";

    await sleep(1000);

    show_rate();

    score=0;
    canAnswer = false;
}

function connect_all()
{
    ws.addEventListener("open", async () =>{
        //document.getElementById("socket").innerHTML = "<h1>Connected</h1>";
        await update_m2("Waiting to start");
        await sleep(500);
    });

    ws.addEventListener('close', async function () {
        await update_m2("Disconnected, please return to main menu and try again");
        await sleep(500);
    });

    ws.addEventListener('message', async function (event) {
        if(event.data!='')
        {
            var j = JSON.parse(event.data.replaceAll(`'`, `"`));

            if(j.group)
            {
                group=j.group;
            }

            if(j.command == "ready")
            {
                document.getElementById("board").style.opacity = "0";

                if(j.group == "d")
                    await update_m2(`Starting Finals`);
                else
                    await update_m2(`Starting for group: ${j.group}`);

                ready=true;
            }
            else if(j.command == "new")
            {
                show_names(j.count);
            }
            else if(j.command == "board")
            {
                show_board();
            }
            
            if(ready)
            {
                if(j.command == "go")
                {
                    question = j.question;
                    get_question();
                }
                else if(j.command == "start")
                {
                    score=0;
                    canAnswer=true;
                    await start_timer();
                }
                else if(j.command == "win")
                {
                    xhr = new XMLHttpRequest();
                    xhr.open("GET", `http://${domain}:8000/api/getUser?id=${j.id}`, true);
                    xhr.send();

                    xhr.onload = async function(){
                        var l = JSON.parse(xhr.responseText);
                        await update_m2(`Group ${j.group} Leaderboard:`);
                        show_board_final();
                    }

                    group="d";
                }
                else if(j.command == "final")
                {
                    xhr = new XMLHttpRequest();
                    xhr.open("GET", `http://${domain}:8000/api/getUser?id=${j.id}`, true);
                    xhr.send();

                    xhr.onload = async function(){
                        var l = JSON.parse(xhr.responseText);
                        await update_m2(`Finals Leaderboard:`);
                        show_board_final();
                    }
                    
                }
            }

        }
    });
}

function get_question()
{
    if(ans!=0)
    {
        document.getElementById(ans).style.cssText = `
                border-color: black;
                border-width: 3px;
            `
        s=false;
    }
    else
    {
        document.getElementById("rates").style.opacity = "0";
        document.getElementById("buttons").style.top = "60%";
    }

    const value = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://${domain}:8000/api/getQuestion?id=${question}`, true);
    xhr.send(`{"sessionID":"${value}"}`);

    xhr.onload = async function() {
        const obj = JSON.parse(xhr.responseText);
        update_alert(`Question ${question} : ${obj.content}`);
        await sleep(1000);
        spawn_buttons(obj.a,obj.b,obj.c,obj.d);
        document.getElementById("t").innerText = `10`;
        document.getElementById("timer").style.backgroundColor = "lightblue";
        await sleep(500);
        document.getElementById("timer").style.opacity = "1";
    }
}


function show_rate()
{
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://${domain}:8000/api/hxhx?code=${keyword}&question=${question}`, true);
    xhr.send();
    
    xhr.onload = function() 
    {
        var txt = JSON.parse(xhr.responseText);

        answer = txt.answer;

        document.getElementById(`rate_${String(answer)}`).style.borderColor = `green`;
        document.getElementById(`rate_${String(answer)}`).style.borderWidth = `15px`;

        xhr = new XMLHttpRequest();
        xhr.open("GET", `http://${domain}:8000/api/getRates`, true);
        xhr.send();

        xhr.onload = async function(){
            var t = JSON.parse(xhr.responseText);
        
            var total = t.a + t.b + t.c + t.d;
        
        if(total===0)
        {
           total = 1;
        }
        
            a = Math.trunc((t.a*100)/total);
            b = Math.trunc((t.b*100)/total);
            c = Math.trunc((t.c*100)/total);
            d = Math.trunc((t.d*100)/total);
        
        //alert(`total: ${total} a ${t.a} b ${t.b} c ${t.c} d ${t.d}`);
            
            document.getElementById("rate_a").innerHTML = `<h1>${a}%</h1>`;
            document.getElementById("rate_b").innerHTML = `<h1>${b}%</h1>`;
            document.getElementById("rate_c").innerHTML = `<h1>${c}%</h1>`;
            document.getElementById("rate_d").innerHTML = `<h1>${d}%</h1>`;

            document.getElementById("rate_a").style.width = `${(a*3)+43}%`;
            document.getElementById("rate_b").style.width = `${(b*3)+43}%`;
            document.getElementById("rate_c").style.width = `${(c*3)+43}%`;
            document.getElementById("rate_d").style.width = `${(d*3)+43}%`;

            document.getElementById("message").style.opacity = "0";
            document.getElementById("rates").style.opacity = "1";
            document.getElementById("buttons").style.opacity = "0";  
        }
    }
}

function show_board()
{
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://${domain}:8000/api/getLeaderboard?group=${group}`, true);
    xhr.send();

    xhr.onload = async function(){

        document.getElementById("leader").style.opacity = "0";

        var elem = ["message","buttons","timer","leader","rates"];
        var elems2  = [];

        elem.forEach(function(dv)
        {
            // check if visible, if yes opacity = 0
            var l = window.getComputedStyle(document.getElementById(dv)).opacity.toString();
            
            if(l.localeCompare("0"))
            {
                elems2.push(dv);
                document.getElementById(dv).style.opacity = "0";
            }
            // else remove from lise
        });

        var l = JSON.parse(xhr.responseText);
        var s;

        if(l.length>5)
        {
            s=5;
        }
        else
        {
            s=l.length;
        }

        document.getElementById("board").innerHTML = ``;

        for (let step = 0; step < s; step++) 
        {
            var values = Object.values(l[step][1]);

            var name = values[0];
            var score = values[1];

            document.getElementById("board").innerHTML += `<h1 id="ranki">${step+1} : ${name} Score: ${score}</h1>`;

        }

        await sleep(1000);

        document.getElementById("board").style.opacity = "1";

        await sleep(2000);

        document.getElementById("board").style.opacity = "0";


        for ( var i=0; i<elems2.length; i++)
        {
            document.getElementById(elems2[i]).style.opacity = "1";
        }

    }
}

function show_board_final()
{
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://${domain}:8000/api/getLeaderboard?group=${group}`, true);
    xhr.send();

    xhr.onload = async function(){

        document.getElementById("leader").style.opacity = "0";

        var elem = ["message","buttons","timer","leader","rates"];
        var elems2  = [];

        elem.forEach(function(dv)
        {
            // check if visible, if yes opacity = 0
            var l = window.getComputedStyle(document.getElementById(dv)).opacity.toString();
            
            if(l.localeCompare("0"))
            {
                elems2.push(dv);
                document.getElementById(dv).style.opacity = "0";
            }
            // else remove from lise
        });

        var l = JSON.parse(xhr.responseText);
        var s;

        if(l.length>5)
        {
            s=5;
        }
        else
        {
            s=l.length;
        }

        document.getElementById("board").innerHTML = ``;

        for (let step = 0; step < s; step++) 
        {
            var values = Object.values(l[step][1]);

            var name = values[0];
            var score = values[1];

            document.getElementById("board").innerHTML += `<h1 id="ranki">${step+1} : ${name} Score: ${score}</h1>`;

        }

        await sleep(1000);

        document.getElementById("board").style.opacity = "1";
    }
}

function show_names(c)
{
    xhr = new XMLHttpRequest();
    xhr.open("GET", `http://${domain}:8000/api/getUsers`, true);
    xhr.send();

    xhr.onload = function(){
        var l = JSON.parse(xhr.responseText);

        document.getElementById(`group_a`).innerHTML = ``;
        document.getElementById(`group_b`).innerHTML = ``;
        document.getElementById(`group_c`).innerHTML = ``;

        for (let step = 0; step < c-1; step++) 
        {
            n = l[`${step}`].name;
            g = l[`${step}`].group;

            if(!(users.includes(n))){
                users.push(n);
            }

            document.getElementById(`group_${g}`).innerHTML += `<h3 id="item">${n}</h3>`;
        }
        
    }
}

function hover(obj)
{
    if(!s)
    {
        document.getElementById(obj.id).style.cssText = `
            border-color: cyan;
            border-width: 5px;
        `
    }
}

function leave(obj)
{
    if(!s)
    {
        document.getElementById(obj.id).style.cssText = `
            border-color: black;
            border-width: 3px;
        `
    }
}

function reset()
{
    if(ws.readyState !== WebSocket.CLOSED)
    {
        ws.close();
    }
    
    window.location.reload();
}

connect_all();
  
