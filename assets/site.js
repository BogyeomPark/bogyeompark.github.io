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
// of truth: the arrows scroll the track, and whatever the track lands on drives
// the arrow states, the caption, and which video is playing. Two videos both
// autoplaying would be two soundtracks and twice the traffic, so only the
// visible one runs.
document.querySelectorAll('[data-media-carousel]').forEach((root) => {
  const track = root.querySelector('.carousel-track');
  if (!track || track.children.length < 2) return;
  const slides = [...track.children];
  const captions = [...root.querySelectorAll('[data-caption]')];
  const arrows = [...root.querySelectorAll('[data-step]')];
  let current = 0;

  const settle = (index) => {
    current = index;
    slides.forEach((slide, n) => {
      const video = slide.querySelector('video');
      if (!video) return;
      if (n === index) video.play().catch(() => {});
      else video.pause();
    });
    captions.forEach((caption, n) => { caption.hidden = n !== index; });
    arrows.forEach((arrow) => {
      const next = index + Number(arrow.dataset.step);
      arrow.disabled = next < 0 || next > slides.length - 1;
    });
  };

  const go = (index) => {
    const clamped = Math.min(slides.length - 1, Math.max(0, index));
    track.scrollTo({ left: slides[clamped].offsetLeft - slides[0].offsetLeft, behavior: 'smooth' });
  };

  arrows.forEach((arrow) => arrow.addEventListener('click', () => go(current + Number(arrow.dataset.step))));

  track.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    go(current + (event.key === 'ArrowRight' ? 1 : -1));
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) settle(slides.indexOf(entry.target));
    });
  }, { root: track, threshold: 0.6 });
  slides.forEach((slide) => observer.observe(slide));

  settle(0);
});
