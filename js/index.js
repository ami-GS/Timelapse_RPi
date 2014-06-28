/**
 * Created by daiki on 2014/05/09.
 */
var canvas1 = document.getElementById("canvas1");
var context1 = canvas1.getContext("2d");
var canvas2 = document.getElementById("canvas2");
var context2 = canvas2.getContext("2d");
var duration = document.getElementById("duration");
var count;
var effectType = {"USB":['normal', 'edge', 'motion', 'gray'],
                  "RPi":['none', 'sketch', 'posterise', 'gpen', 'colorbalance', 'film',
                      'pastel', 'emboss', 'denoise', 'negative', 'hatch', 'colorswap',
                      'colorpoint', 'saturation', 'blur', 'posterise',
                      'watercolor', 'cartoon', 'solarize', 'oilpaint']};
var img = new Image();
var STATE = "";
var ws = new WebSocket("ws://localhost:8080/camera");
ws.binaryType = 'blob';


window.onload = function(){
    context1.fillStyle = "blue";
    context1.font = "bold 20px Arial";
    context1.textAlign = "center";
    context1.textBaseline = "middle";
    context1.fillText("No connection", canvas1.width/2, canvas1.height/2);
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
            cntEnd();
        }
		else if(evt.data.indexOf("camType" != -1)){
            showEffectButton(effectType[evt.data.slice(-3)]); //extract 'USB' or 'RPi'
		}
        //else if(evt.data.indexOf("effect") != -1){
        //    setClicked();//TODO initial setting of clicked button
        //}
    }
};

function showEffectButton(camTypes){
    var elm;
    var lab;
    var parent = document.getElementById("radioSet");
    for(i = 0; i < camTypes.length; i++){
        elm = document.createElement("input");
        lab = document.createElement("label");
        elm.type = "radio";
        elm.id = "radio".concat(i.toString());
        elm.name = "mode";
        elm.value = camTypes[i];
        elm.onclick = function(){chmd(this.value);};
        lab.htmlFor = elm.id;
        lab.appendChild(document.createTextNode(camTypes[i]));
        parent.appendChild(elm);
        parent.appendChild(lab);
    }
}

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
    ws.send('["start"]');
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

var isMouseDown = false;
document.onmousedown = function() { isMouseDown = true };
document.onmouseup   = function() { isMouseDown = false };
function chParam(slider){
    if (isMouseDown){
        ws.send('[\"'+slider.id + '\", \"' + slider.value + '\"]');
        var s = document.getElementById("param"+slider.id[slider.id.length-1]);
        s.innerHTML = slider.value;
    }
}

function chmd(radio){
    ws.send('[\"'+radio+'\"]');
}
