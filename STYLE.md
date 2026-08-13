# 사이트 작성 규칙

이 사이트를 고칠 때 지키는 규칙. 새 세션·새 사람이 이어받을 때 여기부터 읽는다.
**원칙: 같은 것은 한 곳에만 쓰고, 나머지는 거기서 생성한다.**

---

## 1. 무엇이 생성물이고 무엇이 손으로 쓰는 파일인가

| 파일 | 소유 | 고칠 때 |
|---|---|---|
| 모든 페이지의 `<head>`, 사이드바 | `scripts/build_site.py` | 스크립트의 `PAGES`·`NAV`를 고치고 다시 실행 |
| `sitemap.xml`, `robots.txt` | `scripts/build_site.py` | 직접 고치지 않는다 |
| 홈 푸터의 "Last updated" 달 (`<span data-last-updated>`) | `scripts/build_site.py` | 손대지 않는다 — 빌드가 그 달로 찍고, 달이 바뀌면 `--check`가 잡아 커밋 전 갱신을 강제한다 |
| `/cv/` 본문 (`cv:start`~`cv:end` 사이) | `scripts/build_cv_html.py` | 아래 순서대로 다시 실행 |
| `assets/cv/Bogyeom_Park_CV.pdf` | `scripts/build_cv.py` | `scripts/cv_data.py`를 고친다 |
| `assets/cv/pages/page-N.webp` | `scripts/build_assets.py` | PDF를 다시 만들고 실행 |
| `assets/news/thumbs/*`, `favicon.ico`, `apple-touch-icon.png`, `og-card.jpg`, `bogyeom-park-224.webp` | `scripts/build_assets.py` | 원본 이미지를 바꾸고 다시 실행 |
| 각 페이지 `<main>` 안의 본문 | 손으로 작성 | 직접 편집 |

**CV 내용은 `scripts/cv_data.py` 한 곳에만 있다.** PDF와 웹페이지가 같은 모듈을 읽으므로,
둘 중 하나만 고치면 다음 빌드에서 덮어써진다.

## 2. 빌드·검사 명령

```bash
python scripts/build_site.py          # head·사이드바·sitemap 동기화
python scripts/build_cv_html.py       # cv_data -> /cv/ 본문
python scripts/build_assets.py        # 썸네일·아이콘·og 카드 재생성

# PDF는 reportlab이 필요하고, 이 PC에서는 base가 아니라 agent 환경에만 있다
"$HOME/anaconda3/envs/agent/python.exe" scripts/build_cv.py
```

검사만 하고 파일은 안 건드리는 모드 (커밋 전에 돌린다):

```bash
python scripts/build_site.py --check
python scripts/build_cv_html.py --check
```

`build_cv_html.py --check`는 **publications 페이지가 CV의 섹션 이름을 안 쓰면 실패**한다.
그 페이지는 손으로 쓰는 파일이라 데이터에서 생성할 수 없어서 검사로 묶어 둔 것이다.

---

## 3. 표기 규칙

### 3-1. 페이지 제목 = nav 이름

nav에서 `News`를 눌렀는데 제목이 "Research updates & milestones"면 방문자가 자기 위치를 의심한다.
**`<h2>`는 nav 항목과 같은 단어를 쓰고**, 설명 문구는 그 아래 `.lead` 한 줄로 내린다.
섹션 페이지에는 `.eyebrow`를 쓰지 않는다 (nav 이름과 같은 말이 두 번 나온다).

홈은 예외 — `.eyebrow`가 분야를 표시하고, `<h2>`는 연구 주장을 담는다.

### 3-2. 논문 섹션 이름

`scripts/cv_data.py`의 `SECTION_TITLES`가 유일한 원천이다. 현재:

| 섹션 | 내용 |
|---|---|
| `Journal Articles` | 심사 학술지 논문 |
| `International Conference Papers` | 국제 학회 (CHI EA, ITC-CSCC, ICEIC …) |
| `Domestic Conference Papers` | 국내 학회 (HCI Korea) |

