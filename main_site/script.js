var domain='192.168.11.107'
var ws;

/*if(!(navigator.userAgent.match(/firefox/i)))
{
    //update_m2('Please use a firefox or safari browser!');
    //document.getElementById("main").style.display = "none";
    //document.getElementById("main").style.top = "250%";
}*/

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

        xhr = new XMLHttpRequest();
        xhr.open("GET", `http://${domain}:8000/api/checkCode?code=${document.getElementById("main_input").value}`, true);
        xhr.send();

        xhr.onload = async function() {
            var resp = xhr.responseText;
            var s = JSON.parse(resp).success;

            if (s == "true")
            {
                
                document.getElementById("main").style.top = "250%";
                document.getElementById("m2").style.display = "none";
                document.getElementById("logo").style.opacity = "0";
                await sleep(500);
                connect_all();
            }
            else
            {
                document.getElementById("r2").innerText = "Invalid Code or session already active";
                document.getElementById("m2").style.opacity = "1";
            }
        }
    }
    else
    {
        document.getElementById("r2").innerText = "You have to enter your name!";
        document.getElementById("m2").style.opacity = "1";
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

    /*
    var l = parseInt(document.getElementById("alert").innerText.length);

    if(l<=100)
    {
        document.getElementById("alert").style.cssText = "font-size: 180%;font-size: 2.5vh;";
    }
    else if(l<=200)
    {
        document.getElementById("alert").style.cssText = "font-size: 145%;font-size: 2.5vh;";
    }
    else if(l<=300)
    {
        document.getElementById("alert").style.cssText = "font-size: 115%;font-size: 3vh;";
    }
    else
    {
        document.getElementById("alert").style.cssText = "font-size: 75%;font-size: 3.5vh;";
    } 
    */

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
    document.getElementById("a").style.cssText = `
    border-color: black;
    border-width: 5px;
    box-shadow: 5px 10px black;
        `
    document.getElementById("b").style.cssText = `
    border-color: black;
    border-width: 5px;
    box-shadow: 5px 10px black;
    `
    document.getElementById("c").style.cssText = `
    border-color: black;
    border-width: 5px;
    box-shadow: 5px 10px black;
    `
    document.getElementById("d").style.cssText = `
    border-color: black;
    border-width: 5px;
    box-shadow: 5px 10px black;
    `
    document.getElementById("a").innerText = `${a}`;
    document.getElementById("b").innerText = `${b}`;
    document.getElementById("c").innerText = `${c}`;
    document.getElementById("d").innerText = `${d}`;

    document.getElementById("buttons").style.opacity = "1";

    await sleep(1000);
    document.getElementById("a").style.opacity = "1";
    await sleep(1000);
    document.getElementById("b").style.opacity = "1";
    await sleep(1000);
    document.getElementById("c").style.opacity = "1";
    await sleep(1000);
    document.getElementById("d").style.opacity = "1";
}

async function update_profile(a,a1,b,c)
{
    document.getElementById("profile").style.opacity = "0";

    document.getElementById("name").innerText = `Name: ${a} ${a1}`;

    if(b=="d")
    {
        document.getElementById("group").innerText = `Rank: Top 5`;
    }
    else if(b=="c")
    {
        document.getElementById("group").innerText = `Rank: Top 15`;
    }
    else if(b=="b")
    {
        document.getElementById("group").innerText = `Rank: Top 30`;
    }
    else if(b=="a")
    {
        document.getElementById("group").innerText = `Rank: Top 60-80`;
    }
        
    document.getElementById("score").innerText = `Score: ${c}`;

    document.getElementById("profile").style.opacity = "1";
}

function spawn_fireworks()
{
    document.getElementById("f1").style.display = `grid`;
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
var index=0;
var groups = ["a","b","c","d"];

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
    score=0;
    selected=1;
    canAnswer = false;
}

async function advance()
{
    var phrase;
    index+=1;

    if(groups[index]=="b")
    {
        phrase="You made it to top 30!";
    }
    else if(groups[index]=="c")
    {
        phrase="You made it to top 15!"
    }
    else
    {
        phrase="You made it to top 5!"
    }


    await update_m2(phrase);
    
    group=groups[index];
    get_profile_v2();
}

function reset_op()
{
    document.getElementById("buttons").style.opacity = "0";
    document.getElementById("a").style.opacity = "0";
    document.getElementById("b").style.opacity = "0";
    document.getElementById("c").style.opacity = "0";
    document.getElementById("d").style.opacity = "0";
}

