# -*- coding: utf-8 -*-
"""사이트 전수 검사 — STYLE.md 규칙 중 기계가 확인할 수 있는 것.

    python scripts/audit_site.py

정적 검사(HTML·CSS 읽기)는 항상 돌고, 브라우저 검사(실제 렌더된 서체·줄 길이)는
playwright가 있을 때만 돈다. 규칙 위반이 하나라도 있으면 종료 코드 1.

왜 브라우저가 필요한가: 서체가 어긋난 사고(논문 12쪽 섹션 제목 57개가 브라우저 기본
산세리프로 나옴)는 CSS만 읽어서는 안 잡힌다. 규칙은 h3에 붙어 있었고 마크업은 h2였다.
둘 다 문법상 멀쩡했고, 실제로 계산된 font-family를 봐야 드러났다.
"""
import os
import re
import sys
import io
import collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── STYLE.md 가 정한 것들 ──────────────────────────────────────────────
# §3-3 링크 라벨 닫힌 어휘. 새 표현을 여기 추가하기 전에 STYLE.md 부터 고친다.
LINK_LABELS = {
    'PDF ↗', 'Publisher ↗', 'Video ↗', 'Project page →',
    'Play it →', 'Watch it →', 'Open PDF ↗', 'All demos →', 'All news →', 'All publications →',
}
# §4-5 역할별 서체. 값은 CSS 변수가 가리키는 실제 첫 패밀리.
SERIF, SANS = 'Newsreader', 'Inter'
FONT_ROLES = {
    'h1': SERIF, 'h2': SERIF, 'h3': SERIF,
    'p.lead': SANS, '.card-index': SANS, '.tag': SANS,
    '.work-venue': SANS, '.paper-breadcrumb': SANS, 'footer': SANS,
}
MAX_CPL = 78   # §4-6 한 줄 글자 수 상한

fail = []
note = []


def bad(rule, detail):
    fail.append((rule, detail))


# ── 정적 검사 ─────────────────────────────────────────────────────────
pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # scripts/ 안의 .html 은 사이트의 쪽이 아니라 빌드 입력이다 —
    # ca_animation.html 은 헤드리스 브라우저가 녹화할 화면이라 사이트의
    # 서체·제목 규칙을 따르지 않으며, 따를 이유도 없다.
    dirnames[:] = [d for d in dirnames
                   if d not in ('.git', 'node_modules', '__pycache__', 'assets', 'scripts')]
    for fn in filenames:
        if fn.endswith('.html') and 'DESKTOP' not in fn:
            pages.append(os.path.join(dirpath, fn))
pages.sort()

# OneDrive 충돌 사본 — 한 번 공개 배포된 적이 있다
ghosts = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != '.git']
    ghosts += [os.path.relpath(os.path.join(dirpath, f), ROOT)
               for f in filenames if '-DESKTOP-' in f]
if ghosts:
    bad('OneDrive 충돌 사본', '%d개 남아 있음 (.gitignore 되지만 지우는 게 낫다): %s%s'
        % (len(ghosts), ', '.join(ghosts[:3]), ' …' if len(ghosts) > 3 else ''))

TAG = re.compile(r'<[^>]+>')

# 캐시 토큰이 자산의 실제 내용과 맞는가 (§6).
# build_site.py 의 asset_version() 과 같은 계산이어야 한다 — 줄끝을 LF 로 정규화한 뒤
# sha1. 정규화를 빼면 Windows 체크아웃(CRLF)에서 라이브(LF)와 다른 값이 나와,
# 내용이 바뀐 적 없는데도 매번 어긋난 것처럼 보인다.
import hashlib
_hash_cache = {}


def asset_hash(rel_asset):
    if rel_asset not in _hash_cache:
        p = os.path.join(ROOT, rel_asset.lstrip('/'))
        _hash_cache[rel_asset] = (
            hashlib.sha1(open(p, 'rb').read().replace(b'\r\n', b'\n')).hexdigest()[:8]
            if os.path.exists(p) else None)
    return _hash_cache[rel_asset]


