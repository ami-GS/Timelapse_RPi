/**
 * Created by daiki on 2014/05/09.
 */
var img = document.getElementById("liveImg");
var duration = document.getElementById("duration");
var count;
var ws = new WebSocket("ws://localhost:8080/camera");
ws.binaryType = 'blob';

window.onload = function(){
        setInfo();
};

ws.onopen = function(){
	console.log("connection was established");
};

ws.onmessage = function(evt){
    if(evt.data.size > 100){
        img.src = URL.createObjectURL(evt.data);
    }
    else{
        if(evt.data == "recording"){
            console.log("now recording");
            STATE = "recording";
            drawRec();
        }
        else if(evt.data.indexOf("remaining") != -1){
            count = Number(evt.data.slice(10,evt.data.indexOf(".")+1)); //TODO receive remaining time
            setInfo(STATE)
        }
    }
};

window.onbeforeunload = function(){
    ws.close(1000); //Is this needed??
    clearInterval(timer);
};

function drawRec(){
    var canvas = document.getElementById("canvas");
    var context = canvas.getContext("2d");
    context.fillStyle = "red";
    context.font = "30px 'Arial'";
    context.textAlign = "start";
    context.textBaseline = "top";
    context.fillText("REC", 0, 0, 200);
}

function startTimeLapse() {
    cntStart();
    drawRec();
    document.getElementById("start").disabled = true;
    var fps = document.getElementById("fps").value;
    var length = document.getElementById("len").value;
    ws.send('["fps", %s]'.replace("%s", fps));
    ws.send('["length", %s]'.replace("%s", length));
}

var timer;
function cntStart(){
    timer = setInterval("cntDown()",1000);
}

function cntDown(){
    count -= 1;
    if(count <= 0){
        cntEnd();
    }
    else{
        updateInfo(count);
    }
}

function cntEnd(){
    duration.innerHTML = "Finish recording";
    clearInterval(timer);
}


function setInfo(STATE){
    if(STATE == "recording"){
        document.getElementById("start").disabled = true;
        cntStart()
    }
    else{
        var fps = parseFloat(document.getElementById("fps").value);
        var length = parseFloat(document.getElementById("len").value);
        count = (length*25)/fps;
        updateInfo(count);
    }
}

function updateInfo(time){
    time = time*10;
    tmp = "Recording lasts " + String(Math.round(time)/10)+" seconds.";
    duration.innerHTML = tmp;
}

function chParam1(value){
    ws.send('["param1", %s]'.replace("%s", value));
    var param1 = document.getElementById("param1");
    param1.innerHTML = value;
}
function chParam2(value){
    ws.send('["param2", %s]'.replace("%s", value));
    var param2 = document.getElementById("param2");
    param2.innerHTML = value;
}

function disable(button){
    document.getElementById("motion").disabled = false;
    document.getElementById("gray").disabled = false;
    document.getElementById("normal").disabled = false;
    document.getElementById("edge").disabled = false;
    button.disabled = true;
}

function motionMode(){ws.send('["motion"]');}
function grayMode(){ws.send('["gray"]');}
function normalMode(){ws.send('["normal"]');}
function edgeMode(){ws.send('["edge"]');}