function connect_all()
{
    xhr = new XMLHttpRequest();
    var name = document.getElementById("main_input").value;
    xhr.open("POST", `http://${domain}:8000/api/register`, true);
    xhr.send(`{"code":"${name}"}`);
    document.cookie=``;

    xhr.onload = function() {
            var resp = xhr.responseText;
            const myObj = JSON.parse(resp);
            var name = myObj.cookie_name;
            var value = myObj.value;
            document.cookie = `${name}=${value};SameSite=Secure`
    }

    ws = new WebSocket(`ws://${domain}:5555`);

    ws.addEventListener("open", async () =>{
        //document.getElementById("socket").innerHTML = "<h1>Connected</h1>";
        await update_m2("Waiting to start");
        await sleep(500);
        get_profile();
    });

    ws.addEventListener('close', async function () {
        await update_m2("Disconnected, please return to main menu and try again");
        await sleep(500);
    });

    ws.addEventListener('message', async function (event) {
        if(event.data!='')
        {
            var j = JSON.parse(event.data.replaceAll(`'`, `"`));
            
            if(ready && j.group == group)
            {
                
                if(j.command == "go")
                {
                    question = j.question;
                    reset_op();
                    get_question();
                }
                else if(j.command == "start")
                {
                    score=0;
                    //await update_m2("Go");
                    canAnswer=true;
                    await start_timer();
                    get_profile();
                }
                else if(j.command == "win")
                {
                    xhr = new XMLHttpRequest();
                    xhr.open("GET", `http://${domain}:8000/api/getUser?id=${id}`, true);
                    xhr.send();

                    xhr.onload = async function() {
                        var resp = xhr.responseText;
                        var g = JSON.parse(resp).group;
                        
                        if(g == groups[index+1])
                        {
                            advance();
                        }
                        else if(g == "l")
                        {
                            await update_m2("You lost!");
                            await sleep(10000);
                            window.location.reload();
                        }
                        else
                        {
                            await update_m2("Waiting for extra questions...");
                        }
                    }
                }
                else if(j.command == "final")
                {
                    xhr = new XMLHttpRequest();
                    xhr.open("GET", `http://${domain}:8000/api/getUser?id=${id}`, true);
                    xhr.send();

                    xhr.onload = async function() {
                        var resp = xhr.responseText;
                        var g = JSON.parse(resp).group;

                        if(g == "f")
                        {
                            await update_m2("Finals winner!");
                            spawn_fireworks();
                            //await sleep(10000);
                            //window.location.reload();
                        }
                        else
                        {
                            await update_m2("Lost final!");
                            await sleep(10000);
                            window.location.reload();
                        }
                    }
                }
            }
        
            if(j.command == "ready" && j.group == group)
            {
                await update_m2("Starting...");
                ready=true;
            }
            
            if(j.command == "close")
            {
                ws.close();
            }
            else if(j.command == "reset")
            {
                ws.close();
            }

        }
    });
}

function get_profile()
{
    const v = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];

    xhr = new XMLHttpRequest();
    xhr.open("POST", `http://${domain}:8000/api/getProfile`, true);
    xhr.send(`{"sessionID":"${v}"}`);

    xhr.onload = async function() 
    {
        var txt = JSON.parse(xhr.responseText);

        score = txt.score;
        group=txt.group;
        id=txt.id;

        if(group==="n")
        {
            update_m2('Lobby is full, please wait then try again...');
            document.getElementById("main").style.display = "none";
            document.getElementById("main").style.top = "250%";
            return;
        }

        if(selected!=0)
        {
            if(score!=last_score)
            {
                //document.getElementById("question").innerHTML = `<h1>correct</h1>`;
                await sleep(1000);
                await update_m2("Correct!");
                update_profile(txt.name,txt.last,txt.group,txt.score);
            }else
            {
                //document.getElementById("question").innerHTML = `<h1>incorrect</h1>`;
                await sleep(1000);
                await update_m2("False!");
                update_profile(txt.name,txt.last,txt.group,txt.score);
            }
        }
        else
        {
            update_profile(txt.name,txt.last,txt.group,txt.score);
        }

        last_score=score;
    }
}

function get_profile_v2()
{
    const v = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];

    xhr = new XMLHttpRequest();
    xhr.open("POST", `http://${domain}:8000/api/getProfile`, true);
    xhr.send(`{"sessionID":"${v}"}`);

    xhr.onload = async function() 
    {
        var txt = JSON.parse(xhr.responseText);

        score = txt.score;
        group=txt.group;
        id=txt.id;

        update_profile(txt.name,txt.last,txt.group,txt.score);

        last_score=score;
    }
}

function send_answer(a,obj)
{
    if(!canAnswer)
        return;

    if(!s)
    {
        document.getElementById(obj.id).style.cssText = `
            box-shadow: 0 0 5px 5px #00ffff;
            border-width: 5px;
            opacity: 1;
        `
        s=true;
        ans=obj.id;
    }

    selected=1;
    const value = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];

    xhr = new XMLHttpRequest();
    xhr.open("POST", `http://${domain}:8000/api/submitAnswer`, true);
    xhr.send(`{"question":"${question}", "answer":"${a}", "sessionID":"${value}"}`);

    canAnswer=false;
}

function get_question()
{
    if(ans!=0)
    {
        document.getElementById(ans).style.cssText = `
                border-color: black;
                border-width: 5px;
            `
        s=false;
    }
    else
    {
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

async function reset()
{
    if (ws.readyState !== WebSocket.CLOSED) {
        xhr = new XMLHttpRequest();
        const value = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];
        xhr.open("POST", `http://${domain}:8000/api/disconnect`, true);
        xhr.send(`{"sessionID":"${value}"}`);
        ws.close();
    }

    await sleep(500);
    window.location.reload();
}

window.addEventListener('beforeunload', async (event)=>{
    if (ws.readyState !== WebSocket.CLOSED) {
        xhr = new XMLHttpRequest();
        const value = ('; '+document.cookie).split(`; sessionID=`).pop().split(';')[0];
        xhr.open("POST", `http://${domain}:8000/api/disconnect`, true);
        xhr.send(`{"sessionID":"${value}"}`);
        ws.close();
        await sleep(500);
        return 'Disconnecting';
    }
})
