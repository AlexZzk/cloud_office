const sceneEl = document.getElementById('scene');
const jsonEl = document.getElementById('json');

const positions = {
  'node-zone-work': { x: 20, y: 20 },
  'node-zone-meet': { x: 220, y: 20 },
  'node-seat-a1': { x: 40, y: 120 },
  'node-seat-a2': { x: 140, y: 120 },
};

function addNode(text, cls, x, y) {
  const div = document.createElement('div');
  div.className = `node ${cls}`;
  div.style.left = `${x}px`;
  div.style.top = `${y}px`;
  div.textContent = text;
  sceneEl.appendChild(div);
}

async function render() {
  const res = await fetch('/api/scene/gathered');
  const data = await res.json();
  jsonEl.textContent = JSON.stringify(data, null, 2);
  sceneEl.innerHTML = '';

  data.nodes.forEach((node) => {
    const pos = positions[node.scene_node] || { x: 10, y: 10 };
    const cls = node.node_type === 'ZONE' ? 'zone' : 'seat';
    addNode(`${node.node_type}: ${node.business_id}`, cls, pos.x, pos.y);
  });

  data.participants.forEach((p, index) => {
    addNode(`👤 ${p.subject_id}`, 'participant', 40 + index * 120, 230);
  });
}

render().catch((err) => {
  jsonEl.textContent = `load failed: ${err.message}`;
});
