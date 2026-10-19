# 가상환경 및 라이브러리 설치

Python 3.11 이상 기준입니다. 프로젝트 폴더에서 실행합니다.

## 가상환경 생성·활성화 (Mac)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 라이브러리 설치

```bash
python -m pip install -r requirements.txt
```

- pytest: 테스트 실행
- Appium-Python-Client: 기존 Appium 서버를 통한 Android 앱 제어
- selenium: 요소 탐색 및 명시적 대기

## 실행 결과 생성 (Windows / Mac 공통)

새 Mac에서는 프로젝트 루트에서 `.venv/bin/python -m pip install -r requirements.txt`를 실행합니다.
`vendor/`의 수집기 0.4.7 wheel과 Allure 플러그인도 설치됩니다. 이미 설치된 환경의 버전을 확인한 후 적용하세요.
이번 Windows 환경의 기존 수집기 0.4.8 설치는 유지했으며, 새 Mac 재현용 wheel은 분석기 소스와 같은 0.4.7입니다.

휴대폰·Appium 서버·앱 메인 준비 후 기존 테스트를 실행합니다. 아래 명령은 실제 단말 테스트를 시작합니다.

Windows:
```powershell
.\.venv\Scripts\python.exe scripts/run_reports.py tests/test_guest.py
```
Mac:
```bash
.venv/bin/python scripts/run_reports.py tests/test_guest.py
```

매 실행은 새로운 `test-artifacts/날짜-고유ID/`에 저장합니다.

- `allure-results/`: Allure JSON과 setup/call 시점 화면 PNG·XML
- `allure-results.zip`: 분석기의 Allure 결과 ZIP 입력용
- `qa-results/*.zip`: 분석기의 QA 수집 ZIP 입력용
- `observation.log`: START/END와 UTC 시각·순번 기록
- `pytest.log`, `run-summary.json`: 실행 로그·종료 코드·결과 경로

CSV를 함께 보관하려면 `--tc-csv quickmenu_strong.csv`처럼 실제 실행 TC와 맞는 CSV를 지정합니다.
`python -m pytest ...`를 직접 실행해도 `allure-results/`와 `qa-results/`에 결과를 남깁니다.
직접 실행은 기존 Allure 결과에 누적되므로 실행별 자료 분리는 위 스크립트를 권장합니다.
기존 결과를 삭제하는 `--clean-alluredir`는 사용하지 않습니다.

Allure PNG·XML 첨부는 기존 driver/home_screen fixture를 읽으며 새 Appium 세션이나 클릭을 생성하지 않습니다.
추가 화면 조회 시간은 발생합니다. 첨부 실패는 진단으로 남기며 원래 테스트 판정을 바꾸지 않습니다.
fixture 준비 전에 실패하면 연결된 드라이버가 없어 화면 첨부가 없을 수 있습니다.
설치된 플러그인이 없다면 먼저 requirements 설치가 필요합니다. 결과에는 앱 화면·XML·테스트 소스가 포함될 수 있으므로 제공 범위를 확인하세요.

### HTML 보고서 보기

Python 플러그인은 Allure 결과 데이터를 만듭니다. HTML 보고서는 별도 Allure CLI 설치 후 생성합니다.
```bash
allure generate test-artifacts/실행ID/allure-results --output test-artifacts/실행ID/allure-report
allure open test-artifacts/실행ID/allure-report
```
완성된 HTML 폴더가 아니라 `allure-results.zip`을 분석기에 넣으세요.

### 고객 테스트 화면 관찰 연결

실제 테스트 시작 전에 로그만 준비합니다. 이 명령은 pytest·휴대폰을 실행하지 않습니다.
```bash
python scripts/run_reports.py --prepare-log --observation-log test-artifacts/live-observation.log
```
관찰 웹에서 이 로그의 절대 경로와 CSV를 지정합니다.
로그 형식은 시작 `{time} seq={seq} START {test}`, 종료 `{time} seq={seq} END {test} {status}`입니다.
로그 이름은 pytest node ID 전체(예: `tests/test_guest.py::test_t_day_a[TC_GUEST_DAY_A]`)와 연결합니다.
관찰을 시작한 후 별도 터미널에서 실행합니다.
```bash
python scripts/run_reports.py --observation-log test-artifacts/live-observation.log tests/test_guest.py
```
로그는 기존 줄을 보존하며 추가합니다. 매 테스트 실행마다 새 관찰 세션을 시작하세요.
화면 수집은 분석기 관찰 모드가 담당하며, 이 로그가 화면 검증 성공을 보장하지는 않습니다.

### 단말 없이 준비 상태 확인

```bash
python -m pytest --collect-only -q
qa-capture doctor --project .
```
가상환경 Python/qa-capture 경로를 사용하세요. 수집은 fixture 요청이 발생하는 실제 실행 시점에 수행됩니다.
`qa_observer_bridge.py`의 기존 HTTP 브릿지는 이번 설정에 등록하지 않았습니다.
모든 결과 폴더는 Git에서 제외하고 소스·설정·스크립트·vendor wheel만 커밋합니다.

공식 Allure 안내: https://allurereport.org/docs/pytest/

## 가상환경 비활성화

```bash
deactivate
```