세 이름은 **같은 문법 형태**(범위 + Papers/Articles)를 유지한다.
국제/국내는 합치지 않는다 — 합쳐서 연도순으로 두면 국내 최신 논문이 CHI·JMIR 위로 올라가고,
해외 심사자에게는 한국어 지역 학회가 CHI 옆에 붙은 것으로 보인다.

이 이름은 `/publications/`와 `/cv/`와 PDF **세 곳에 같이** 나타난다.

### 3-3. 링크 라벨 (닫힌 어휘 — 새 표현을 만들지 않는다)

**본문 링크 줄** (`.paper-links`, `.news-links`) — *목적지*를 이름으로 쓴다:

| 라벨 | 가리키는 곳 | 쓰는 곳 |
|---|---|---|
| `PDF ↗` | 이 사이트에 올린 논문 파일 | 논문·데모 |
| `Publisher ↗` | 공식 게재 기록 (ACM, IEEE Xplore, DBpia, 학회 proceedings) | 논문 |
| `Video ↗` | 발표·데모 영상 | 논문·데모 |
| `Project page →` | 이 사이트 안의 상세 페이지 | **Demos 페이지에서만** |

**순서도 이 표의 순서**를 따른다. 없는 항목은 건너뛴다.

**같은 곳으로 가는 링크를 두 번 두지 않는다.** 논문 카드는 썸네일과 제목이 이미
상세 페이지(없으면 PDF나 출판사 기록)로 가는 링크다. 그래서 논문 카드에는
`Project page →`를 두지 않는다 — 같은 목적지를 세 번 적는 셈이었다.
그 대신 카드 제목은 hover에서 밑줄이 생겨 링크임을 드러낸다.
Demos·News 페이지는 제목이 링크가 아니므로 거기서는 `Project page →`가 유일한 통로다.

**어휘를 늘리지 않는다.** 한두 장에만 붙는 링크는 규칙이 아니라 예외이고, 예외가
쌓이면 방문자는 라벨을 읽는 대신 매번 해석해야 한다. 실제로 이렇게 정리했다:

- `SeoulTech record`(교내 PURE 서지 레코드) — 출판사 기록이 이미 있어 같은 논문을 두 번
  가리켰다. **삭제.**
- `News ↗`가 논문 카드 12장 중 2장에만 있었다. 수상은 그 카드의 배지가 이미 말하고,
  사건의 서술은 News 페이지가 한다. **논문 카드에서는 삭제**, News 페이지에는 유지.
- `Related paper →`(국내판 ↔ 국제판)가 12장 중 1장. 두 논문 모두 같은 페이지에 있다.
  **삭제.**

결과: 논문 카드는 위 네 라벨의 부분집합만 갖고, 순서는 항상 같다.

**버튼 줄** (`.paper-actions`, `.button-row`) — 주 동작 하나만 둔다:

| 라벨 | 동작 |
|---|---|
| `Open PDF ↗` | 브라우저 PDF 뷰어로 열기 |

`Download PDF`를 따로 두지 않는다. 같은 파일을 가리키는 버튼이 둘이었고,
**뷰어로 열면 검색도 되고 거기서 저장도 되므로 Open이 Download를 포함한다.**
반대는 성립하지 않는다.

화살표: **`↗` = 외부 사이트 / 새 탭**, **`→` = 이 사이트 안**. 예외 없다.

### 3-3-1. News 항목 쓰는 법

**한 항목 = 한 문단.** 원래는 두 문단(①어디서 발표했다 ②연구 내용)이었는데,
그러면 제일 강한 사실이 둘째 문단 끝에 묻힌다 — 94.4% 정확도, 1천만원, 수상이
전부 거기 있었다.

1. **첫 문장에 이룬 것을 쓴다.** 장소·프로그램 이름 같은 정황은 뒤로 보내거나 뺀다.
2. **구체적 수치나 선별성을 하나 넣는다** (94.4% 정확도 · KRW 10,000,000 · 6명 중 선발 ·
   Best Paper). 없으면 넣지 않는다 — 지어내지 않는다.
