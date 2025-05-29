// Polling-based Whiteboard client
const ROOM_ID = "<ROOM_ID>"; // replace after gen_config
const API = "http://localhost:8000";

const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
let drawing = false;

canvas.addEventListener('mousedown', () => drawing = true);
canvas.addEventListener('mouseup', () => { drawing = false; ctx.beginPath(); });
canvas.addEventListener('mousemove', e => {
  if(!drawing) return;
  const rect = canvas.getBoundingClientRect();
  const cmd = { x: e.clientX - rect.left, y: e.clientY - rect.top, type: "line" };
  sendCommand(cmd);
  draw(cmd);
});

document.getElementById('refresh').onclick = poll;

function draw(cmd){
  ctx.lineTo(cmd.x, cmd.y);
  ctx.stroke();
}

async function sendCommand(cmd){
  await fetch(`${API}/draw/${ROOM_ID}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd)
  });
}

async function poll(){
  const res = await fetch(`${API}/draw/${ROOM_ID}`);
  const cmds = await res.json();
  ctx.clearRect(0,0,canvas.width,canvas.height);
  cmds.forEach(draw);
}

// initial data
poll();
