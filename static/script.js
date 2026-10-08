let siriWave;
let listening=false;

window.onload=function(){

siriWave=new SiriWave({
container:document.getElementById('siri-container'),
width:640,
height:200,
style:'ios9',
speed:0.2,
amplitude:0
});

siriWave.start();

document.getElementById("micBtn").addEventListener("click",toggleMic);

updateUI();
}

function toggleMic(){

listening=!listening;

let btn=document.getElementById("micBtn");

if(listening){

btn.classList.add("listening");

siriWave.setAmplitude(1);

fetch("/start_listening");

}
else{

btn.classList.remove("listening");

siriWave.setAmplitude(0);

fetch("/stop_listening");

}
}

async function updateUI(){

const res=await fetch("/status");
const data=await res.json();

document.getElementById("recognized").innerText="You: "+(data.recognized||"");

document.getElementById("reply").innerText="Keero: "+(data.reply||"");

if(data.state==="thinking"){
document.getElementById("thinking").innerText="Keero is thinking...";
siriWave.setAmplitude(0.3);
}
else{
document.getElementById("thinking").innerText="";
}

setTimeout(updateUI,500);

}