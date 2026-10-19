# 나스닥 체크

QQQ(나스닥-100 추종 ETF)의 종가를 기준으로 역대 최고점 대비 하락률과 −10%·−20%·−30% 매수 단계를 보여주는 정적 페이지입니다. 시세는 평일마다 GitHub가 스스로 갱신합니다.

## 구성

| 경로 | 역할 |
|---|---|
| `site/index.html` | 화면. 같은 폴더의 `data.json`을 읽어 그립니다. |
| `site/data.json` | 저장된 종가. 매일 자동으로 갱신됩니다. |
| `scripts/update.py` | Alpha Vantage에서 새 종가를 받아 `data.json`에 추가합니다. |
| `.github/workflows/update.yml` | 평일 한국 시간 07:30에 위 스크립트를 실행하고 페이지를 배포합니다. |

## 설정 순서

1. GitHub에서 **공개(Public)** 저장소를 새로 만듭니다. 무료 계정에서는 공개 저장소만 GitHub Pages를 쓸 수 있습니다.
2. 이 폴더의 파일을 모두 저장소에 올립니다. `.github` 폴더는 점으로 시작해서 탐색기에서 숨겨질 수 있으니, 보이지 않으면 숨김 파일 표시를 켜세요. 웹에서 올릴 때는 **Add file → Create new file**에서 파일 이름에 `.github/workflows/update.yml`을 입력하고 내용을 붙여 넣으면 됩니다.
3. [Alpha Vantage](https://www.alphavantage.co/support/#api-key)에서 무료 API 키를 발급받습니다.
4. 저장소 **Settings → Secrets and variables → Actions → New repository secret**에서 이름을 `AV_API_KEY`로, 값을 발급받은 키로 저장합니다. 키는 코드에 쓰지 않습니다.
5. **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
6. **Actions** 탭에서 `시세 갱신 및 배포`를 열고 **Run workflow**를 눌러 한 번 실행합니다. 성공하면 Pages 주소가 표시됩니다. 이 주소가 공유할 링크입니다.

## 동작과 한도

- 무료 키는 하루 25회, 분당 5회까지입니다. 이 설정은 하루 1회만 호출합니다.
- 미국 휴장일에는 새 종가가 없어서 `updatedAt`만 바뀝니다.
- 실행이 실패하면(키 오류, 호출 한도 등) Actions 탭에 빨간 표시가 뜨고 GitHub가 이메일로 알려줍니다. 실패해도 이전 데이터는 그대로 남습니다.
- 페이지는 마지막 갱신이 4일 넘게 지나면 경고를 표시합니다.
- 역대 최고점은 2026년 5월 27일 이전은 주간 종가(`prior`), 이후는 일별 종가로 계산합니다. 오래된 고점은 며칠 차이가 날 수 있어 날짜 앞에 ≈를 붙입니다.
- 이 페이지는 투자 권유가 아닙니다. 매수 단계는 −10%, −20%, −30%라는 정해진 기준을 그대로 보여줍니다.

## 로컬에서 확인

`site/index.html`을 파일로 바로 열면 브라우저가 `data.json` 읽기를 막습니다. 폴더에서 `python3 -m http.server -d site`를 실행하고 `http://localhost:8000`으로 여세요.
