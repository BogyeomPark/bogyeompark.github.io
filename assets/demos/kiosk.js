/* Virtual kiosk demo.
 *
 * Reproduces the six-step ordering task from the JMIR validation study and
 * measures three of its four VR-derived biomarkers: time to completion, number
 * of errors, and hand movement speed — here the pointer stands in for the hand
 * controller. The fourth, scanpath length, needs an eye tracker and is not
 * reproduced; saying so is part of the demo.
 *
 * The result then feeds the narrative-AI study: the same numbers are written up
 * twice, once looking back and once looking forward, and the visitor picks the
 * one that moves them. Both reports are computed from what they actually did,
 * so nothing about the reader is invented.
 *
 * Everything stays in the browser. No data is sent anywhere.
 */
(() => {
  const TASK = ['Shrimp Burger', 'Cheese Sticks', 'Coca-Cola'];

  const STEPS = [
    {
      id: 'place', prompt: 'Where will you eat?', layout: 'kiosk-wide',
      items: [{ name: 'Eat in' }, { name: 'Take out' }], target: null,
    },
    {
      id: 'burger', prompt: 'Choose a burger.',
      items: [
        { name: 'Bulgogi Burger', price: '3,200' },
        { name: 'Cheese Burger', price: '3,800' },
        { name: 'Chicken Burger', price: '4,300' },
        { name: 'Shrimp Burger', price: '5,200' },
        { name: 'Double Beef Burger', price: '5,900' },
        { name: 'Egg Burger', price: '3,500' },
      ],
      target: 'Shrimp Burger',
    },
    {
      id: 'side', prompt: 'Choose a side.',
      items: [
        { name: 'String Cheese', price: '+1,200' },
        { name: 'Cheese Sticks', price: '+500' },
        { name: 'Hash Brown', price: '+1,200' },
        { name: 'Apple Pie', price: '+1,300' },
      ],
      target: 'Cheese Sticks',
    },
    {
      id: 'drink', prompt: 'Choose a drink.',
      items: [
        { name: 'Cider', price: '+500' },
        { name: 'Vanilla Shake', price: '+1,200' },
        { name: 'Coca-Cola', price: '+500' },
        { name: 'Milk', price: '+1,200' },
      ],
      target: 'Coca-Cola',
    },
    { id: 'confirm', prompt: 'Check your order.', kind: 'confirm' },
    {
      id: 'payment', prompt: 'Choose a payment method.', layout: 'kiosk-wide',
      items: [{ name: 'Card' }, { name: 'Mobile voucher' }], target: null,
    },
  ];

  const el = (sel, root = document) => root.querySelector(sel);
  const stage = el('#kiosk-stage');
  const result = el('#kiosk-result');
  const taskLine = el('#kiosk-task-line');
  if (!stage) return;

  const state = {
    step: -1, started: 0, errors: 0, distance: 0, points: [],
    last: null, order: {}, code: '',
  };

  /* --- speech ---------------------------------------------------------- */
  let voice = null;
  const pickVoice = () => {
    const voices = window.speechSynthesis ? speechSynthesis.getVoices() : [];
    voice = voices.find(v => /^en(-|_)?/i.test(v.lang)) || voices[0] || null;
  };
  if (window.speechSynthesis) {
    pickVoice();
    speechSynthesis.addEventListener('voiceschanged', pickVoice);
  }
  const say = (text) => {
    if (!window.speechSynthesis || el('#kiosk-mute').checked) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    if (voice) u.voice = voice;
    u.rate = 0.95;
    speechSynthesis.speak(u);
  };

  /* --- pointer path ----------------------------------------------------- */
  const track = (event) => {
    if (state.step < 0) return;
    const rect = stage.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    if (state.last) {
      state.distance += Math.hypot(x - state.last.x, y - state.last.y);
    }
    state.last = { x, y };
    if (state.points.length < 4000) state.points.push([Math.round(x), Math.round(y)]);
  };
  stage.addEventListener('pointermove', track);

  /* --- rendering -------------------------------------------------------- */
  const money = (n) => n.toLocaleString('en-US');

  function screen(inner, stepLabel) {
    stage.innerHTML =
      '<div class="kiosk-screen">' +
        '<div class="kiosk-head"><span>SeoulTech Kiosk</span><span>' + stepLabel + '</span></div>' +
        '<div class="kiosk-body">' + inner + '</div>' +
      '</div>';
  }

  function renderStart() {
    screen(
      '<p class="kiosk-prompt">Touch Start to begin your order.</p>' +
      '<div class="kiosk-start"><button type="button" id="kiosk-go">Start</button></div>',
      'Start');
    el('#kiosk-go').addEventListener('click', begin);
  }

  function renderStep() {
    const step = STEPS[state.step];
    const label = 'Step ' + (state.step + 1) + ' of ' + STEPS.length;

    if (step.kind === 'confirm') {
      const rows = ['burger', 'side', 'drink']
        .map(k => '<li><b>' + state.order[k] + '</b><span>' + (k === 'burger' ? '5,200' : '+500') + '</span></li>')
        .join('');
      screen(
        '<p class="kiosk-prompt">' + step.prompt + '</p>' +
        '<ul class="kiosk-summary">' + rows + '</ul>' +
        '<div class="kiosk-grid kiosk-wide">' +
          '<button class="kiosk-item" type="button" data-confirm="1"><b>Confirm</b></button>' +
        '</div>',
        label);
      el('[data-confirm]').addEventListener('click', () => advance());
      say(step.prompt);
      return;
    }

    const items = step.items.map((item, i) =>
      '<button class="kiosk-item" type="button" data-i="' + i + '">' +
        '<b>' + item.name + '</b>' + (item.price ? '<span>' + item.price + '</span>' : '') +
      '</button>').join('');
    screen(
      '<p class="kiosk-prompt">' + step.prompt + '</p>' +
      '<div class="kiosk-grid ' + (step.layout || '') + '">' + items + '</div>',
      label);

    stage.querySelectorAll('[data-i]').forEach(button => {
      button.addEventListener('click', () => {
        const item = step.items[Number(button.dataset.i)];
        if (step.target && item.name !== step.target) {
          state.errors += 1;
          button.classList.remove('wrong');
          void button.offsetWidth;
          button.classList.add('wrong');
          return;
        }
        if (step.target) state.order[step.id] = item.name;
        if (step.id === 'payment' && item.name === 'Mobile voucher') return renderKeypad();
        advance();
      });
    });
    say(step.prompt);
  }

  function renderKeypad() {
    const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Clear', '0', 'OK'];
    const draw = () =>
      screen(
        '<p class="kiosk-prompt">Enter your voucher number.</p>' +
        '<p class="kiosk-code">' + (state.code || ' ') + '</p>' +
        '<div class="kiosk-pad">' + keys.map(k => '<button type="button" data-k="' + k + '">' + k + '</button>').join('') + '</div>',
        'Step ' + STEPS.length + ' of ' + STEPS.length);

    const wire = () => stage.querySelectorAll('[data-k]').forEach(b => b.addEventListener('click', () => {
      const k = b.dataset.k;
      if (k === 'Clear') state.code = state.code.slice(0, -1);
      else if (k === 'OK') { if (state.code.length >= 4) return advance(); }
      else if (state.code.length < 6) state.code += k;
      draw(); wire();
    }));
    draw(); wire();
    say('Enter your voucher number.');
  }

  /* --- flow ------------------------------------------------------------- */
  function begin() {
    Object.assign(state, { step: 0, started: performance.now(), errors: 0, distance: 0, points: [], last: null, order: {}, code: '' });
    result.hidden = true;
    renderStep();
  }

  function advance() {
    state.step += 1;
    if (state.step >= STEPS.length) return finish();
    renderStep();
  }

  function finish() {
    const seconds = (performance.now() - state.started) / 1000;
    const speed = state.distance / seconds;
    state.step = -1;
    screen('<p class="kiosk-prompt">Thank you.</p>' +
           '<div class="kiosk-start"><button type="button" id="kiosk-again">Try again</button></div>', 'Done');
    el('#kiosk-again').addEventListener('click', begin);
    say('Thank you.');
    report(seconds, speed);
  }

  /* --- results and the two reports -------------------------------------- */
  const KEY = 'kiosk-best-seconds';

  function pathSvg() {
    if (state.points.length < 2) return '';
    const rect = stage.getBoundingClientRect();
    const w = Math.max(rect.width, 1), h = Math.max(rect.height, 1);
    const d = state.points.map((p, i) => (i ? 'L' : 'M') + p[0] + ' ' + p[1]).join(' ');
    const last = state.points[state.points.length - 1];
    return '<svg class="kiosk-path" viewBox="0 0 ' + Math.round(w) + ' ' + Math.round(h) + '" role="img" ' +
           'aria-label="Path your pointer travelled during the task">' +
           '<path d="' + d + '"></path><circle cx="' + last[0] + '" cy="' + last[1] + '" r="4"></circle></svg>';
  }

  function report(seconds, speed) {
    const errors = state.errors;
    // Both narratives are arithmetic on what just happened: a wrong selection
    // costs roughly one step's worth of time, so the counterfactual saving and
    // the prefactual target come from the same measured pace.
    const perStep = seconds / STEPS.length;
    const taken = Math.max(1, Math.round(seconds));
    // Only claim a saving when it rounds to at least a second, so an
    // impossibly fast run cannot produce "0 seconds instead of 0".
    const saved = Math.round(errors * perStep);
    const target = Math.max(1, taken - saved);

    const counterfactual = errors && saved >= 1
      ? 'You made ' + errors + ' wrong ' + (errors === 1 ? 'selection' : 'selections') +
        '. Had you selected correctly each time, this order would have taken about ' +
        target + ' seconds instead of ' + taken + '.'
      : 'You made no wrong selections. Had you hesitated at even one step, this order would have taken noticeably longer than the ' +
        taken + ' seconds it did.';

    const prefactual = errors && saved >= 1
      ? 'If you keep this pace and avoid those ' + errors + ' wrong ' + (errors === 1 ? 'selection' : 'selections') +
        ', your next order will take about ' + target + ' seconds.'
      : 'If you keep this pace, your next order will stay near ' + taken +
        ' seconds even as the menu becomes less familiar.';

    const best = Number(localStorage.getItem(KEY) || 0);
    const isBest = !best || seconds < best;
    if (isBest) localStorage.setItem(KEY, String(Math.round(seconds * 10) / 10));

    result.innerHTML =
      '<h3>Your measurements</h3>' +
      '<div class="metric-grid">' +
        '<div class="metric"><strong>' + seconds.toFixed(1) + 's</strong><span>Time to completion, across all six steps.</span></div>' +
        '<div class="metric"><strong>' + errors + '</strong><span>Number of errors &mdash; selections that were not the item asked for.</span></div>' +
        '<div class="metric"><strong>' + Math.round(speed) + '</strong><span>Hand movement speed in pixels per second: pointer distance divided by time.</span></div>' +
      '</div>' +
      '<p class="kiosk-best">' + (isBest ? 'That is your fastest run on this browser.'
        : 'Your fastest run on this browser is ' + best + 's.') + '</p>' +
      '<figure class="paper-figure">' + pathSvg() +
        '<figcaption class="kiosk-figcaption">The path your pointer travelled. In the study this was the hand controller, ' +
        'tracked by base stations; its total length divided by time is one of the four biomarkers.</figcaption>' +
      '</figure>' +

      '<h3 id="kiosk-report">The same result, written two ways</h3>' +
      '<p>Our other study asked which kind of explanation moves someone to act. Both reports below describe ' +
      'the run you just finished; only the direction of the sentence changes.</p>' +
      '<div class="card-grid" id="kiosk-choice">' +
        '<article class="card"><span class="card-index">COUNTERFACTUAL</span><h3>Looking back</h3><p>' +
          counterfactual + '</p><button class="button secondary" type="button" data-pick="counterfactual">This one moves me</button></article>' +
        '<article class="card"><span class="card-index">PREFACTUAL</span><h3>Looking forward</h3><p>' +
          prefactual + '</p><button class="button secondary" type="button" data-pick="prefactual">This one moves me</button></article>' +
      '</div>' +
      '<div id="kiosk-reveal"></div>' +
      '<p class="kiosk-note"><strong>This is a demonstration, not a screening test.</strong> It reproduces the task and three of ' +
      'its measures in a browser; a diagnosis in the study rested on a clinical assessment, an MRI scan, and an eye-tracking ' +
      'headset. Nothing you do here is sent anywhere &mdash; the measurements stay in this browser.</p>' +
      '<div class="kiosk-actions"><a class="button" href="/publications/multimodal-biomarkers-jmir/">Read the study &rarr;</a>' +
      '<a class="button secondary" href="/publications/counterfactual-prefactual-hci2023/">The narrative study &rarr;</a></div>';

    result.hidden = false;
    result.querySelectorAll('[data-pick]').forEach(b => b.addEventListener('click', () => reveal(b.dataset.pick)));
    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function reveal(pick) {
    localStorage.setItem('kiosk-narrative-pick', pick);
    const mechanism = pick === 'counterfactual'
      ? 'Participants who read the counterfactual report looked back: they revisited what they had done and asked how the analysis worked. The mechanism was <b>self-reflection</b>.'
      : 'Participants who read the prefactual report looked ahead: they planned what to change next. The mechanism was <b>self-improvement</b>.';
    el('#kiosk-reveal').innerHTML =
      '<div class="research-note"><p>Twenty participants rated both kinds of report on the System Causability Scale, and the ' +
      'scores came out <b>the same</b> &mdash; neither explained better than the other. The interviews were where they parted.</p>' +
      '<p>' + mechanism + '</p></div>';
    el('#kiosk-choice').querySelectorAll('button').forEach(b => { b.disabled = true; });
  }

  /* --- start ------------------------------------------------------------ */
  taskLine.innerHTML = 'Use the kiosk to order a <strong>' + TASK[0] + '</strong>, <strong>' + TASK[1] +
    '</strong>, and a <strong>' + TASK[2] + '</strong>.';
  el('#kiosk-say').addEventListener('click', () => say(taskLine.textContent));
  renderStart();
})();
