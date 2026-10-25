const $ = s => document.querySelector(s);
const form = $('#analyzer-form'), input = $('#message'), button = $('#analyze-btn'), result = $('#result'), errorBox = $('#error');
const label = button.querySelector('span');
input.addEventListener('input', () => { $('#char-count').textContent = input.value.length.toLocaleString('en-IN') + ' / 10,000'; });

fetch('/api/health').then(r => r.json()).then(h => {
  const m = $('#mode');
  m.textContent = h.ml_available ? 'Check mode: rules + ML prototype (chhote dataset par train hua).' : 'Check mode: rule-based screening.';
  m.hidden = false;
}).catch(() => {});

form.addEventListener('submit', async e => {
  e.preventDefault();
  result.hidden = errorBox.hidden = true;
  button.disabled = true; label.textContent = 'Jaanch rahe hain…';
  try {
    const res = await fetch('/api/analyze-message', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: input.value }) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Jaanch nahi ho saki. Dobara koshish karein.');
    show(data);
    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    errorBox.textContent = err.message || 'Server se sampark nahi ho saka. Page refresh karke dobara koshish karein.';
    errorBox.hidden = false;
  } finally { button.disabled = false; label.textContent = 'Check message'; }
});

function el(tag, cls, text) { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }

function show(d) {
  const lvl = d.risk_assessment === 'High' ? 'high' : d.risk_assessment === 'No obvious indicators' ? 'low' : 'medium';
  $('#risk-title').textContent = { high: 'Kai warning signs mile', medium: 'Kuch warning signs mile', low: 'Koi obvious sign nahi mila' }[lvl];
  const b = $('#risk-badge'); b.textContent = { high: 'Zyada savdhaani', medium: 'Savdhaan rahein', low: 'Kam signal' }[lvl]; b.className = 'badge ' + lvl;
  $('#meter').className = 'meter ' + lvl;
  $('#explanation').textContent = d.explanation;
  const box = $('#indicators'); box.replaceChildren();
  (d.indicators || []).forEach(i => { const a = el('article'); a.append(el('strong', '', i.signal), el('p', '', i.reason)); box.append(a); });
  if (!(d.indicators || []).length) box.append(el('p', 'none ind-none', 'Configured warning phrases nahi mile. Iska matlab message safe hai, ye confirm nahi hota.'));
  const ul = $('#actions'); ul.replaceChildren();
  (d.recommended_actions || []).forEach(t => ul.append(el('li', '', t)));
  $('#limitations').textContent = d.limitations || '';
  result.hidden = false;
}
