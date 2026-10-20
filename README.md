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
최신 전달물 20261020.01의 수집기는 0.4.7입니다. 기존 0.4.7/0.4.8 설치와 관계없이 동봉 wheel을 `--force-reinstall --no-deps`로 재설치하고 체크섬으로 내용을 확인하세요. 상세 순서는 [Windows 이어서 확인하기](WINDOWS_HANDOFF_20261020.md)를 따릅니다.

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

## 고객 화면 테스트 20개 실행

기존 `tests/test_guest.py`의 4개는 유지하고 `tests/test_guest_extended.py`에 16개를 추가했습니다.

`guest` 파일명·`TC_GUEST_*` ID는 기존 식별자이며 로그인 상태를 자동 판별한 결과가 아닙니다.
현재 fixture는 `noReset=True`로 앱의 로그인 정보를 유지합니다. 준비 시 메인의 사용자 표시와 포인트 영역으로 로그인 화면 표시를 확인하고 판별할 수 없으면 `unknown`으로 기록합니다.
따라서 로그인한 단말에서는 로그인 상태로 공통 화면 흐름을 검사합니다. 실제 20개 실행 증거도 로그인 상태였습니다.
현재 20개 CSV와 기존 4개 묶음 CSV의 대분류는 모두 `공통`으로 정리했습니다. 과거 ZIP·이력·기존 qa-results 안의 명세는 변경하지 않습니다.
비로그인 전용 검증은 실행 전에 직접 로그아웃하고 `settings.py`의 `EXPECTED_LOGIN_STATE = "logged_out"`으로 지정하세요. `logged_in`은 로그인 화면 표시를 요구하고 기본 `any`는 공통 흐름을 허용합니다. 이 설정은 자동 로그인·로그아웃을 수행하지 않습니다.
기존 결과 연결을 유지하기 위해 TC ID와 저장된 ZIP·이력은 변경하지 않습니다.
메인 필수 요소 4개, 퀵메뉴 표시 4개, T day 복귀·재진입·검색 후 이동 4개,
검색 문구·종료·재진입·T day 후 이동 4개입니다. 추가 테스트는 앱 데이터나 로그인을 초기화하지 않습니다.
연결 단말과 Appium을 준비한 뒤 프로젝트 루트에서 실행합니다.

```bash
python -m pytest tests/test_guest.py tests/test_guest_extended.py -s -v
```

전체 실행과 맞는 관찰용 CSV는 `test_data/guest_blindspot_20.csv`입니다.
수집기 자동 로그 모드에서는 TC ID를 자동 연결하며 기존 시작·종료 형식을 직접 바꿀 필요가 없습니다.
일반 pytest 실행의 로그는 `qa-results/observation.log`를 사용합니다.
관찰을 먼저 시작하고 ‘관찰 준비 완료’를 확인한 다음 위 명령을 실행합니다.
테스트가 모두 끝나면 관찰 화면에서 ‘관찰 종료·분석’을 누릅니다.

Allure·수집 ZIP·로그를 실행별로 나누어 저장하려면 기존 실행 스크립트를 사용할 수 있습니다.
이 명령의 결과는 새로운 `test-artifacts/실행ID/`에 보관하며 이전 결과를 삭제하지 않습니다.

```bash
python scripts/run_reports.py --tc-csv test_data/guest_blindspot_20.csv tests/test_guest.py tests/test_guest_extended.py
```

이 스크립트와 화면 관찰을 함께 쓸 때는 먼저 고정 로그를 준비합니다.

```bash
python scripts/run_reports.py --prepare-log --observation-log test-artifacts/live-observation.log
```

관찰 화면에 `test-artifacts/live-observation.log`의 절대 경로를 넣고 관찰을 준비한 다음 실행합니다.

```bash
python scripts/run_reports.py --observation-log test-artifacts/live-observation.log --tc-csv test_data/guest_blindspot_20.csv tests/test_guest.py tests/test_guest_extended.py
```

### 4개씩 나누어 분석하기

20개 전체는 대량 실행·로그 연결 점검용으로 사용할 수 있습니다. 일반 캡처의 예상 AI 요청은
최대 표본 기준 약 296회이며 기본 검토 40회·전체 96회 한도를 넘을 수 있습니다.
추가 오류가 없어도 이어 분석이 필요할 수 있으므로 아래 4개 단위 실행을 권장합니다.
각 행의 CSV와 명령은 같은 TC만 포함합니다. 일반 캡처 기준 각 묶음의 예상 요청은 96회 이내이지만,
실제 표본·재시도·모델 수에 따라 처리 시간과 완료 여부는 달라집니다.