3. **제목·날짜·분류 칩·사진이 이미 말하는 것을 본문에서 반복하지 않는다.**
4. 겸양으로 성과를 깎지 않는다. 공저자면 공저자라고 쓰면 충분하고,
   "이 항목은 논문 단위 수상을 기록한 것" 같은 해명은 붙이지 않는다.
5. **본문에 링크를 두지 않는다.** 항목은 제목·날짜·분류·사진·한 문단으로 자립해야 한다.
   논문 페이지로도, 연구실 소식으로도 연결하지 않는다 — Publications는 nav 한 번 거리에
   있고, 소식 링크는 항목이 이미 말한 것을 밖에서 한 번 더 확인시키는 것뿐이었다.
   사진을 누르면 원본이 열리는 것이 유일한 링크다.

**분류 칩 어휘 (닫힌 목록 — 전부 한 단어):**

| 칩 | 쓰는 경우 |
|---|---|
| `Talk` | 구두 발표 |
| `Poster` | 포스터·LBW 발표 |
| `Publication` | 논문 게재 소식 |
| `Award` | 수상 (`class="award"`, accent 채움) |
| `Teaching` | 강의·멘토링 |
| `Service` | 학술 봉사 (SV 등) |

칩은 **한 단어만** 쓴다 — 두 단어 칩("Oral Presentation"·"Teaching & Mentoring")은
115px 날짜 칼럼을 넘어 본문과 겹쳤다 (2026-08 실제 사고). 공식 명칭은 본문·venue·CV에
그대로 쓰고, 칩은 스캔용 분류만 담는다. CSS도 칩이 칼럼을 넘으면 겹치는 대신
줄바꿈되도록 `max-width: 100%`로 잠가 두었다.

### 3-3-1-A. 홈의 Selected Work 고르는 기준

**헤드라인을 증명하는 세 편**을 고른다. 홈이 "이렇게 주장한다 → 이게 근거다"로 읽혀야 한다.
venue가 센 순서로 고르지 않는다 — 그러면 홈이 실적 진열대가 되고, 주장과 무관한 논문이
첫 화면에 올라온다.

현재 헤드라인은 *"agents that make people think &mdash; and measuring whether they do"* 이므로:

| 자리 | 논문 | 왜 |
|---|---|---|
| 1 | Multi-Agent Debate Chatbot (CHI EA 2025) | 생각하게 만들고, 그것을 평가함 &mdash; 헤드라인 양쪽 |
| 2 | VR/MRI Biomarkers (JMIR 2024) | 행동에서 인지를 **측정**하는 쪽 |
| 3 | Agentic Career Counseling (HCI Korea 2026) | 지금 주도하는 방향 |

세 편 모두 **1저자 또는 공동 1저자**여야 한다. 홈 첫 화면의 대표작에 남이 주도한 연구를
올리지 않는다 (공저 연구는 Publications에 그대로 실린다).
헤드라인을 바꾸면 이 세 편도 다시 고른다.

### 3-3-1-B. 홈의 Demo 카드

Selected Work 아래에 **플레이 가능한 데모 하나**를 카드로 둔다 (`.demo-teaser`).
헤드라인이 "measuring whether they do"를 주장하므로, 방문자가 직접 만질 수 있는
측정이 홈에 있어야 주장이 선다. 규칙:

- 카드는 **하나만.** 데모가 늘면 카드를 늘리지 말고 대표 하나를 고른다 — 나머지는
  섹션 헤딩의 `All demos →`가 감당한다.
- **카드 전체가 링크**다 (`.work`와 같은 패턴). 안에 별도 `<a>`를 두지 않고,
  `Try the demo →`는 시각 신호용 `<span>`이다.
- 카피는 `/demos/` 카드의 요약을 **echo해도 되지만 대체하면 안 된다** — 상세 설명과
  논문 연결은 /demos/와 데모 페이지의 몫이다.

### 3-3-2. 논문 상세 페이지의 Key Findings

**타일에는 결과만 넣는다.** 참가자 수·조건 수·이론 구성요소는 결과가 아니라 설계이고,
그건 Method에 이미 있다. 한때 두 페이지의 타일이 전부 설계 정보라서
(`40 University students` · `2 conditions` · `3 outcomes`), 페이지에서 제일 크게 보이는
자리가 표본 크기를 알려주고 있었다.

