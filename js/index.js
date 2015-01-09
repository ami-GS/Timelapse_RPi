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
var frameColor = "white";


window.onload = function(){
	wsConnect();
	reconnect();
    context1.fillStyle = "blue";
    context1.font = "bold 20px Arial";
    context1.textAlign = "center";
    context1.textBaseline = "middle";
    context1.fillText("No connection", canvas1.width/2, canvas1.height/2);
    setInfo();
    document.getElementById("range1").value = 0;
    document.getElementById("range2").value = 50;
};

function wsSetting() {
ws.binaryType = 'blob';

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
			frameColor = "rgb(255,0,0)";
            drawFrame();
        }
        else if(evt.data.indexOf("remaining") != -1){
            count = Number(evt.data.slice(10,evt.data.indexOf(".")+1)); //TODO receive remaining time
            setInfo()
        }
        else if(evt.data == "finish"){
            //make synchronize with server
            cntEnd();
        }
        else if(evt.data.indexOf("param") != -1){
            var ran = evt.data.slice(6);
            for(var i = 1; i < 3; i++){
                document.getElementById("param"+i).innerHTML = ran.slice(0,ran.indexOf(":"));
                document.getElementById("range"+i).value = parseInt(ran.slice(0,ran.indexOf(":")));
                ran = ran.slice(ran.indexOf(":")+1);
            }
        } else if(evt.data.indexOf("temperature") != -1) {
			drawTemp(evt.data.slice(12));
		}
        //else if(evt.data.indexOf("effect") != -1){
        //    setClicked();//TODO initial setting of clicked button
        //}
    }
};

ws.onerror = function(evt){
	wsConnect();
};

}

function reconnect() {
	if (ws.readyState >= 2) {
		wsConnect();
	}
	window.setTimeout("reconnect()", 1000);
}


img.onload = function(){
    context2.drawImage(img,0,0);
};


window.onbeforeunload = function(){
    ws.close(1000); //Is this needed??
    clearInterval(timer);
};

function drawFrame(){
    context1.lineWidth = 20;
	context1.strokeStyle = frameColor;
    context1.strokeRect(0, 0, canvas1.width, canvas1.height);
	if (STATE == "recording") {
		drawRec();
	}
}

function drawRec(){
    context1.fillStyle = "black";
    context1.font = "5px 'Arial'";
    context1.textAlign = "start";
    context1.textBaseline = "top";
    context1.fillText("REC", 20, 0, 200);
}

function drawTemp(data){
	drawFrame();
    context1.fillStyle = "black";
    context1.font = "5px Arial";
    context1.textAlign = "start";
    context1.textBaseline = "top";
    context1.fillText(data, canvas1.width-40, 0);
}

function removeRec(){context1.clearRect(0,0,canvas1.width, canvas1.height);}

function startTimeLapse() {
	STATE = "recording";
	frameColor = "rgb(255,0,0)";
    cntStart();
    drawFrame();
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
	frameColor = "white";
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

function toggleLED(btn) {
	if (btn.value == "light ON") {
		btn.value = "light OFF";
	} else {
		btn.value = "light ON";
	}
	ws.send('[\"LED\"]');
}