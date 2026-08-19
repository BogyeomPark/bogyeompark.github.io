document.querySelectorAll('[data-media-tabs]').forEach((tabs) => {
  const buttons = [...tabs.querySelectorAll('[role="tab"]')];
  const panels = [...tabs.querySelectorAll('[role="tabpanel"]')];

  const activate = (button) => {
    buttons.forEach((item) => {
      const selected = item === button;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach((panel) => {
      panel.hidden = panel.id !== button.getAttribute('aria-controls');
    });
  };

  buttons.forEach((button, index) => {
    button.addEventListener('click', () => activate(button));
    button.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === 'ArrowLeft') next = (index - 1 + buttons.length) % buttons.length;
      if (event.key === 'ArrowRight') next = (index + 1) % buttons.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      activate(buttons[next]);
      buttons[next].focus();
    });
  });
});

// Swipe carousel (Home's "Watch it"). The scroll position is the single source
// of truth: arrows scroll the track, and whatever it lands on drives the caption
// and which video is playing. Only the visible video runs - two at once would be
// two soundtracks and twice the traffic.
//
// Sound: no browser will autoplay audio before the visitor has interacted with
// the page, so the first video starts muted and everything unmutes on the first
// real gesture. Trying to start unmuted does not produce a loud page, it
// produces a stopped one.
//
// The videos do not loop. Each hands off to the next when it ends, and the last
// wraps to the first, so the section plays through on its own.
document.querySelectorAll('[data-media-carousel]').forEach((root) => {
  const track = root.querySelector('.carousel-track');
  if (!track || track.children.length < 2) return;
  const slides = [...track.children];
  const videos = slides.map((slide) => slide.querySelector('video'));
  const captions = [...root.querySelectorAll('[data-caption]')];
  const dots = root.querySelector('[data-carousel-dots]');
  if (dots) slides.forEach(() => dots.appendChild(document.createElement('span')));
  const arrows = [...root.querySelectorAll('[data-step]')];
  let current = 0;
  let wantsSound = false;

  const settle = (index) => {
    current = index;
    videos.forEach((video, n) => {
      if (!video) return;
      if (n === index) {
        video.muted = !wantsSound;
        video.play().catch(() => {});
      } else {
        video.pause();
        video.currentTime = 0;
      }
    });
    captions.forEach((caption, n) => { caption.hidden = n !== index; });
    if (dots) [...dots.children].forEach((dot, n) => dot.toggleAttribute('data-active', n === index));
  };

  // Wrap around: an arrow that disappears at the end reads as a broken control,
  // and with two slides either arrow is always a sensible move.
  const go = (index) => {
    const wrapped = (index + slides.length) % slides.length;
    track.scrollTo({ left: slides[wrapped].offsetLeft - slides[0].offsetLeft, behavior: 'smooth' });
  };

  arrows.forEach((arrow) => arrow.addEventListener('click', () => go(current + Number(arrow.dataset.step))));

  track.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    go(current + (event.key === 'ArrowRight' ? 1 : -1));
  });

  videos.forEach((video) => {
    if (!video) return;
    video.addEventListener('ended', () => go(current + 1));
    // Reaching for the volume control is the clearest possible statement of
    // intent, so honour it for the rest of the section too.
    video.addEventListener('volumechange', () => { if (!video.muted) wantsSound = true; });
  });

  const unmute = () => {
    wantsSound = true;
    const video = videos[current];
    if (video) { video.muted = false; video.play().catch(() => {}); }
  };
  ['pointerdown', 'keydown'].forEach((type) =>
    document.addEventListener(type, unmute, { once: true, passive: true }));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) settle(slides.indexOf(entry.target));
    });
  }, { root: track, threshold: 0.6 });
  slides.forEach((slide) => observer.observe(slide));

  settle(0);
});
