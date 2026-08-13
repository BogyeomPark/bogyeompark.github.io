/* Virtual kiosk demo — the study's own screens.
 *
 * panel01–08 are the interface from the JMIR validation study, with click
 * targets laid over them in percentage coordinates so they scale. The flow is
 * the original one: start, where to eat, then burger / side / drink as an
 * accordion, then the order with its payment choice, then the keypad.
 *
 * Measures three of the study's four VR-derived biomarkers — time to
 * completion, number of errors, hand movement speed (pointer standing in for
 * the controller). Scanpath length needs an eye tracker and is not reproduced.
 *
 * Prompts are spoken in Korean because the screens are Korean; an English
 * translation sits under the screen. If no Korean voice is installed the demo
 * stays silent rather than letting another language mangle it.
 *
 * Everything stays in the browser.
 */
(() => {
  const COL = [[4, 25], [27, 48], [51, 72], [74, 96]];   // menu grid columns, %
  const box = (col, top, bottom) => ({ x: COL[col][0], w: COL[col][1] - COL[col][0], y: top, h: bottom - top });

  const STEPS = [
    {
      panel: 'panel01', ko: '주문을 시작하려면 시작버튼을 눌러주세요.',
      en: 'Touch the Start button to begin your order.',
      hits: [{ label: 'Start', area: { x: 19, y: 45, w: 62, h: 33 }, round: true }],
    },
    {
      panel: 'panel02', ko: '식사하실 장소를 선택해 주세요.',
      en: 'Where will you eat?',
      hits: [
        { label: 'Eat in', area: { x: 5, y: 47, w: 43, h: 31 } },
        { label: 'Take out', area: { x: 52, y: 47, w: 43, h: 31 } },
      ],
    },
    {
      panel: 'panel03', ko: '햄버거 메뉴를 선택해 주세요.',
      en: 'Choose a burger.', target: '새우버거',
      hits: [
        { label: '소고기버거', area: box(0, 30.5, 43.5) }, { label: '치즈버거', area: box(1, 30.5, 43.5) },
        { label: '치킨버거', area: box(2, 30.5, 43.5) }, { label: '마늘버거', area: box(3, 30.5, 43.5) },
        { label: '불고기버거', area: box(0, 45, 58) }, { label: '양파버거', area: box(1, 45, 58) },
        { label: '새우버거', area: box(2, 45, 58) }, { label: '토마토버거', area: box(3, 45, 58) },
      ],
    },
    {
      panel: 'panel04', ko: '사이드 메뉴를 선택해 주세요.',
      en: 'Choose a side.', target: '치즈스틱',
      hits: [
        { label: '감자튀김', area: box(0, 45, 58) }, { label: '치즈스틱', area: box(1, 45, 58) },
        { label: '스트링 치즈', area: box(2, 45, 58) }, { label: '해시브라운', area: box(3, 45, 58) },
        { label: '치킨 랩', area: box(0, 60, 73) }, { label: '사과 파이', area: box(1, 60, 73) },
        { label: '핫케이크', area: box(2, 60, 73) }, { label: '치킨 너겟', area: box(3, 60, 73) },
      ],
    },
    {
      panel: 'panel05', ko: '음료 메뉴를 선택해 주세요.',
      en: 'Choose a drink.', target: '코카콜라',
      hits: [
        { label: '코카콜라', area: box(0, 60, 73) }, { label: '사이다', area: box(1, 60, 73) },
        { label: '환타 오렌지', area: box(2, 60, 73) }, { label: '생수', area: box(3, 60, 73) },
        { label: '바닐라 쉐이크', area: box(0, 75, 88) }, { label: '초코 쉐이크', area: box(1, 75, 88) },
        { label: '딸기 쉐이크', area: box(2, 75, 88) }, { label: '우유', area: box(3, 75, 88) },
      ],
    },
    {
      panel: 'panel06', ko: '주문을 확인하시고 결제 방법을 선택해 주세요.',
      en: 'Check your order, then choose a payment method.',
      hits: [
        { label: '카드 결제', area: { x: 3, y: 56, w: 44, h: 30 } },
        { label: '모바일 상품권', area: { x: 51, y: 56, w: 44, h: 30 } },
      ],
    },
    { panel: 'panel07', ko: '비밀번호를 입력해 주세요.', en: 'Enter your four-digit number.', keypad: true },
  ];

  const KEYS = [
    ['1', 6, 21.5], ['2', 38, 21.5], ['3', 69, 21.5],
    ['4', 6, 35], ['5', 38, 35], ['6', 69, 35],
    ['7', 6, 49], ['8', 38, 49], ['9', 69, 49],
    ['clear', 6, 63], ['0', 38, 63], ['ok', 69, 63],
  ];

  const el = (s, r = document) => r.querySelector(s);
  const stage = el('#kiosk-stage');
  const result = el('#kiosk-result');
  const caption = el('#kiosk-caption');
  if (!stage) return;

  const state = { step: -1, started: 0, errors: 0, distance: 0, points: [], last: null, code: '' };

  /* --- speech: Korean screens, Korean voice, or silence ------------------ */
  let koVoice = null;
  const findVoice = () => {
    const voices = window.speechSynthesis ? speechSynthesis.getVoices() : [];
    koVoice = voices.find(v => /^ko/i.test(v.lang)) || null;
    const btn = el('#kiosk-say');
    if (btn) {
      btn.disabled = !koVoice;
      btn.textContent = koVoice ? '🔊 다시 듣기' : 'No Korean voice installed';
    }
  };
  if (window.speechSynthesis) {
    findVoice();
    speechSynthesis.addEventListener('voiceschanged', findVoice);
  }
  const say = (text) => {
    if (!koVoice || el('#kiosk-mute').checked) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = koVoice; u.lang = koVoice.lang; u.rate = 0.95;
    speechSynthesis.speak(u);
  };

  /* --- pointer path ------------------------------------------------------ */
  stage.addEventListener('pointermove', (e) => {
    if (state.step < 0) return;
    const r = stage.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    if (state.last) state.distance += Math.hypot(x - state.last.x, y - state.last.y);
    state.last = { x, y };
    if (state.points.length < 4000) state.points.push([Math.round(x), Math.round(y)]);
  });

  /* --- rendering --------------------------------------------------------- */
  function paint(step, extra = '') {
    const hits = (step.hits || []).map((h, i) =>
      '<button class="kiosk-hit' + (h.round ? ' round' : '') + '" type="button" data-i="' + i + '"' +
      ' aria-label="' + h.label + '" style="left:' + h.area.x + '%;top:' + h.area.y + '%;' +
      'width:' + h.area.w + '%;height:' + h.area.h + '%"></button>').join('');
    stage.innerHTML =
      '<div class="kiosk-panel">' +
        '<img src="/assets/demos/kiosk/' + step.panel + '.webp" alt="Kiosk screen: ' + step.en + '">' +
        hits + extra +
      '</div>';
    caption.textContent = step.en;
    say(step.ko);
  }

  function renderStep() {
    const step = STEPS[state.step];
    if (step.keypad) return renderKeypad();
    paint(step);
    stage.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => {
      const hit = step.hits[Number(b.dataset.i)];
      if (step.target && hit.label !== step.target) {
        state.errors += 1;
        b.classList.remove('miss'); void b.offsetWidth; b.classList.add('miss');
        return;
      }
      advance();
    }));
  }

  function renderKeypad() {
    const step = STEPS[state.step];
    const keys = KEYS.map(([k, x, y]) =>
      '<button class="kiosk-hit" type="button" data-k="' + k + '" aria-label="' + k + '"' +
      ' style="left:' + x + '%;top:' + y + '%;width:25%;height:12%"></button>').join('');
    const dots = '<div class="kiosk-dots" aria-live="polite">' +
      [0, 1, 2, 3].map(i => '<span' + (state.code.length > i ? ' class="on"' : '') + '></span>').join('') + '</div>';
    paint(step, keys + dots);
    stage.querySelectorAll('[data-k]').forEach(b => b.addEventListener('click', () => {
      const k = b.dataset.k;
      if (k === 'clear') state.code = state.code.slice(0, -1);
      else if (k === 'ok') { if (state.code.length === 4) return finish(); }
      else if (state.code.length < 4) state.code += k;
      renderKeypad();
    }));
  }

  function begin() {
    Object.assign(state, { step: 1, started: performance.now(), errors: 0, distance: 0, points: [], last: null, code: '' });
    result.hidden = true;
    renderStep();
  }

  function advance() {
    if (state.step === 0) return begin();
    state.step += 1;
    renderStep();
  }

  function renderStart() {
    state.step = 0;
    paint(STEPS[0]);
    el('[data-i]').addEventListener('click', begin);
  }

  /* --- results ----------------------------------------------------------- */
  const KEY = 'kiosk-best-seconds';

  function finish() {
    const seconds = (performance.now() - state.started) / 1000;
    const speed = state.distance / seconds;
    state.step = -1;
    caption.textContent = 'Thank you.';
    stage.innerHTML = '<div class="kiosk-panel"><img src="/assets/demos/kiosk/panel08.webp" alt="Kiosk screen: thank you">' +
      '<button class="kiosk-restart" type="button" id="kiosk-again">Run it again</button></div>';
    el('#kiosk-again').addEventListener('click', renderStart);
    say('수고하셨습니다.');
    report(seconds, speed);
  }

  function pathSvg() {
    if (state.points.length < 2) return '';
    const r = stage.getBoundingClientRect();
    const d = state.points.map((p, i) => (i ? 'L' : 'M') + p[0] + ' ' + p[1]).join(' ');
    const last = state.points[state.points.length - 1];
    return '<svg class="kiosk-path" viewBox="0 0 ' + Math.round(r.width) + ' ' + Math.round(r.height) + '" role="img" ' +
      'aria-label="The path your pointer travelled"><path d="' + d + '"></path>' +
      '<circle cx="' + last[0] + '" cy="' + last[1] + '" r="5"></circle></svg>';
  }

  function report(seconds, speed) {
    const errors = state.errors;
    const taken = Math.max(1, Math.round(seconds));
    const perStep = seconds / 6;
    const saved = Math.round(errors * perStep);
    const target = Math.max(1, taken - saved);
    const best = Number(localStorage.getItem(KEY) || 0);
    const isBest = !best || seconds < best;
    if (isBest) localStorage.setItem(KEY, String(Math.round(seconds * 10) / 10));

    const measures =
      '<ul class="kiosk-measures">' +
        '<li><b>Time to completion</b><span>' + seconds.toFixed(1) + ' s</span></li>' +
        '<li><b>Number of errors</b><span>' + errors + '</span></li>' +
        '<li><b>Hand movement speed</b><span>' + Math.round(speed) + ' px/s</span></li>' +
        '<li class="absent"><b>Scanpath length</b><span>needs an eye tracker</span></li>' +
      '</ul>';

    // Both reports describe the same three numbers. Only the direction of the
    // conditional changes — the contrast the narrative study was built on.
    const back = errors && saved >= 1
      ? '<p>You made <b>' + errors + '</b> ' + (errors === 1 ? 'wrong selection' : 'wrong selections') +
        '. Had you chosen correctly at each step, this order would have taken about <b>' + target +
        ' seconds</b> rather than ' + taken + '.</p>' +
        '<p>Your hand moved at ' + Math.round(speed) + ' pixels per second. Had it moved more slowly while ' +
        'searching the menu, the same wrong turns would have cost more than they did.</p>'
      : '<p>You made <b>no wrong selections</b>, and the order took <b>' + taken + ' seconds</b>. Had you ' +
        'paused at even one step to re-read the menu, that number would have grown.</p>' +
        '<p>Your hand moved at ' + Math.round(speed) + ' pixels per second. Had it wandered between items ' +
        'before settling, the same six steps would have covered more ground.</p>';

    const forward = errors && saved >= 1
      ? '<p>You made <b>' + errors + '</b> ' + (errors === 1 ? 'wrong selection' : 'wrong selections') +
        '. If you avoid them next time and keep this pace, your order will take about <b>' + target +
        ' seconds</b>.</p>' +
        '<p>Your hand moves at ' + Math.round(speed) + ' pixels per second. If you keep that speed while ' +
        'reading ahead to the next step, the wrong turns will disappear before they cost anything.</p>'
      : '<p>You made <b>no wrong selections</b>, and the order took <b>' + taken + ' seconds</b>. If you keep ' +
        'this up on an unfamiliar menu, the result will hold.</p>' +
        '<p>Your hand moves at ' + Math.round(speed) + ' pixels per second. If it keeps moving straight to ' +
        'each target, the distance it covers will stay short as the task gets longer.</p>';

    result.innerHTML =
      '<h3>Your measurements</h3>' + measures +
      '<p class="kiosk-best">' + (isBest ? 'That is your fastest run in this browser.'
        : 'Your fastest run in this browser is ' + best + ' s.') + '</p>' +
      '<figure class="paper-figure">' + pathSvg() +
        '<figcaption class="kiosk-figcaption">Where your pointer went. The study recorded the same thing from a ' +
        'hand controller tracked by base stations; its length divided by time is one of the four biomarkers.</figcaption>' +
      '</figure>' +

      '<h3 id="kiosk-report">Two reports of the same result</h3>' +
      '<p>A separate study asked which kind of explanation actually moves someone to act. Both reports below ' +
      'describe the run you just finished, in the two forms it compared.</p>' +
      '<div class="card-grid" id="kiosk-choice">' +
        '<article class="card"><span class="card-index">COUNTERFACTUAL</span>' +
          '<h3>The impact of past inputs on present outcomes</h3>' + back +
          '<button class="button secondary" type="button" data-pick="counterfactual">This one moves me</button></article>' +
        '<article class="card"><span class="card-index">PREFACTUAL</span>' +
          '<h3>The impact of present inputs on future outcomes</h3>' + forward +
          '<button class="button secondary" type="button" data-pick="prefactual">This one moves me</button></article>' +
      '</div>' +
      '<div id="kiosk-reveal"></div>' +
      '<p class="kiosk-note"><strong>A demonstration, not a screening test.</strong> The study reached a diagnosis ' +
      'through clinical assessment, an MRI scan and an eye-tracking headset; this page reproduces the task and three ' +
      'of its measures. Nothing you do here leaves your browser.</p>' +
      '<div class="kiosk-actions"><a class="button" href="/publications/multimodal-biomarkers-jmir/">The kiosk study &rarr;</a>' +
      '<a class="button secondary" href="/publications/counterfactual-prefactual-hci2023/">The narrative study &rarr;</a></div>';

    result.hidden = false;
    result.querySelectorAll('[data-pick]').forEach(b => b.addEventListener('click', () => reveal(b.dataset.pick)));
    el('#kiosk-report').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function reveal(pick) {
    localStorage.setItem('kiosk-narrative-pick', pick);
    const mechanism = pick === 'counterfactual'
      ? 'Readers of the counterfactual report looked <b>back</b>. They revisited what they had done, and asked how the analysis had reached its conclusion. The mechanism was <b>self-reflection</b>.'
      : 'Readers of the prefactual report looked <b>forward</b>. They started planning what to change. The mechanism was <b>self-improvement</b>.';
    el('#kiosk-reveal').innerHTML =
      '<div class="research-note">' +
      '<p>Twenty participants read one of these two reports and rated it on the System Causability Scale. ' +
      'The scores came out <b>the same</b>: neither form explained better than the other.</p>' +
      '<p>The interviews were where they parted. ' + mechanism + '</p>' +
      '<p>So the choice is not which report is clearer. It is which of the two things you want a reader to do.</p>' +
      '</div>';
    el('#kiosk-choice').querySelectorAll('button').forEach(b => { b.disabled = true; });
  }

  renderStart();
  const sayBtn = el('#kiosk-say');
  if (sayBtn) sayBtn.addEventListener('click', () => { if (state.step >= 0) say(STEPS[state.step].ko); });
})();