- **비교 대상을 같이 쓴다.** `0.78`만 있으면 좋은 건지 알 수 없다 —
  "단일 에이전트는 0.09"가 붙어야 의미가 선다.
- 유의확률은 APA 표기로: `p < .001`, `p = .86` (앞의 0 없음).
- **유의하지 않은 결과도 적는다.** 감추면 나머지 수치의 신뢰도까지 깎인다.
- 숫자는 논문 결과 절에서 그대로 가져온다. 사이트에서 계산하거나 반올림해 만들지 않는다.

### 3-4. 저자 표기

- 본인 이름은 `<strong>Bogyeom Park</strong>`로 굵게 — 저자 목록에서 자기 위치가 보여야 한다.
- 공동 제1저자는 `<sup>†</sup>`를 이름 뒤에 붙이고, 목록 끝에
  `<span class="author-note">† Co-first authors (equal contribution)</span>`를 단다.
- 개명 전 논문은 옛 이름을 쓰고 `<span class="former-name-note">(now Bogyeom Park)</span>`를 붙인다.
  옛 이름을 지우면 그 논문의 인용이 끊긴다.
- 수상은 그 논문 카드의 `.publication-badges`에 붙인다. 페이지 상단에 몰아두지 않는다 —
  어느 논문 얘긴지 사라지고, 정작 논문 목록을 아래로 밀어낸다.

### 3-5. 학회 명칭

`Extended Abstracts`는 CHI의 **짧은 트랙 논문집 이름**이지 논문 종류가 아니다.
venue 표기에는 공식 명칭 그대로 쓰고(`CHI EA '25: Extended Abstracts of the …`),
**섹션 제목으로는 쓰지 않는다** (초록만 낸 것으로 오해된다).

### 3-6. 지표 표기

- JMIR: `JCR Q1; Top 3%` — percentile 표현과 섞지 않는다 (Top 3%와 96th percentile은 다른 수치다).
- CHI LBW 채택률은 그 해 수치를 쓰고 분모를 같이 적는다: `32.7% acceptance; 619/1,888`.
- 출처 링크를 걸 수 있는 수치만 싣는다.

---

## 4. 디자인 규칙

### 4-1. 굵기와 색

로드된 폰트는 Inter(본문)·Newsreader(제목). **굵기는 네 단계만** 쓴다:

| 굵기 | 용도 |
|---|---|
| 400 | 본문 |
| 500 | 보조 정보 (venue, 날짜) |
| 600 | 제목, 항목 제목, 현재 nav |
| 700 | 아주 드문 강조 |

`650`·`750`·`850` 같은 값을 쓰지 않는다. 폰트가 안 실릴 때 전부 700으로 뭉개져
"강조가 어딘지 모르겠는" 상태가 됐던 원인이다.

**글자 색은 세 가지뿐**: `--ink`(제목) · `--body`(본문) · `--muted`(보조).
더 강조하고 싶으면 새 회색을 만들지 말고 굵기나 크기를 쓴다.

### 4-2. 색은 변수로만 · 라이트 전용

**이 사이트는 밝은 테마 하나로만 간다.** `color-scheme: light`를 선언해 두었으므로
브라우저가 임의로 어둡게 바꾸지 않는다. 다크모드 블록은 없앴다.

새 색을 CSS에 직접 적지 않는다 — `:root`에 변수를 만들어 쓴다. 강조색은 변수 밖
네 곳(링크 밑줄 tint · 포커스 링 · `theme-color` · `build_assets.py`의 favicon/og 팔레트)에도
나타나므로, 강조색을 바꿀 때는 그 넷을 같이 본다.

### 4-2-A. 데모가 쓰는 클래스는 지우지 말 것

`.card`, `.card-grid`, `.research-note`, `.metric*`는 **`assets/demos/kiosk.js`가 실행 중에 만든다.**
정적 HTML을 훑는 도구에는 "미사용"으로 잡히지만 지우면 데모가 무너진다 (실제로 한 번 지워졌다).
CSS 주석에도 표시해 두었다.