for path in pages:
    rel = os.path.relpath(path, ROOT).replace('\\', '/')
    html = open(path, encoding='utf-8').read()
    body = html.split('<main', 1)[-1]

    # §6 캐시 토큰이 자산의 실제 sha1 과 맞는가
    for asset, token in re.findall(r'(/assets/[\w./-]+)\?v=(\w+)', html):
        real = asset_hash(asset)
        if real is None:
            bad('없는 자산', '%s → %s' % (rel, asset))
        elif real != token:
            bad('캐시 토큰', '%s — %s 가 ?v=%s 인데 실제는 %s (build_site.py 를 돌린다)'
                % (rel, asset, token, real))

    # §3-1 h1 은 페이지당 정확히 하나
    n_h1 = len(re.findall(r'<h1[\s>]', body))
    if n_h1 != 1:
        bad('h1 개수', '%s — %d개 (정확히 하나여야 한다)' % (rel, n_h1))

    # §3-3 링크 라벨 닫힌 어휘
    for zone in re.findall(r'<div class="(?:paper-links|news-links)">(.*?)</div>', body, re.S):
        for label in re.findall(r'<a[^>]*>(.*?)</a>', zone, re.S):
            text = TAG.sub('', label).replace('&rarr;', '→').replace('&nearr;', '↗')
            text = ' '.join(text.split())
            if text not in LINK_LABELS and not re.match(r'^The \w', text):
                bad('링크 어휘', '%s — “%s” 는 §3-3 목록에 없다' % (rel, text))
    for label in re.findall(r'<span class="demo-teaser-cta">(.*?)</span>', body, re.S):
        text = ' '.join(TAG.sub('', label).replace('&rarr;', '→').split())
        if text not in LINK_LABELS:
            bad('링크 어휘', '%s — 데모 카드 “%s”' % (rel, text))

    # 화살표 (§3-3): ↗ 는 새 탭, → 는 이 탭. 도메인이 아니라 탭이 기준이다 —
    # 사이트 안의 PDF도 새 탭으로 열리므로 ↗ 가 맞다.
    for tag, inner in re.findall(r'(<a[^>]*>)(.*?)</a>', body, re.S):
        txt = TAG.sub('', inner).replace('&rarr;', '→').replace('&nearr;', '↗')
        href = (re.search(r'href="([^"]*)"', tag) or [None, '?'])[1]
        new_tab = 'target="_blank"' in tag
        if '↗' in txt and not new_tab:
            bad('화살표', '%s — ↗ 인데 새 탭이 아니다 (%s)' % (rel, href))
        if '→' in txt and new_tab:
            bad('화살표', '%s — → 인데 새 탭으로 열린다 (%s)' % (rel, href))

    # 곧은 아포스트로피 — 산문에서는 굽은 것만 쓴다
    prose = re.sub(r'<(script|style|code|pre)[\s>].*?</\1>', '', body, flags=re.S)
    for m in re.finditer(r"\w'(?:s|t|re|ve|ll|d|m)\b", TAG.sub(' ', prose)):
        bad('아포스트로피', '%s — “%s” 는 ’ 를 써야 한다' % (rel, m.group(0)))

    # alt 없는 img
    for m in re.finditer(r'<img(?![^>]*\balt=)[^>]*>', body):
        bad('alt', '%s — %s' % (rel, m.group(0)[:70]))

print('정적 검사: %d쪽' % len(pages))

# ── 브라우저 검사 ─────────────────────────────────────────────────────
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    note.append('playwright 없음 → 서체·줄 길이 검사 건너뜀 (pip install playwright)')
    sync_playwright = None

