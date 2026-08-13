/* Virtual kiosk demo — the study's own screens.
 *
 * panel01–08 are the interface from the JMIR validation study, with click
 * targets laid over them in percentage coordinates so they scale. The flow is
 * the original one: start, where to eat, then burger / side / drink as an
 * accordion, then the order with its payment choice, then the keypad.
 *
 * Measures two of the study's four VR-derived biomarkers — time to completion
 * and number of errors. The other two stay with the study's hardware: hand
 * movement speed was a tracked hand in meters per second, which a mouse in
 * pixels cannot stand in for, and scanpath length needed the headset's eye
 * tracker.
 *
 * The order is spoken once, from a shipped audio file, before the task starts —
 * as in the study, where the instruction was given verbally beforehand and the
 * kiosk itself said nothing. Each screen's own instruction is written under it,
 * never spoken: narrating the steps would cue the memory being measured.
 *
 * Measurements stay in the browser. The only things that leave are two
 * anonymous GoatCounter events — a run started, a run finished — sent by
 * tally() below, carrying no times, errors or choices.
 */
(() => {
  // Measured off the panels rather than eyeballed, so a target sits on its card
  // instead of near it: each column, row and radius below is the card's own,
  // found by the same script that prepares the screens. Hand-set numbers had the
  // rows starting a third of a percent low and every radius a shade too tight,
  // which showed the moment a hover outline was drawn on top of a card.
  const COL = [[3.23, 23.93], [27.46, 48.16], [51.63, 72.33], [75.83, 96.53]];
  const TILE_R = 2.9, CARD_R = 6.54, KEY_R = 5.65;
  // The pill itself, and the same on every screen: the panels used to draw it
  // at five different distances from the edge, so build_kiosk_panels.py now moves
  // it to one — BACK_BOX there is this box.
  const BACK = { x: 62.89, y: 2.71, w: 33.2, h: 4.16 };
  const PIN = '6289';   // the study's own password, JMIR 2024;26:e54538
  const box = (col, top, bottom) => ({ x: COL[col][0], w: COL[col][1] - COL[col][0], y: top, h: bottom - top });
  const back = { label: '이전 화면', area: BACK, back: true, r: 4.2 };   // half its own height: a pill

  const STEPS = [
    {
      panel: 'panel01', ko: '주문을 시작하려면 시작버튼을 눌러주세요.',
      en: 'Touch the Start button to begin your order.',
      hits: [{ label: 'Start', area: { x: 16.7, y: 46.2, w: 67.3, h: 33.6 }, round: true }],
    },
    {
      panel: 'panel02', ko: '식사하실 장소를 선택해 주세요.',
      en: 'Where will you eat?', target: 'Eat in',
      hits: [
        { label: 'Eat in', area: { x: 2.91, y: 47.76, w: 45.15, h: 30.14 }, r: CARD_R },
        { label: 'Take out', area: { x: 51.29, y: 47.76, w: 45.15, h: 30.14 }, r: CARD_R },
      ],
    },
    {
      panel: 'panel03', ko: '햄버거 메뉴를 선택해 주세요.',
      en: 'Choose a burger.', target: '새우버거',
      hits: [
        back,
        { label: '소고기버거', area: box(0, 32.12, 43.43), r: TILE_R }, { label: '치즈버거', area: box(1, 32.12, 43.43), r: TILE_R },
        { label: '치킨버거', area: box(2, 32.12, 43.43), r: TILE_R }, { label: '마늘버거', area: box(3, 32.12, 43.43), r: TILE_R },
        { label: '불고기버거', area: box(0, 46.14, 57.45), r: TILE_R }, { label: '양파버거', area: box(1, 46.14, 57.45), r: TILE_R },
        { label: '새우버거', area: box(2, 46.14, 57.45), r: TILE_R }, { label: '토마토버거', area: box(3, 46.14, 57.45), r: TILE_R },
      ],
    },
    {
      panel: 'panel04', ko: '사이드 메뉴를 선택해 주세요.',
      en: 'Choose a side.', target: '치즈스틱',
      hits: [
        back,
        { label: '감자튀김', area: box(0, 45.94, 57.21), r: TILE_R }, { label: '치즈스틱', area: box(1, 45.94, 57.21), r: TILE_R },
        { label: '스트링 치즈', area: box(2, 45.94, 57.21), r: TILE_R }, { label: '해시브라운', area: box(3, 45.94, 57.21), r: TILE_R },
        { label: '치킨 랩', area: box(0, 59.96, 71.23), r: TILE_R }, { label: '사과 파이', area: box(1, 59.96, 71.23), r: TILE_R },
        { label: '핫케이크', area: box(2, 59.96, 71.23), r: TILE_R }, { label: '치킨 너겟', area: box(3, 59.96, 71.23), r: TILE_R },
      ],
    },
    {
      panel: 'panel05', ko: '음료 메뉴를 선택해 주세요.',
      en: 'Choose a drink.', target: '코카콜라',
      hits: [
        back,
        { label: '코카콜라', area: box(0, 59.47, 70.70), r: TILE_R }, { label: '사이다', area: box(1, 59.47, 70.70), r: TILE_R },
        { label: '환타 오렌지', area: box(2, 59.47, 70.70), r: TILE_R }, { label: '생수', area: box(3, 59.47, 70.70), r: TILE_R },
        { label: '바닐라 쉐이크', area: box(0, 73.41, 84.72), r: TILE_R }, { label: '초코 쉐이크', area: box(1, 73.41, 84.72), r: TILE_R },
        { label: '딸기 쉐이크', area: box(2, 73.41, 84.72), r: TILE_R }, { label: '우유', area: box(3, 73.41, 84.72), r: TILE_R },
      ],
    },
    {
      panel: 'panel06', ko: '주문을 확인하시고 결제 방법을 선택해 주세요.',
      en: 'Check your order, then choose a payment method.', target: '카드 결제',
      hits: [
        back,
        // The voucher card is drawn a third of a percent higher than the card
        // beside it; both hits follow their own card rather than one average.
        { label: '카드 결제', area: { x: 3.23, y: 56.61, w: 45.15, h: 30.14 }, r: CARD_R },
        { label: '모바일 상품권', area: { x: 51.62, y: 56.24, w: 45.07, h: 30.14 }, r: CARD_R },
      ],
    },
    { panel: 'panel07', ko: '비밀번호를 입력해 주세요.', en: 'Enter your four-digit number.', keypad: true },
  ];

  // The twelve keys are drawn on a perfectly regular grid; these are its own
  // numbers rather than an approximation of them.
  const KEY_X = [6.46, 37.48, 68.58], KEY_W = 24.98;
  const KEY_Y = [21.74, 35.64, 49.54, 63.47], KEY_H = 12.24;
  const KEYS = [
    ['1', 0, 0], ['2', 1, 0], ['3', 2, 0],
    ['4', 0, 1], ['5', 1, 1], ['6', 2, 1],
    ['7', 0, 2], ['8', 1, 2], ['9', 2, 2],
    ['clear', 0, 3], ['0', 1, 3], ['ok', 2, 3],
  ];
  // The four boxes the entered digits appear in, measured off the panel.
  const CODE_BOX = [[7.7, 23.4], [30.9, 46.7], [54.1, 69.9], [77.3, 93.1]];
  const CODE_Y = 80.3, CODE_H = 8.2;

  // Hit labels stay the panels' own Korean — they are what the screens say —
  // but everything the visitor reads (aria, the wrong-item list) speaks the
  // same English as the chips laid over those screens.
  const EN = {
    '이전 화면': 'Back', '카드 결제': 'Card', '모바일 상품권': 'Mobile voucher',
    '소고기버거': 'Beef Burger', '치즈버거': 'Cheese Burger', '치킨버거': 'Chicken Burger',
    '마늘버거': 'Garlic Burger', '불고기버거': 'Bulgogi Burger', '양파버거': 'Onion Burger',
    '새우버거': 'Shrimp Burger', '토마토버거': 'Tomato Burger',
    '감자튀김': 'Fries', '치즈스틱': 'Cheese Sticks', '스트링 치즈': 'String Cheese',
    '해시브라운': 'Hash Brown', '치킨 랩': 'Chicken Wrap', '사과 파이': 'Apple Pie',
    '핫케이크': 'Hotcake', '치킨 너겟': 'Chicken Nuggets',
    '코카콜라': 'Coca-Cola', '사이다': 'Cider', '환타 오렌지': 'Fanta Orange', '생수': 'Water',
    '바닐라 쉐이크': 'Vanilla Shake', '초코 쉐이크': 'Choco Shake', '딸기 쉐이크': 'Berry Shake',
    '우유': 'Milk',
  };
  const en = (k) => EN[k] || k;

  const el = (s, r = document) => r.querySelector(s);
  const stage = el('#kiosk-stage');
  const result = el('#kiosk-result');
  const caption = el('#kiosk-caption');
  if (!stage) return;

  // `chosen` is the order as it stands and `picks` is how it got there. Going back
  // overwrites a choice but not the error it counted — the study counts selections
  // that were not the item asked for, and one was made — so without the history a
  // corrected run looks like an order with an error in it and nothing wrong.
  const state = { step: -1, started: 0, errors: 0, code: '', chosen: {}, picks: [], typed: false };

  // scrollIntoView with an explicit behavior ignores the CSS reduced-motion
  // override, so the OS setting has to be read here too.
  const SCROLL = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';

  // Participation is counted, results are not: these events carry no time,
  // errors or choices — only that a run began or reached the report. The
  // optional chain keeps the demo whole if the counter is blocked or unloaded.
  const tally = (path, title) => window.goatcounter?.count?.({ path, title, event: true });

  // Every screen is laid down once, stacked, and stays in the page for good.
  // Stepping through the task only changes which one is opaque, so no image is
  // ever created, fetched or decoded mid-run — the three things that made the
  // stage blink. The panels are decorative here: the instruction on each is in
  // the caption underneath, as text.
  // The screens are the study's own, with the Korean lifted out of the pixels and
  // the cards that carried a fixed order left empty — see
  // scripts/build_kiosk_panels.py, which also measures where each label went and
  // in what colour. So the English is text on an empty band rather than a patch
  // laid over Korean, and there is no moment where the Korean is what you see.
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const enLayer = (panel) => ((window.KIOSK_EN || {})[panel] || []).map(i =>
    '<span class="kiosk-en" style="left:' + i.x + '%;top:' + i.y + '%;width:' + i.w + '%;height:' + i.h +
    '%;color:' + i.c + ';font-size:' + i.s + 'cqw;text-align:' + i.a +
    (i.r ? ';border-radius:' + i.r + 'cqw' : '') + '">' +
    i.t.map(esc).join('<br>') + '</span>').join('');

  /* --- what was actually ordered -------------------------------------------
   * The collapsed headers and the confirmation screen show the order so far. On
   * the study's screens that was a shrimp burger, cheese sticks and a Coca-Cola
   * whatever the visitor picked — the screens are one participant's run, caught as
   * photographs. Those cards now arrive empty and this fills them in.
   *
   * The photo is the item's own tile on the menu screen, seen through a window:
   * the panel is the background image, scaled so that one tile fills the card and
   * offset so that it is the tile you see. A percentage background-position
   * resolves against (container - image), so a crop starting at x% of a source
   * w% wide sits at x / (100 - w).
   */
  const CARDS = window.KIOSK_CARDS || { items: {}, slots: {} };

  const photoStyle = (item) => {
    const [x, y, w, h] = item.photo;
    return 'background-image:url(/assets/demos/kiosk/' + item.p + '-en.webp);' +
      'background-size:' + (100 / w * 100).toFixed(2) + '% ' + (100 / h * 100).toFixed(2) + '%;' +
      'background-position:' + (x / (100 - w) * 100).toFixed(3) + '% ' +
      (y / (100 - h) * 100).toFixed(3) + '%';
  };

  const cardLayer = (panel) => (CARDS.slots[panel] || []).map(s => {
    const item = CARDS.items[state.chosen[s.src]];
    if (!item) return '';          // nothing chosen yet: the card stays empty
    const band = (a, b) => 'top:' + a + '%;height:' + (b - a) + '%';
    return '<div class="kiosk-card" style="left:' + s.x + '%;top:' + s.y + '%;width:' + s.w +
      '%;height:' + s.h + '%;background:' + s.cw + ';border-radius:' + s.r + 'cqw">' +
      '<span class="kiosk-card-photo" style="height:' + s.photo + '%;' + photoStyle(item) + '"></span>' +
      '<b style="' + band(s.name[0], s.name[1]) + ';font-size:' + s.ns + 'cqw;color:' + s.nc + '">' +
        esc(item.en) + '</b>' +
      '<i style="' + band(s.price[0], s.price[1]) + ';font-size:' + s.ps + 'cqw;color:' + s.pc + '">' +
        esc(item.price) + '</i>' +
      '</div>';
  }).join('');

  const PANELS = STEPS.map(s => s.panel).concat('panel08');
  stage.innerHTML =
    '<div class="kiosk-panel">' +
      PANELS.map(p => '<img class="kiosk-screen" data-panel="' + p + '" alt="" ' +
        'src="/assets/demos/kiosk/' + p + '-en.webp">').join('') +
      PANELS.map(p => '<div class="kiosk-en-layer" data-panel="' + p + '">' + enLayer(p) + '</div>').join('') +
      '<div class="kiosk-overlay"></div>' +
      // The whole screen sits behind this veil until the order has been heard:
      // greyed, blurred, and itself the play button. It lifts when the clip
      // ends, which is also what makes the locked state legible — not one grey
      // circle to decode, but a kiosk that is visibly not on yet.
      '<button class="kiosk-veil" type="button" id="kiosk-veil" hidden>' +
        '<b>🔊 Listen first</b><span>The order is spoken once &mdash; press to play it.</span>' +
      '</button>' +
    '</div>';
  const overlay = el('.kiosk-overlay');
  const veil = el('#kiosk-veil');
  const veilTitle = veil.querySelector('b');
  const veilNote = veil.querySelector('span');
  const screens = {};
  stage.querySelectorAll('.kiosk-screen').forEach(im => { screens[im.dataset.panel] = im; });
  const enLayers = {};
  stage.querySelectorAll('.kiosk-en-layer').forEach(d => { enLayers[d.dataset.panel] = d; });

  // All eight screens stay in the page so that stepping through never waits on a
  // decode, but only the one on show may be read. Left in the accessibility tree,
  // the other seven let a screen reader read every menu — and the answers to a task
  // whose whole demand is holding an order in memory — before it has begun.
  const showPanel = (panel) => {
    Object.keys(screens).forEach(p => {
      const on = p === panel;
      screens[p].classList.toggle('on', on);
      enLayers[p].classList.toggle('on', on);
      screens[p].setAttribute('aria-hidden', String(!on));
      enLayers[p].setAttribute('aria-hidden', String(!on));
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

  // The veil is the only play control, and it carries all the wording too —
  // listen first, hold it in memory, not repeated. The caption underneath only
  // speaks during the task, one screen instruction at a time.
  const player = new Audio();
  player.preload = 'auto';
  let orderSpent = false;              // the order is heard once per attempt

  const spendOrder = () => { orderSpent = true; };
  const armOrder = () => { orderSpent = false; };

  // The Start button on screen: held until the order has been heard, because a
  // run started cold has nothing to remember — unusable numbers and a worse
  // report to read at the end.
  let startHit = null;
  const releaseStart = () => {
    if (!startHit || !startHit.disabled) return;
    startHit.disabled = false;
    startHit.classList.add('ready');   // the wash lifts and the ring pulses
  };

  // Faded out but still a button, the veil kept its place in the tab order and
  // could be pressed by a keyboard from behind the screen it had just uncovered.
  const liftVeil = () => { veil.classList.add('off'); veil.disabled = true; releaseStart(); };

  const sayOrder = () => {
    if (orderSpent) return;
    player.src = '/assets/demos/kiosk/audio/order.mp3';
    player.onended = liftVeil;
    const played = player.play();
    // Spend it only once it is really sounding — and if the browser refuses to
    // play, lift the veil anyway rather than locking the demo shut.
    if (played) played.then(
      () => {
        spendOrder();
        veil.classList.add('playing');
        veilTitle.textContent = 'Hold it in memory';
        veilNote.textContent = 'It is not repeated.';
      },
      () => { liftVeil(); });
  };

  /* --- rendering --------------------------------------------------------- */
  function paint(step, extra = '', silent = false) {
    // Each control's own corner radius, so the hover outline follows its shape
    // instead of cutting a 10px corner across a much rounder card or key.
    const hits = (step.hits || []).map((h, i) =>
      '<button class="kiosk-hit' + (h.round ? ' round' : '') + '" type="button" data-i="' + i + '"' +
      ' aria-label="' + en(h.label) + '" style="left:' + h.area.x + '%;top:' + h.area.y + '%;' +
      'width:' + h.area.w + '%;height:' + h.area.h + '%' +
      (h.r ? ';border-radius:' + h.r + 'cqw' : '') + '"></button>').join('');
    showPanel(step.panel);
    // The cards are redrawn with every screen rather than once at the start:
    // what they show is whatever has been chosen by the time you arrive.
    overlay.innerHTML = hits + cardLayer(step.panel) + extra;
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
        state.picks.push({ panel: step.panel, label: hit.label, right: hit.label === step.target });
        if (hit.label !== step.target) state.errors += 1;
      }
      advance();
    }));
  }

  function renderKeypad() {
    const step = STEPS[state.step];
    const keys = KEYS.map(([k, cx, cy]) =>
      '<button class="kiosk-hit" type="button" data-k="' + k + '" aria-label="' + k + '"' +
      ' style="left:' + KEY_X[cx] + '%;top:' + KEY_Y[cy] + '%;width:' + KEY_W + '%;height:' + KEY_H + '%;' +
      'border-radius:' + KEY_R + 'cqw"></button>').join('');
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
    Object.assign(state, { step: 1, started: performance.now(), errors: 0, code: '', chosen: {}, picks: [], typed: false });
    result.hidden = true;
    tally('kiosk-run-started', 'Kiosk run started');
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
    // remove the memory demand the task exists to measure. It is also never
    // played automatically — where autoplay is allowed the clip would be spent
    // before anyone was listening, and where it is blocked it would not sound
    // at all. Pressing the veil is the one behavior every browser agrees on.
    startHit = el('[data-i]');
    startHit.disabled = true;
    startHit.addEventListener('click', begin);
    veil.hidden = false;
    veil.disabled = false;
    veil.classList.remove('off', 'playing');
    veilTitle.innerHTML = '🔊 Listen first';
    veilNote.innerHTML = 'The order is spoken once &mdash; press to play it.';
  }

  /* --- results ----------------------------------------------------------- */

  function finish() {
    const seconds = (performance.now() - state.started) / 1000;
    tally('kiosk-run-finished', 'Kiosk run finished');
    state.step = -1;
    caption.textContent = '';
    showPanel('panel08');
    // The restart lives in the report, where the reader is: one on the screen and
    // one under the result meant two buttons with the same words on the same page.
    overlay.innerHTML = '';
    report(seconds);
  }

  function report(seconds) {
    const errors = state.errors;

    // What was actually ordered, against what was asked for. The kiosk never
    // said anything at the time.
    const asked = { panel02: 'Eat in', panel03: '새우버거', panel04: '치즈스틱', panel05: '코카콜라', panel06: '카드 결제' };
    const wrongPanels = Object.keys(asked).filter(k => state.chosen[k] && state.chosen[k] !== asked[k]);
    const wrongItems = wrongPanels.map(k => en(state.chosen[k]) + ' (asked for ' + en(asked[k]) + ')');
    const wrongPin = state.code !== PIN;
    const slips = wrongItems.concat(wrongPin ? ['payment number ' + (state.code || 'blank') + ' (asked for ' + PIN + ')'] : []);
    // Steps that were got wrong and then put right: the order is correct, and the
    // error the study would have counted still happened.
    const fixes = Object.keys(asked)
      .filter(k => state.chosen[k] === asked[k] && state.picks.some(p => p.panel === k && !p.right))
      .map(k => ({ panel: k, first: en(state.picks.find(p => p.panel === k && !p.right).label) }));
    const fixList = fixes.map(f => f.first + ' for ' + en(asked[f.panel])).join(', ');
    const orderNote = slips.length
      ? '<p class="kiosk-best">You ordered ' + slips.join(', ') +
        (fixes.length ? ', and went back to change ' + fixList : '') + '.</p>'
      : fixes.length
        ? '<p class="kiosk-best">Everything you ordered matched the request &mdash; you went back to change ' +
          fixList + '.</p>'
        : '<p class="kiosk-best">Everything you ordered matched the request.</p>';

    // Table 3 of the study, means as printed: healthy controls (n=22) against
    // patients with mild cognitive impairment (n=32). All four biomarkers are
    // quoted; the two this page cannot take show the study's own figures with
    // an empty You cell, which says the same thing a footnote would.
    // Means as the study printed them, and the control group's spread on time,
    // which is what decides below whether a run has anything to say about it.
    const HC = { time: 39.48, timeSD: 18.96, errors: 1.73, speed: '0.23 m/s', scan: '23.66 m' };
    const MCI = { time: 105.39, errors: 4, speed: '0.17 m/s', scan: '60.36 m' };
    const nearHc = v => (a, b) => Math.abs(v - a) <= Math.abs(v - b);
    const timeHc = nearHc(seconds)(HC.time, MCI.time);
    const errHc = nearHc(errors)(HC.errors, MCI.errors);
    // Stated as distance to a printed mean, not as a side of a gap: "you are on
    // the healthy side" reads as a verdict about the reader no matter what the
    // disclaimer above it says.
    const placing = timeHc && errHc
      ? 'Both of your values are closer to the healthy-control means in the study.'
      : (!timeHc && !errHc
        ? 'Both of your values are closer to the means of the group with MCI — in a browser that ' +
          'usually means a menu you cannot read, not anything about you.'
        // Which of the two went which way is left to the table. Naming it — "your
        // errors are nearer the MCI mean" — reads as a finding about the reader
        // however carefully the line around it is worded.
        : 'Your two values fall on opposite sides: one is nearer the healthy-control mean, the '
          + 'other nearer the mean of the group with MCI. Which is which is in the table above.');
    // One table for everything: the four measures as rows, you beside the two
    // groups. It used to be a list of your numbers followed by a second table
    // repeating two of them against the study.
    const na = s => '<td class="na">' + s + '</td>';
    const vs =
      '<table class="kiosk-vs"><thead><tr><th></th><th>You</th>' +
      '<th>Healthy controls (n=22)</th><th>With MCI (n=32)</th></tr></thead><tbody>' +
      '<tr><th>Time to completion</th><td>' + seconds.toFixed(1) + ' s</td>' +
      '<td>' + HC.time + ' s</td><td>' + MCI.time + ' s</td></tr>' +
      '<tr><th>Number of errors</th><td>' + errors + '</td>' +
      '<td>' + HC.errors + '</td><td>' + MCI.errors + '</td></tr>' +
      '<tr><th>Hand movement speed</th>' + na('needs a hand controller') +
      '<td>' + HC.speed + '</td><td>' + MCI.speed + '</td></tr>' +
      '<tr><th>Scanpath length</th>' + na('needs an eye tracker') +
      '<td>' + HC.scan + '</td><td>' + MCI.scan + '</td></tr>' +
      '</tbody></table>' +
      // Where this run's numbers land, and nothing else. The line about a browser
      // not being able to screen anyone used to be repeated here; it is already
      // the disclaimer above the task, which is the place someone worried about
      // their memory reads it — before they hold a score, not after.
      '<p class="kiosk-vs-note">' + placing + ' These are the two groups&rsquo; averages from the ' +
      'study, not a score: a browser cannot screen anyone for anything.</p>';

    // Both reports describe the same run, and the only thing that differs between
    // them is where the conditional points: If you had / would have against If you /
    // will. Those are the study's own two forms — it wrote "If you did something, you
    // would do something" against "If you do something, you will do something" — and
    // they are the whole of what it varied, so they are the whole of what varies here:
    // same opening, same verb, same clause, same numbers on both sides.
    const WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six'];
    const misordered = wrongPanels.length;
    const picked = misordered ? en(state.chosen[wrongPanels[0]]) : '';
    const wanted = misordered ? en(asked[wrongPanels[0]]) : '';
    const count = n => (WORDS[n] || n);

    // What happened, in plain words and named, before either wording of it. The
    // report used to open on the framing alone — "the one item you picked instead"
    // — which is true and forgettable, and left the two versions reading as two
    // sayings rather than two readings of one run.
    const facts = [
      'You completed the order with ' + (errors ? count(errors) + ' error' + (errors === 1 ? '' : 's') : 'no errors') + '.',
      misordered === 1 ? 'You selected ' + picked + ' instead of ' + wanted + '.'
        : misordered > 1 ? 'You selected ' + wrongPanels.map(k => en(state.chosen[k]) + ' instead of ' + en(asked[k])).join(', ') + '.'
        : '',
      fixes.length ? 'You went back to change ' + fixList + '.' : '',
      wrongPin ? 'You typed ' + (state.code || 'nothing') + ' instead of ' + PIN + '.' : '',
    ].filter(Boolean).join(' ');

    // Both wordings say the same thing about the same choice; only the direction of
    // the conditional moves, which is the whole of what the study varied. Naming the
    // item is what makes that visible — the tense is easy to miss when the subject
    // is "the one item you picked instead".
    const taken = Math.max(1, Math.round(seconds));
    const hc = Math.round(HC.time);
    // One wrong item, or a time outside the control group's own spread: 39.48 s,
    // SD 18.96, both from the study's table. Inside that spread is an ordinary
    // control-group time with nothing to improve on, and a wording that promises an
    // improvement of nothing says nothing. The line is the study's number rather
    // than a round one picked here, and it decides what half the visitors read.
    const room = errors > 0 || seconds > HC.time + HC.timeSD;
    const pair = misordered === 1
      ? ['If you had chosen <b>' + wanted + '</b> instead of <b>' + picked + '</b>, your order <b>would have matched</b> the request.',
         'If you choose <b>' + wanted + '</b> instead of <b>' + picked + '</b> next time, your order <b>will match</b> the request.']
      : misordered > 1
      ? ['If you had chosen what was asked for at those ' + count(misordered) + ' steps, your order <b>would have matched</b> the request.',
         'If you choose what was asked for at those ' + count(misordered) + ' steps next time, your order <b>will match</b> the request.']
      : wrongPin
      ? ['If you had typed <b>' + PIN + '</b>, this order <b>would have gone</b> through as asked.',
         'If you type <b>' + PIN + '</b> next time, this order <b>will go</b> through as asked.']
      : fixes.length
      // Everything ended as asked and the error is a choice made and taken back, so
      // the pair points at the going back rather than at the order.
      ? ['If you had chosen <b>' + en(asked[fixes[0].panel]) + '</b> first, you <b>would not have gone</b> back to change it.',
         'If you choose <b>' + en(asked[fixes[0].panel]) + '</b> first next time, you <b>will not go</b> back to change it.']
      // Nothing was wrong, so the pair turns on pace, against the study's own mean
      // rather than a target invented here.
      : ['If you had matched the pace of the study&rsquo;s healthy controls, this order <b>would have taken</b> about ' + hc + ' seconds, not ' + taken + '.',
         'If you match the pace of the study&rsquo;s healthy controls next time, this order <b>will take</b> about ' + hc + ' seconds, not ' + taken + '.'];

    // One of the two, at random, and never both at once: side by side the reader
    // sees the manipulation and it stops working on them, which is also why
    // neither is labelled. The study gave one report to one person. The order of
    // the two ways on is drawn separately, because a wording randomised into a
    // fixed first position is still a fixed first position.
    const shown = Math.random() < 0.5 ? 0 : 1;
    const lookFirst = Math.random() < 0.5;
    const KIND = ['counterfactual', 'prefactual'];
    const LOOK = 'See this run step by step', AGAIN = 'Run it again';

    // The run, step by step, in the order the steps came. What was asked for at each
    // one comes from `asked` above, not from a second copy of the same five names:
    // the copy had a typo in it, and a name that does not match marks a step wrong
    // when it was right.
    const ORDER = [['panel02', 'Where to eat'], ['panel03', 'Burger'], ['panel04', 'Side'],
                   ['panel05', 'Drink'], ['panel06', 'Payment']];
    const stepList = () => '<ol class="kiosk-steps">' +
      ORDER.map(([panel, name]) => {
        const ask = asked[panel];
        const got = state.chosen[panel];
        const right = got === ask;
        const undone = right && state.picks.some(p => p.panel === panel && !p.right);
        return '<li' + (right ? (undone ? ' class="fixed"' : '') : ' class="wrong"') + '><b>' + name +
          '</b><span>' + (got ? en(got) : '&mdash;') +
          (right ? '' : ' <i>asked for ' + en(ask) + '</i>') +
          (undone ? ' <i>first picked ' + en(state.picks.find(p => p.panel === panel && !p.right).label) +
            '</i>' : '') + '</span></li>';
      }).join('') +
      '<li' + (state.code === PIN ? '' : ' class="wrong"') + '><b>Payment number</b><span>' +
      (state.code || 'blank') + (state.code === PIN ? '' : ' <i>asked for ' + PIN + '</i>') +
      '</span></li></ol>';

    // What the wording was, once it can no longer act on the reader. The caveat
    // comes before the reader's own behaviour is named: after it, the sentence is
    // read as a verdict on the click that has already been made.
    const TITLE = ['The impact of past inputs on present outcomes',
                   'The impact of present inputs on future outcomes'];
    const study =
      '<p>Twenty people each read one of the two &mdash; reports on an MRI result, not a lunch order. ' +
      'They rated them <b>equally clear</b>; what differed was where their attention went. The ' +
      '<b>counterfactual</b> readers dwelt on what had already happened, the <b>prefactual</b> readers ' +
      'on what to do next.</p>';
    // A run with nothing wrong in it is the one a reader is most likely to have,
    // and it used to end the section: no report, no wordings, nothing to see. The
    // example is somebody else's run, in the third person and labelled as such, so
    // that the best performance is not the one sent away from the point of the page.
    const example = () =>
      '<p class="kiosk-facts">An example, not your run. Someone completes the order with one error: ' +
      'they select Beef Burger instead of Shrimp Burger.</p>' +
      '<p class="kiosk-other"><b>' + KIND[0] + '</b> &mdash; &ldquo;' + TITLE[0] + '&rdquo;<br>' +
      'If they had chosen <b>Shrimp Burger</b> instead of <b>Beef Burger</b>, their order ' +
      '<b>would have matched</b> the request.</p>' +
      '<p class="kiosk-other"><b>' + KIND[1] + '</b> &mdash; &ldquo;' + TITLE[1] + '&rdquo;<br>' +
      'If they choose <b>Shrimp Burger</b> instead of <b>Beef Burger</b> next time, their order ' +
      '<b>will match</b> the request.</p>';
    const kept =
      '<p class="kiosk-vs-note">The study did not watch anyone go again; it asked them what the report ' +
      'made them think about. Nothing here was measured on you either: your time and errors never left ' +
      'this browser, and the only things that leave are two anonymous counts &mdash; a run started, a ' +
      'run finished.</p>';
    const reveal = () =>
      '<div class="research-note">' +
      (room
        ? '<p>Half of the people who get here read this instead:</p>' +
          '<p class="kiosk-other">' + pair[1 - shown] + '</p>' +
          '<p>Same facts, different tense. The study called yours the <b>' + KIND[shown] + '</b> report, ' +
          '&ldquo;' + TITLE[shown] + '&rdquo;, and that one the <b>' + KIND[1 - shown] + '</b>, &ldquo;' +
          TITLE[1 - shown] + '&rdquo;.</p>' +
          study
        : example() + study) +
      kept +
      '</div>';

    // Only what this run produced: the four measures, where they landed, and what
    // was ordered against what was asked for. A personal best from an earlier run
    // sat here too, and every extra line pushed the one thing worth pressing —
    // the report — further off the screen.
    const ways = [
      '<button class="button" type="button" data-act="look">' + LOOK + '</button>',
      '<button class="button" type="button" data-act="again">' + AGAIN + '</button>',
    ];
    result.innerHTML =
      '<h3>Your measurements, against the study</h3>' + vs + orderNote +

      '<div class="kiosk-handoff"><p><b>Your run is now a set of numbers</b> &mdash; and how a report words ' +
      // Attention, not behaviour: the study asked its readers what the report made
      // them think about rather than watching what they did, and this line is the
      // first the reader meets. Promising a change in behaviour here and explaining
      // a change in attention two screens later is the same overclaim twice.
      'them changes where its reader&rsquo;s attention goes. A second study wrote the same result ' +
      'two ways.</p>' +
      '<button class="button" type="button" id="kiosk-open-report">Read your report &rarr;</button></div>' +

      '<div id="kiosk-report-body" hidden>' +
      '<h3 id="kiosk-report">Your result</h3>' +
      '<p class="kiosk-facts">' + facts + '</p>' +
      (room
        ? '<p class="kiosk-report-line">' + pair[shown] + '</p>' +
          '<div class="kiosk-actions" id="kiosk-next">' +
            '<button class="button" type="button" data-act="other">See the other version</button>' +
          '</div>'
        : '<p class="kiosk-report-line">Your run had no error to explain, so a report of it cannot be ' +
          'written either way &mdash; which is also what the study&rsquo;s two reports needed a result ' +
          'for.</p>' +
          '<div class="kiosk-actions" id="kiosk-next">' +
            '<button class="button" type="button" data-act="example">Show me an example anyway</button>' +
          '</div>') +
      '<div id="kiosk-reveal"></div>' +
      // The two ways on come after the explanation rather than before it. They used
      // to gate it, so that pressing one could not be coloured by knowing what the
      // wordings were — which mattered while the press was thought to be what the
      // study measured, and stopped mattering when it turned out to have asked its
      // readers instead.
      '<div class="kiosk-actions" id="kiosk-ways" hidden>' +
        (lookFirst ? ways[0] + ways[1] : ways[1] + ways[0]) +
      '</div>' +
      '<div id="kiosk-steps-out"></div></div>' +
      // The two studies leave in the same form, side by side — one used to be
      // a button and the other an inline link, which read as different kinds
      // of thing. The old "demonstration, not a screening test" note is gone:
      // the one line under the comparison table already does that job.
      '<div class="kiosk-actions"><a class="button" href="/publications/multimodal-biomarkers-jmir/">The kiosk study &rarr;</a>' +
      '<a class="button secondary" href="/publications/counterfactual-prefactual-hci2023/">The narrative study &rarr;</a></div>';

    result.hidden = false;
    // Focused rather than announced: a live region would read the whole table, the
    // report and both study links out in one breath. Taking the reader to it lets
    // them read it at their own pace, and the scroll below does the same visually.
    result.focus({ preventScroll: true });
    // Reading the run back explains nothing and takes nothing away: it opens in
    // place, both ways on stay, and the reader can still go again afterwards. The
    // explanation waits for that, or for the reader to ask for it outright — put on
    // the first click, it would have contaminated every re-run that followed it.
    result.querySelectorAll('[data-act]').forEach(b => b.addEventListener('click', () => {
      const act = b.dataset.act;
      if (act === 'look') {
        b.disabled = true;
        el('#kiosk-steps-out').innerHTML = stepList();
        return;
      }
      if (act === 'again') {
        renderStart();
        stage.scrollIntoView({ behavior: SCROLL, block: 'center' });
        return;
      }
      // The other version, or the worked one for a run that has none. Either way
      // the ways on appear underneath it, now that there is nothing left to spoil.
      el('#kiosk-next').hidden = true;
      el('#kiosk-reveal').innerHTML = reveal();
      el('#kiosk-ways').hidden = false;
      el('#kiosk-reveal').scrollIntoView({ behavior: SCROLL, block: 'nearest' });
    }));
    el('#kiosk-open-report').addEventListener('click', (e) => {
      el('#kiosk-report-body').hidden = false;
      e.currentTarget.parentNode.hidden = true;
      el('#kiosk-report').scrollIntoView({ behavior: SCROLL, block: 'start' });
    });
    result.scrollIntoView({ behavior: SCROLL, block: 'start' });
  }

  renderStart();
  // The veil plays the order and nothing else: mid-task it would be a replay,
  // and sayOrder refuses once the clip is spent.
  veil.addEventListener('click', sayOrder);
})();