### 4-3. 반응형

고정 브레이크포인트로 열 수를 정하지 않는다. `repeat(auto-fit, minmax(Npx, 1fr))`로
**내용 폭에 따라 접히게** 한다. 3열 고정 때문에 900~1100px에서 카드가 175px로 짜부라진 적이 있다.

### 4-4. 이미지

- **원본은 지우지 않는다.** news 사진은 클릭하면 열리는 대상이고, 논문 그림은 인쇄 품질 원본이다.
- 화면에 쓰는 것은 `build_assets.py`가 만든 webp: news 사진 720px, 논문 그림 1400px.
  논문 그림은 안에 글자가 있어서 폭과 품질을 더 준다.
- HTML은 항상 webp를 가리킨다. 새 그림을 넣으면 `build_assets.py`를 돌리고 참조를 `.webp`로 쓴다.
- 휴대폰 사진은 EXIF 회전 정보를 갖고 있다. 재인코딩하면 그 정보가 사라지므로
  `ImageOps.exif_transpose()`로 픽셀에 회전을 구워 넣는다.

---

## 5. 새 논문을 추가할 때

1. `assets/publications/<slug>/`에 `paper.pdf`와 대표 그림을 넣는다.
2. `scripts/cv_data.py`의 해당 목록에 항목을 추가한다 (제목·저자·venue·url).
3. `/publications/index.html`에 카드를 추가한다 — 링크 줄은 §3-3 순서와 어휘를 따른다.
4. **상세 페이지를 만든다** (`publications/<slug>/index.html`) — 저널이든 국제학회든 국내학회든
   예외 없이. 12편 전부 있고, 없으면 목록에서 제목이 갈 곳이 없어진다. 구조는 기존 페이지와 같게:
   breadcrumb / 제목 / 저자 / venue / 버튼 / 목차 / 그림 / Overview / Method / Key Findings /
   Contribution / Citation. 그리고 `scripts/build_site.py`의 `PAGES`에 등록한다
   (`citation` 항목까지 채우면 Google Scholar가 색인한다. DOI가 없으면 생략해도 된다).
   **논문 전문을 여기 올리지 않는 경우엔 Key Findings를 비워 둔다** — 수치를 추측해 넣지 않는다.
5. 빌드:
   ```bash
   python scripts/build_cv_html.py
   "$HOME/anaconda3/envs/agent/python.exe" scripts/build_cv.py
   python scripts/build_site.py
   ```
6. `--check` 두 개를 돌려 통과하는지 확인하고 커밋한다.

## 6. 커밋

푸시하면 곧바로 공개된다(GitHub Pages, `main` 브랜치). 커밋 전에 `--check`를 돌린다.
새 파일이 페이지에서 참조되는데 untracked로 남으면 라이브에서 깨지므로 `git add -A`를 쓴다.

## 7. 방문자 집계 (GoatCounter)

- 대시보드: **https://bogyeompark.goatcounter.com** (무료·쿠키 없음 → 동의 배너 불필요).
- 스니펫은 `scripts/build_site.py`의 `build_head()` **한 곳**에만 있고 빌드가 전 페이지에
  넣는다. 페이지에 직접 붙이지 않는다.
- `count.js`는 localhost를 스스로 건너뛰므로 로컬 확인은 집계를 오염시키지 않는다
  (로컬 콘솔에 "not counting" 경고가 보이는 것이 정상).
- **커스텀 이벤트는 kiosk.js의 `tally()` 둘뿐**: `kiosk-run-started`(시작 버튼) ·
  `kiosk-run-finished`(리포트 도달). 시작 대비 완주율이 대시보드에서 나온다.
- **철칙: 이벤트는 사실만 보내고 측정값(시간·오답·선택)은 절대 보내지 않는다.**
  (리포트에 있던 "counts runs, not results" 주석 문단은 호스트 판단으로 삭제됨,
  2026-08-13 — 페이지가 프라이버시를 주장하지 않을 뿐, 이 철칙 자체는 그대로다.
  이벤트를 늘리려면 여기서 다시 따져본다.)