if sync_playwright:
    import threading
    import functools
    import http.server
    import socketserver

    PORT = 8817

    class Silent(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Silent, directory=ROOT)

    # 스레드가 하나면 홈의 자동재생 영상이 연결을 붙잡은 동안 나머지 요청이
    # 줄을 서고, networkidle 이 영영 오지 않는다. 영상이 길어질수록 잘 걸린다.
    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, *a):
            pass

    srv = Quiet(('127.0.0.1', PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    JS = """(roles) => {
      const out = {fonts: [], measure: [], headings: []};
      const first = el => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '');
      for (const sel of Object.keys(roles))
        document.querySelectorAll(sel).forEach(el => {
          if (el.textContent.trim())
            out.fonts.push([sel, first(el), el.textContent.trim().slice(0, 42)]);
        });
      // 한 줄 글자 수
      const ctx = document.createElement('canvas').getContext('2d');
      const alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ';
      for (const sel of ['p.lead', '.paper-section > p', '.takeaway-list li',
                         '.publication-card p', '.demo-teaser p']) {
        const el = document.querySelector(sel);
        if (!el) continue;
        const cs = getComputedStyle(el);
        ctx.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
        const w = el.getBoundingClientRect().width;
        out.measure.push([sel, Math.round(w),
                          Math.round(w / (ctx.measureText(alpha).width / alpha.length))]);
      }
      document.querySelectorAll('main h1, main h2, main h3, main h4')
        .forEach(el => out.headings.push(+el.tagName[1]));
      return out;
    }"""

    seen_font = collections.defaultdict(collections.Counter)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        for path in pages:
            url = '/' + os.path.relpath(path, ROOT).replace('\\', '/')
            url = url.replace('/index.html', '/')
            # networkidle 은 못 쓴다: 홈이 자동재생하는 영상이 재생 내내 연결을
            # 붙잡고 있어서, 영상이 30초보다 길면 절대 오지 않는다. 여기서 재는
            # 것은 서체와 배치이니 기다려야 할 것은 load 와 웹폰트뿐이다.
            r = pg.goto('http://127.0.0.1:%d%s' % (PORT, url), wait_until='load')
            if r.status != 200:
                bad('페이지', '%s → %d' % (url, r.status))
                continue
            pg.wait_for_function("document.fonts.status === 'loaded'")
            pg.wait_for_timeout(200)
            got = pg.evaluate(JS, FONT_ROLES)

            for sel, fam, txt in got['fonts']:
                seen_font[sel][fam] += 1
                if fam != FONT_ROLES[sel]:
                    bad('서체', '%s — %s 가 %s (규칙은 %s) “%s”'
                        % (url, sel, fam, FONT_ROLES[sel], txt))
            for sel, px, cpl in got['measure']:
                if cpl > MAX_CPL:
                    bad('줄 길이', '%s — %s %dpx = 약 %d자/줄 (상한 %d)'
                        % (url, sel, px, cpl, MAX_CPL))
            lv = got['headings']
            for i in range(1, len(lv)):
                if lv[i] - lv[i - 1] > 1:
                    bad('제목 단계', '%s — h%d 다음에 h%d' % (url, lv[i - 1], lv[i]))
                    break

            for href in pg.eval_on_selector_all(
                    'a[href^="/"]', 'e => e.map(x => x.getAttribute("href").split("#")[0])'):
                if href and pg.request.get('http://127.0.0.1:%d%s' % (PORT, href)).status != 200:
                    bad('깨진 링크', '%s → %s' % (url, href))
        b.close()
    srv.shutdown()

    print('브라우저 검사: 서체 %d역할 · 줄 길이 · 제목 단계 · 내부 링크'
          % len(seen_font))

# ── 결과 ─────────────────────────────────────────────────────────────
print()
for n in note:
    print('  참고: ' + n)
if not fail:
    print('통과 — 위반 없음')
    sys.exit(0)

grouped = collections.defaultdict(list)
for rule, detail in fail:
    grouped[rule].append(detail)
print('위반 %d건' % len(fail))
for rule, details in grouped.items():
    print('\n[%s] %d건' % (rule, len(details)))
    for d in details[:8]:
        print('   ' + d)
    if len(details) > 8:
        print('   … 외 %d건' % (len(details) - 8))
sys.exit(1)