| 묶음 | 관찰 CSV (`test_data/guest_batches/` 아래) | pytest 실행 대상·선택 |
| --- | --- | --- |
| 기존 4개 | `01_original.csv` | `tests/test_guest.py` |
| 메인 4개 | `02_home.csv` | `tests/test_guest_extended.py -m guest_home` |
| 퀵메뉴 4개 | `03_quickmenu.csv` | `tests/test_guest_extended.py -m guest_quickmenu` |
| 화면 이동 A 4개 | `04_navigation_a.csv` | `tests/test_guest_extended.py -m guest_flow_a` |
| 화면 이동 B 4개 | `05_navigation_b.csv` | `tests/test_guest_extended.py -m guest_flow_b` |

예를 들어 `04_navigation_a.csv`를 관찰 화면에 올렸다면 다음과 같이 실행합니다.

```bash
python -m pytest tests/test_guest_extended.py -m guest_flow_a -s -v
```

일반 캡처는 총 600장 제한이 있습니다. 전체 20개를 관찰할 때 0.5초 간격은 테스트 완료 전에
한도에 도달할 수 있습니다. 순간 화면 확인이 목적이면 4개씩 나누고 기존 간격을 유지하세요.
전체 부하·연결 점검이 목적이면 최대 관찰 시간을 1800~3600초로 두고 2~3초 간격 또는 연속 영상을 선택할 수 있습니다.
2초 간격도 저장 구간이 누적 약 20분에 이르면 600장에 도달할 수 있으며 전후 버퍼도 장수에 포함됩니다.
연속 영상은 원본 녹화와 AI가 검토하는 표본이 다릅니다.

pytest 수집 목록만 확인하려면 아래 명령을 사용합니다. 단말은 실행하지 않습니다.

```bash
python -m pytest tests/test_guest.py tests/test_guest_extended.py --collect-only -q
```

20개 실제 실행의 Allure ZIP과 QA 수집 ZIP 모두 한 번에 가져올 수 있습니다(최신 분석기 기준).
QA 수집 ZIP의 반복 XML 요약은 중복을 제거해 메모리에서 공유합니다. 원본 XML·이미지와 검사 기록은 유지합니다.
ZIP/manifest/파일 크기 및 서로 다른 XML 요약의 구조·텍스트 한도는 계속 적용됩니다.
한 번에 가져오기와 AI 분석 요청 한도는 별개이므로 전체 20개 AI 분석에는 이어 분석이 필요할 수 있습니다.
Allure 증적 가져오기와 QA 수집 ZIP의 실제 검사 기록 비교는 제공되는 근거 범위가 다릅니다.

### QA ZIP 명세 자동 연결과 첫 화면 준비

현재 `pytest.ini`에 `qa_capture_tc_csv = test_data/guest_blindspot_20.csv`가 설정되어 있으므로
평소 `python -m pytest ...` 명령만 실행해도 **실제 실행한 TC**의 명세를 QA ZIP에 넣습니다.
기존 ZIP에는 소급 적용하지 않습니다. `scripts/run_reports.py --tc-csv ...`를 사용하면 실행 전
CSV를 복사해 같은 명세를 QA ZIP과 Allure 결과에 사용합니다. 별도 CSV를 전달하지 않아도
QA ZIP은 pytest.ini의 기본 명세를 사용합니다.

첫 홈 진입은 로고·멤버십 탭·T day·검색 버튼이 활성 상태이고 로딩 표시가 없는 상태를
1초 이상 확인합니다. 초기 준비 제한은 60초이고 T day 목적지 표시 대기는 45초입니다.
테스트의 기존 표시·문구 assert는 유지하며 화면을 다시 누르거나 실패를 자동 통과시키지 않습니다.
`settings.py`의 준비/목적지 대기는 페이지 준비에만 적용하고 다른 기본 대기는 20초를 유지합니다.

Allure에는 ‘로그인 준비 상태’ JSON, QA ZIP의 실행 구간에는 ‘준비 시 로그인 상태’ 메모가
남습니다. HTML 보고서에서는 ‘실행 준비 상태 · 로그인 표시’를 펼쳐 확인합니다. 계정 이름이나
포인트 값은 이 상태 기록에 저장하지 않습니다. 원래 화면 증거에는 기존과 같이 화면 내용이 포함될 수 있습니다.

단말 없이 준비 조건만 검사하려면 `python -m pytest validation -q -o qa_capture=false -o addopts=`를
실행하세요. 기본 tests/의 고객 테스트 수와 TC ID는 바꾸지 않습니다.
