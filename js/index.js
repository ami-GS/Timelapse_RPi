/**
 * Created by daiki on 2014/05/09.
 */
var canvas1 = document.getElementById("canvas1");
var context1 = canvas1.getContext("2d");
var canvas2 = document.getElementById("canvas2");
var context2 = canvas2.getContext("2d");
var duration = document.getElementById("duration");
var count;
var img = new Image();
var STATE = "";
var ws = new WebSocket("ws://localhost:8080/camera");
ws.binaryType = 'blob';

window.onload = function(){
    setInfo();
};

ws.onopen = function(){
    console.log("connection was established");
};

img.onload = function(){
    context2.drawImage(img,0,0);
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
            setInfo()
        }
        else if(evt.data == "finish"){
            //make synchronize with server
        }
    }
};

window.onbeforeunload = function(){
    ws.close(1000); //Is this needed??
    clearInterval(timer);
};

function drawRec(){
    context1.lineWidth = 20;
    context1.strokeStyle = "rgb(255,0,0)";
    context1.strokeRect(0, 0, canvas1.width, canvas1.height);
    context1.fillStyle = "black";
    context1.font = "5px 'Arial'";
    context1.textAlign = "start";
    context1.textBaseline = "top";
    context1.fillText("REC", 20, 0, 200);
}

function removeRec(){context1.clearRect(0,0,canvas1.width, canvas1.height);}

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
    STATE = "";
    removeRec();
    duration.innerHTML = "Finish recording";
    clearInterval(timer);
    document.getElementById("download").disabled = false;
}


function setInfo(){
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