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
 * The order is spoken once, from a shipped audio file, before the task starts —
 * as in the study, where the instruction was given verbally beforehand and the
 * kiosk itself said nothing. Each screen's own instruction is written under it,
 * never spoken: narrating the steps would cue the memory being measured.
 *
 * Everything stays in the browser.
 */
(() => {
  // Measured off the panels rather than eyeballed, so the targets sit on the
  // cards instead of around them.
  const COL = [[3.5, 24.2], [27.6, 48.3], [51.8, 72.4], [75.9, 96.5]];
  const BACK = { x: 62, y: 2.2, w: 35, h: 5.5 };
  const PIN = '6289';   // the study's own password, JMIR 2024;26:e54538
  const box = (col, top, bottom) => ({ x: COL[col][0], w: COL[col][1] - COL[col][0], y: top, h: bottom - top });
  const back = { label: '이전 화면', area: BACK, back: true };

  const STEPS = [
    {
      panel: 'panel01', ko: '주문을 시작하려면 시작버튼을 눌러주세요.',
      en: 'Touch the Start button to begin your order.',
      hits: [{ label: 'Start', area: { x: 19, y: 45, w: 62, h: 33 }, round: true }],
    },
    {
      panel: 'panel02', ko: '식사하실 장소를 선택해 주세요.',
      en: 'Where will you eat?', target: 'Eat in',
      hits: [
        { label: 'Eat in', area: { x: 5, y: 47, w: 43, h: 31 } },
        { label: 'Take out', area: { x: 52, y: 47, w: 43, h: 31 } },
      ],
    },
    {
      panel: 'panel03', ko: '햄버거 메뉴를 선택해 주세요.',
      en: 'Choose a burger.', target: '새우버거',
      hits: [
        back,
        { label: '소고기버거', area: box(0, 31.3, 42.6) }, { label: '치즈버거', area: box(1, 31.3, 42.6) },
        { label: '치킨버거', area: box(2, 31.3, 42.6) }, { label: '마늘버거', area: box(3, 31.3, 42.6) },
        { label: '불고기버거', area: box(0, 45.8, 57.1) }, { label: '양파버거', area: box(1, 45.8, 57.1) },
        { label: '새우버거', area: box(2, 45.8, 57.1) }, { label: '토마토버거', area: box(3, 45.8, 57.1) },
      ],
    },
    {
      panel: 'panel04', ko: '사이드 메뉴를 선택해 주세요.',
      en: 'Choose a side.', target: '치즈스틱',
      hits: [
        back,
        { label: '감자튀김', area: box(0, 45.8, 57.1) }, { label: '치즈스틱', area: box(1, 45.8, 57.1) },
        { label: '스트링 치즈', area: box(2, 45.8, 57.1) }, { label: '해시브라운', area: box(3, 45.8, 57.1) },
        { label: '치킨 랩', area: box(0, 60.8, 72.1) }, { label: '사과 파이', area: box(1, 60.8, 72.1) },
        { label: '핫케이크', area: box(2, 60.8, 72.1) }, { label: '치킨 너겟', area: box(3, 60.8, 72.1) },
      ],
    },
    {
      panel: 'panel05', ko: '음료 메뉴를 선택해 주세요.',
      en: 'Choose a drink.', target: '코카콜라',
      hits: [
        back,
        { label: '코카콜라', area: box(0, 60.8, 72.1) }, { label: '사이다', area: box(1, 60.8, 72.1) },
        { label: '환타 오렌지', area: box(2, 60.8, 72.1) }, { label: '생수', area: box(3, 60.8, 72.1) },
        { label: '바닐라 쉐이크', area: box(0, 75.8, 87.1) }, { label: '초코 쉐이크', area: box(1, 75.8, 87.1) },
        { label: '딸기 쉐이크', area: box(2, 75.8, 87.1) }, { label: '우유', area: box(3, 75.8, 87.1) },
      ],
    },
    {
      panel: 'panel06', ko: '주문을 확인하시고 결제 방법을 선택해 주세요.',
      en: 'Check your order, then choose a payment method.', target: '카드 결제',
      hits: [
        back,
        { label: '카드 결제', area: { x: 3, y: 56, w: 44, h: 30 } },
        { label: '모바일 상품권', area: { x: 51, y: 56, w: 44, h: 30 } },
      ],
    },
    { panel: 'panel07', ko: '비밀번호를 입력해 주세요.', en: 'Enter your four-digit number.', keypad: true },
  ];

  const KEY_X = [8, 39, 70], KEY_W = 22;
  const KEY_Y = [21.8, 35.3, 48.8, 62.3], KEY_H = 11.5;
  const KEYS = [
    ['1', 0, 0], ['2', 1, 0], ['3', 2, 0],
    ['4', 0, 1], ['5', 1, 1], ['6', 2, 1],
    ['7', 0, 2], ['8', 1, 2], ['9', 2, 2],
    ['clear', 0, 3], ['0', 1, 3], ['ok', 2, 3],
  ];
  // The four boxes the entered digits appear in, measured off the panel.
  const CODE_BOX = [[7.7, 23.4], [30.9, 46.7], [54.1, 69.9], [77.3, 93.1]];
  const CODE_Y = 80.9, CODE_H = 7.6;

  const el = (s, r = document) => r.querySelector(s);
  const stage = el('#kiosk-stage');
  const result = el('#kiosk-result');
  const caption = el('#kiosk-caption');
  if (!stage) return;

  const state = { step: -1, started: 0, errors: 0, distance: 0, points: [], last: null, code: '', chosen: {}, typed: false, pointer: '' };

  // Every screen is laid down once, stacked, and stays in the page for good.
  // Stepping through the task only changes which one is opaque, so no image is
  // ever created, fetched or decoded mid-run — the three things that made the
  // stage blink. The panels are decorative here: the instruction on each is in
  // the caption underneath, as text.
  // The screens are the study's own, so their Korean is baked into the image.
  // These chips sit on top of it, each filled with the colour sampled from the
  // panel underneath, so the English reads as part of the screen rather than as
  // a translation stuck beside it. Generated by scripts/build_kiosk_en.py.
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const enLayer = (panel) => ((window.KIOSK_EN || {})[panel] || []).map(i =>
    '<span class="kiosk-en" style="left:' + i.x + '%;top:' + i.y + '%;width:' + i.w + '%;height:' + i.h +
    '%;background:' + i.bg + ';color:' + i.c + ';font-size:' + i.s + 'cqw;text-align:' + i.a + '">' +
    i.t.map(esc).join('<br>') + '</span>').join('');

  const PANELS = STEPS.map(s => s.panel).concat('panel08');
  stage.innerHTML =
    '<div class="kiosk-panel">' +
      PANELS.map(p => '<img class="kiosk-screen" data-panel="' + p + '" alt="" ' +
        'src="/assets/demos/kiosk/' + p + '.webp">').join('') +
      PANELS.map(p => '<div class="kiosk-en-layer" data-panel="' + p + '">' + enLayer(p) + '</div>').join('') +
      '<div class="kiosk-overlay"></div>' +
    '</div>';
  const overlay = el('.kiosk-overlay');
  const screens = {};
  stage.querySelectorAll('.kiosk-screen').forEach(im => { screens[im.dataset.panel] = im; });
  const enLayers = {};
  stage.querySelectorAll('.kiosk-en-layer').forEach(d => { enLayers[d.dataset.panel] = d; });

  const showPanel = (panel) => {
    Object.keys(screens).forEach(p => {
      screens[p].classList.toggle('on', p === panel);
      enLayers[p].classList.toggle('on', p === panel);
    });
  };

  /* --- speech: pre-rendered clips ---------------------------------------- */
  // Files, not SpeechSynthesis. Most machines have no English voice installed
  // at all, and the ones that do each pick a different voice at a different
  // rate — not a stimulus you can time people against. These are identical
  // everywhere. Rendered with edge-tts, en-US-AriaNeural at -5%.
  // order.mp3 is the study's own spoken instruction, verbatim: "The place to
  // eat is a restaurant. Please use the kiosk to order a shrimp burger, cheese
  // sticks, and a Coca-Cola. Use a credit card as the payment method, and the
  // card payment password is 6 2 8 9." Change PIN above, or any target below, and
  // the clip has to be rendered again — see tools/gen_kiosk_audio.py.

  const player = new Audio();
  player.preload = 'auto';
  const sayBtn = el('#kiosk-say');
  let orderSpent = false;              // the order is heard once per attempt

  const spendOrder = () => {
    orderSpent = true;
    if (sayBtn) { sayBtn.disabled = true; sayBtn.textContent = 'Given once'; }
  };
  const armOrder = () => {
    orderSpent = false;
    if (sayBtn) { sayBtn.disabled = false; sayBtn.textContent = '🔊 Play the order'; }
  };

  // The standing warning — played once, memorise it — sits beside the button,
  // where it is read before anything is pressed. These two only track what to
  // do now.
  const READY_NOTE = 'Press play when you are ready.';
  const HELD_NOTE = 'That was the only time it is played. Touch Start when you have it.';

  const sayOrder = () => {
    if (orderSpent) return;
    player.src = '/assets/demos/kiosk/audio/order.mp3';
    const played = player.play();
    // Spend it only once it is really sounding: if the browser refuses to
    // play, the button has to survive.
    if (played) played.then(() => { spendOrder(); caption.textContent = HELD_NOTE; }, () => {});
  };

  /* --- pointer path ------------------------------------------------------ */
  stage.addEventListener('pointerdown', (e) => { if (e.pointerType) state.pointer = e.pointerType; });
  stage.addEventListener('pointermove', (e) => {
    if (e.pointerType) state.pointer = e.pointerType;
    if (state.step < 0) return;
    const r = stage.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    if (state.last) state.distance += Math.hypot(x - state.last.x, y - state.last.y);
    state.last = { x, y };
    if (state.points.length < 4000) state.points.push([Math.round(x), Math.round(y)]);
  });

  /* --- rendering --------------------------------------------------------- */
  function paint(step, extra = '', silent = false) {
    const hits = (step.hits || []).map((h, i) =>
      '<button class="kiosk-hit' + (h.round ? ' round' : '') + '" type="button" data-i="' + i + '"' +
      ' aria-label="' + h.label + '" style="left:' + h.area.x + '%;top:' + h.area.y + '%;' +
      'width:' + h.area.w + '%;height:' + h.area.h + '%"></button>').join('');
    showPanel(step.panel);
    overlay.innerHTML = hits + extra;
    // The screen's own instruction, in English. A Korean participant could read
    // it off the panel, so a visitor who cannot read Korean should have it too —
    // but written, not spoken. The study's only spoken instruction came before
    // the test; narrating each step would cue the memory the task is measuring.
    caption.textContent = silent ? '' : step.en;
  }

  function renderStep() {
    const step = STEPS[state.step];
    if (step.keypad) return renderKeypad();
    paint(step);
    stage.querySelectorAll('[data-i]').forEach(b => b.addEventListener('click', () => {
      const hit = step.hits[Number(b.dataset.i)];
      if (hit.back) return goBack();
      // The kiosk does not correct anyone. A wrong item is ordered, counted,
      // and the task moves on — the participant only finds out at the end.
      if (step.target) {
        state.chosen[step.panel] = hit.label;
        if (hit.label !== step.target) state.errors += 1;
      }
      advance();
    }));
  }

  function renderKeypad() {
    const step = STEPS[state.step];
    const keys = KEYS.map(([k, cx, cy]) =>
      '<button class="kiosk-hit" type="button" data-k="' + k + '" aria-label="' + k + '"' +
      ' style="left:' + KEY_X[cx] + '%;top:' + KEY_Y[cy] + '%;width:' + KEY_W + '%;height:' + KEY_H + '%"></button>').join('');
    const digits = CODE_BOX.map(([x0, x1], i) =>
      '<span class="kiosk-digit" style="left:' + x0 + '%;top:' + CODE_Y + '%;width:' + (x1 - x0) +
      '%;height:' + CODE_H + '%">' +
      // The digit just pressed stays visible; the ones before it are masked,
      // the way a real payment pad behaves.
      (state.code[i] ? (i === state.code.length - 1 ? state.code[i] : '•') : '') +
      '</span>').join('');
    // Only the first arrival at this screen is announced; typing does not
    // restart the prompt.
    paint(step, keys + '<div class="kiosk-code" aria-live="polite">' + digits + '</div>', state.typed);
    state.typed = true;
    stage.querySelectorAll('[data-k]').forEach(b => b.addEventListener('click', () => {
      const k = b.dataset.k;
      if (k === 'clear') state.code = state.code.slice(0, -1);
      else if (k === 'ok') {
        if (!state.code.length) return;
        // Submitting the wrong number is allowed, and counted, like any other
        // wrong selection.
        if (state.code !== PIN) state.errors += 1;
        return finish();
      } else if (state.code.length < 4) state.code += k;
      renderKeypad();
    }));
  }

  function begin() {
    spendOrder();                      // it is not repeated once you begin
    Object.assign(state, { step: 1, started: performance.now(), errors: 0, distance: 0, points: [], last: null, code: '', chosen: {}, typed: false });
    result.hidden = true;
    renderStep();
  }

  function advance() {
    if (state.step === 0) return begin();
    state.step += 1;
    renderStep();
  }

  function goBack() {
    if (state.step <= 1) return;
    state.step -= 1;
    state.typed = false;
    renderStep();
  }

  function renderStart() {
    state.step = 0;
    armOrder();
    paint(STEPS[0], '', true);
    // The order is spoken, never written: reading it off the screen would
    // remove the memory demand the task exists to measure.
    caption.textContent = READY_NOTE;
    // Not played automatically. Where autoplay is allowed the order would be
    // spent before anyone was listening, and where it is blocked it would not
    // sound at all — the button is the one behaviour every browser agrees on,
    // and it also means the clip starts when the participant is ready.
    el('[data-i]').addEventListener('click', begin);
  }

  /* --- results ----------------------------------------------------------- */
  const KEY = 'kiosk-best-seconds';

  function finish() {
    const seconds = (performance.now() - state.started) / 1000;
    const speed = state.distance / seconds;
    state.step = -1;
    caption.textContent = '';
    showPanel('panel08');
    overlay.innerHTML = '<button class="kiosk-restart" type="button" id="kiosk-again">Run it again</button>';
    el('#kiosk-again').addEventListener('click', renderStart);
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
    // A mouse is dragged between targets, so the pointer traces a path the way
    // a hand controller did. A finger only reports where it lands: the straight
    // lines between taps are not a hand path, so the speed is not measured.
    const mouse = state.pointer !== 'touch' && state.points.length > 12;
    const best = Number(localStorage.getItem(KEY) || 0);
    const isBest = !best || seconds < best;
    if (isBest) localStorage.setItem(KEY, String(Math.round(seconds * 10) / 10));

    // What was actually ordered, against what was asked for. The kiosk never
    // said anything at the time.
    const asked = { panel02: 'Eat in', panel03: '새우버거', panel04: '치즈스틱', panel05: '코카콜라', panel06: '카드 결제' };
    const wrongItems = Object.keys(asked)
      .filter(k => state.chosen[k] && state.chosen[k] !== asked[k])
      .map(k => state.chosen[k] + ' (asked for ' + asked[k] + ')');
    const wrongPin = state.code !== PIN;
    const slips = wrongItems.concat(wrongPin ? ['payment number ' + (state.code || 'blank') + ' (asked for ' + PIN + ')'] : []);
    const orderNote = slips.length
      ? '<p class="kiosk-best">You ordered ' + slips.join(', ') + '.</p>'
      : '<p class="kiosk-best">Everything you ordered matched the request.</p>';

    // Table 3 of the study: healthy controls (n=22) against patients with mild
    // cognitive impairment (n=32), mean (SD). Only the two performance measures
    // are quoted — hand speed there was metres per second of a tracked hand,
    // which a mouse in pixels cannot be held against.
    const HC = { time: 39.5, errors: 1.7 };
    const MCI = { time: 105.4, errors: 4.0 };
    const nearHc = v => (a, b) => Math.abs(v - a) <= Math.abs(v - b);
    const timeHc = nearHc(seconds)(HC.time, MCI.time);
    const errHc = nearHc(errors)(HC.errors, MCI.errors);
    const placing = timeHc && errHc
      ? 'Both of your numbers fall on the healthy control side of that gap.'
      : (!timeHc && !errHc
        ? 'Both of your numbers fall on the far side of it — which in a browser usually means a menu you ' +
          'cannot read, rather than anything about you.'
        : 'One of your numbers falls on each side of it.');
    // Where the numbers land, not what they mean about the reader. This task
    // has no eye tracker, a mouse instead of a tracked hand, and none of the
    // clinical assessment the study's diagnoses actually rested on.
    const against =
      '<h3>Against the study</h3>' +
      '<p>You have just ordered a burger. The same six steps took the healthy controls <b>' + HC.time +
      ' s</b> and <b>' + HC.errors + ' errors</b> on average; the participants with mild cognitive ' +
      'impairment took <b>' + MCI.time + ' s</b> and made <b>' + MCI.errors + '</b>. That distance is ' +
      'the whole finding. You took <b>' + seconds.toFixed(1) + ' s</b> and made <b>' + errors + '</b>. ' +
      placing + '</p>' +
      // The full disclaimer lives once, at the foot of the report. Here it only
      // has to stop the sentence above from being read as a verdict.
      '<p class="kiosk-caveat">Numbers beside numbers. A browser cannot screen anyone for anything.</p>';

    const measures =
      '<ul class="kiosk-measures">' +
        '<li><b>Time to completion</b><span>' + seconds.toFixed(1) + ' s</span></li>' +
        '<li><b>Number of errors</b><span>' + errors + '</span></li>' +
        (mouse
          ? '<li><b>Hand movement speed</b><span>' + Math.round(speed) + ' px/s</span></li>'
          : '<li class="absent"><b>Hand movement speed</b><span>needs a mouse</span></li>') +
        '<li class="absent"><b>Scanpath length</b><span>needs an eye tracker</span></li>' +
      '</ul>';

    // Both reports describe the same three numbers. Only the direction of the
    // conditional changes — the contrast the narrative study was built on.
    const speedLine = (a, b) => mouse ? a : b;
    const secs = n => n + (n === 1 ? ' second' : ' seconds');
    // Branch on the errors themselves, never on what they cost: a fast run can
    // round the cost to zero, and the report used to answer that by claiming
    // there had been no wrong selections at all, one line under a count saying
    // otherwise.
    const back = errors
      ? '<p>You made <b>' + errors + '</b> ' + (errors === 1 ? 'wrong selection' : 'wrong selections') +
        (saved >= 1
          ? '. Had you chosen correctly at each step, this order would have taken about <b>' + target +
            '</b> rather than ' + secs(taken) + '.</p>'
          : '. At this pace they cost you almost nothing &mdash; but each was a step you took twice.</p>') +
        speedLine('<p>Your hand moved at ' + Math.round(speed) + ' pixels per second. Had it moved more slowly while ' +
        'searching the menu, the same wrong turns would have cost more than they did.</p>', '')
      : '<p>You made <b>no wrong selections</b>, and the order took <b>' + secs(taken) + '</b>. Had you ' +
        'paused at even one step to re-read the menu, that number would have grown.</p>' +
        speedLine('<p>Your hand moved at ' + Math.round(speed) + ' pixels per second. Had it wandered between items ' +
        'before settling, the same six steps would have covered more ground.</p>', '');

    const forward = errors
      ? '<p>You made <b>' + errors + '</b> ' + (errors === 1 ? 'wrong selection' : 'wrong selections') +
        (saved >= 1
          ? '. If you avoid them next time and keep this pace, your order will take about <b>' +
            secs(target) + '</b>.</p>'
          : '. Avoid them next time and the same run comes in shorter still.</p>') +
        speedLine('<p>Your hand moves at ' + Math.round(speed) + ' pixels per second. If you keep that speed while ' +
        'reading ahead to the next step, the wrong turns will disappear before they cost anything.</p>', '')
      : '<p>You made <b>no wrong selections</b>, and the order took <b>' + secs(taken) + '</b>. If you keep ' +
        'this up on an unfamiliar menu, the result will hold.</p>' +
        speedLine('<p>Your hand moves at ' + Math.round(speed) + ' pixels per second. If it keeps moving straight to ' +
        'each target, the distance it covers will stay short as the task gets longer.</p>', '');

    result.innerHTML =
      '<h3>Your measurements</h3>' + measures + orderNote +
      '<p class="kiosk-best">' + (isBest ? 'That is your fastest run in this browser.'
        : 'Your fastest run in this browser is ' + best + ' s.') + '</p>' +
      against +
      (mouse
        ? '<figure class="paper-figure">' + pathSvg() +
            '<figcaption class="kiosk-figcaption">Where your pointer went. The study traced the same path with a ' +
            'tracked hand controller &mdash; its length over time is one of the four biomarkers.</figcaption>' +
          '</figure>'
        : '<p class="kiosk-note"><strong>Hand movement was not measured.</strong> A finger reports where it lands, ' +
          'not the path between. Run this with a mouse and the speed and the path both appear.</p>') +

      '<div class="kiosk-handoff"><p><b>Your run is now a set of numbers.</b> Someone still has to be told what ' +
      'they mean &mdash; and the wording changes what they do about it. A second study wrote the same result ' +
      'two ways to find out.</p>' +
      '<button class="button" type="button" id="kiosk-open-report">Read your report &rarr;</button></div>' +

      '<div id="kiosk-report-body" hidden>' +
      '<h3 id="kiosk-report">Your result, written two ways</h3>' +
      '<p>Same run, both of them. Pick the one that would actually make you do something differently.</p>' +
      '<div class="card-grid" id="kiosk-choice">' +
        '<article class="card"><span class="card-index">COUNTERFACTUAL</span>' +
          '<h3>The impact of past inputs on present outcomes</h3>' + back +
          '<button class="button secondary" type="button" data-pick="counterfactual">This one moves me</button></article>' +
        '<article class="card"><span class="card-index">PREFACTUAL</span>' +
          '<h3>The impact of present inputs on future outcomes</h3>' + forward +
          '<button class="button secondary" type="button" data-pick="prefactual">This one moves me</button></article>' +
      '</div>' +
      '<div id="kiosk-reveal"></div></div>' +
      '<p class="kiosk-note"><strong>A demonstration, not a screening test.</strong> The study reached a diagnosis ' +
      'through clinical assessment, an MRI scan and an eye-tracking headset; this page reproduces the task and three ' +
      'of its measures. Nothing you do here leaves your browser.</p>' +
      '<div class="kiosk-actions"><a class="button" href="/publications/multimodal-biomarkers-jmir/">The kiosk study &rarr;</a>' +
      '<a class="button secondary" href="/publications/counterfactual-prefactual-hci2023/">The narrative study &rarr;</a></div>';

    result.hidden = false;
    result.querySelectorAll('[data-pick]').forEach(b => b.addEventListener('click', () => reveal(b.dataset.pick)));
    el('#kiosk-open-report').addEventListener('click', (e) => {
      el('#kiosk-report-body').hidden = false;
      e.currentTarget.parentNode.hidden = true;
      el('#kiosk-report').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
  // The button plays the order and nothing else: mid-task it would be a replay.
  if (sayBtn) sayBtn.addEventListener('click', sayOrder);
})();
