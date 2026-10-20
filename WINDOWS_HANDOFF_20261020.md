# 집 Windows PC 이어서 확인하기 — 20261020.01

## 이번 전달물과 확인 범위

- 분석기: `qa_blindspot_review-0.4.7-build-20261020.01.zip`
- 고객 테스트 프로젝트: `android_pytest_sample-build-20261020.01.zip`
- 각 ZIP 옆 `.sha256`은 압축 파일 해시입니다. 압축 해제 후에는 `MANIFEST.sha256`과 검증 스크립트로 내부 파일도 확인합니다.
- 현재 수집기 wheel: `qa_blindspot_capture-0.4.7-py3-none-any.whl`
- 수집기 SHA-256: `353921215ae28cb23aa3d0ffca9e43d094a171eecd6b7d27290a932aafec59c5`

같은 0.4.7이 이미 설치돼 있어도 내용이 다를 수 있으므로 **wheel을 강제로 재설치**합니다. 기존 Windows에 0.4.8이 있다면 자동으로 최신이라고 판단하지 말고 이번 전달물과 위 해시를 기준으로 맞춥니다. 이 안내는 이번 소스/배포 묶음의 0.4.7에 맞춘 절차입니다.

포함: 자동 관찰 로그·TC 로그 연결, 테스트 구간 일반 캡처, 분석 진행 표시, 오류 진단·재시도, macOS/Windows OCR 경로, 대량 ZIP의 XML 요약 공유·저장 크기 보호, TC 명세 자동 포함, 공통 분류·로그인 표시 기록, 홈 준비 및 T day 목적지 대기 개선, 최신 UI·보고서와 수집기 wheel.

현재 Mac 검증: Python 1,231건·UI 105건 통과, 고객 준비 조건 검사 3건 통과. 최신 수집기를 설치한 실제 단말 첫 두 TC 모두 통과(143초), 로그인 화면 표시와 자동 TC 명세·보고서·재가져오기 확인. 이전 실제 20개 ZIP(20 TC·228화면·111검사) 가져오기 호환도 확인했습니다. 이전 20개 단말 실행은 19개 통과·첫 TC 1개 실패였고 별도 재실행은 통과했습니다. 최신 수정 후 20개 전체 단말 재실행 및 20개 전체 AI 분석, 이번 빌드의 Windows 실환경 검증은 아직 하지 않았습니다.

두 ZIP에는 `.venv`, `review-data`, `config.toml`, 고객의 `qa-results`·`test-artifacts`·Allure 결과, 모델, Git 저장소가 포함되지 않습니다. 고객 프로젝트의 `settings.py`는 현재 코드 사본입니다. 집에서 쓸 단말 ID·Appium 주소·로그인 전제조건을 확인하세요. 고객 프로젝트 ZIP만으로 실제 단말 결과가 이동되지는 않습니다.

## 1. 이동할 자료 준비와 기존 이력 보존

코드 이동은 두 저장소의 최신 변경을 커밋·push/pull하거나 위 ZIP을 새 폴더에 해제하는 방법 중 하나를 사용합니다. 이번 준비 작업에서 Git 커밋·push는 수행하지 않았습니다. Git을 사용할 때 새 `specification.py`, `ui_readiness.py`, 20개 TC·CSV·validation 파일과 갱신된 vendor wheel도 함께 반영해야 합니다. 결과·환경 폴더는 커밋하지 않습니다. 기존에 staging된 삭제 파일이 있다면 `git diff --cached --name-status`로 의도를 확인하고 `git add .`를 무심코 실행하지 마세요.

이력을 이동하려면 Mac 서버와 분석을 종료한 상태에서 분석기의 **review-data 전체**와 개인 `config.toml`을 별도 복사합니다. `.venv`는 옮기지 않습니다. 집 Windows에도 이력이 있다면 덮어쓰거나 두 DB를 합치지 말고 새 폴더에 복원합니다. 코드 ZIP에는 이력이 없습니다.

분석기의 백업 기능을 쓸 수도 있습니다(Mac 서버 종료 후):

```bash
.venv/bin/python -m qa_review storage backup --data review-data --output /path/to/new-backup
.venv/bin/python -m qa_review storage verify --backup /path/to/new-backup
```

`/path/to/new-backup`은 존재하지 않는 새 출력 경로로 바꿉니다. 백업 전체와 `config.toml`을 Windows로 옮깁니다. Windows에서 분석기 설치 후 새 경로에 복원하는 명령은 아래 2번에 있습니다. 단순 폴더 복사를 선택했다면 복원 명령은 실행하지 않습니다. 자세한 규칙은 `docs/PC_MIGRATION.md`, `docs/STORAGE.md`를 따릅니다.

AI만 검증하려면 단말 테스트를 다시 실행할 필요 없이 기존 실제 결과를 가져갈 수 있습니다.

- 기존 20개 QA ZIP: Mac 고객 프로젝트의 `test-artifacts/20261020-133754-dc951784/qa-results/56564d940cd94c5bab23d0b2a1774e2e.zip`
- 대응 명세: 고객 프로젝트 `test_data/guest_blindspot_20.csv`
- 필요 시 원본 진단: 같은 QA ZIP 옆 `.diagnostics.json`, 실행 폴더의 `run-summary.json`·`observation.log`

**이 기존 ZIP은 자동 명세 포함 수정 전에 만들어졌으므로 가져온 뒤 TC CSV를 한 번 반영합니다.** 새 wheel 설치가 과거 ZIP이나 이력을 수정하지 않습니다. 원본 ZIP은 보존하고 시험용으로 새로 가져온 이력에만 CSV를 반영하세요.

## 2. Windows 분석기 설치·이전

아래 예시 경로를 실제 압축 해제한 프로젝트 루트로 바꿉니다. 두 프로젝트의 가상환경은 별개입니다. PowerShell 활성화 대신 각 프로젝트 Python 경로를 직접 사용합니다.

```powershell
$ReviewRoot = 'C:\QA\qa_blindspot_review-0.4.7-build-20261020.01'
$CustomerRoot = 'C:\QA\android_pytest_sample-build-20261020.01'
Set-Location $ReviewRoot
py -3 --version
py -3 scripts/verify_distribution.py
# 출력 빌드 번호가 20261020.01인지 확인
.\setup.cmd
if ($LASTEXITCODE -ne 0) { throw '분석기 설치 실패' }
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/build_release.py --check
```

기존 Windows 폴더를 업데이트하려면 서버 종료·백업 후 `CUSTOMER_INSTALL_CHECKLIST.md`의 업데이트 절차를 사용합니다. 이 안내의 새 폴더 경로와 기존 폴더를 혼동하지 마세요. 기존 `config.toml`은 예시로 덮어쓰지 않습니다. 새 설치만 `config.example.toml`을 복사해 사용할 모델을 맞춥니다.

Mac에서 만든 저장소 백업을 새 경로로 복구하는 경우만:

```powershell
.\.venv\Scripts\python.exe -m qa_review storage verify --backup 'D:\QA-transfer\review-backup'
.\.venv\Scripts\python.exe -m qa_review storage restore --backup 'D:\QA-transfer\review-backup' --output "$ReviewRoot\review-data"
```

복구 대상 `review-data`는 아직 없어야 합니다. 이미 있는 이력에 복원하거나 합치지 않습니다. `config.toml`은 백업에 포함되지 않으므로 별도로 복사합니다. Mac 경로가 들어 있는 개인 설정은 Windows에 맞게 확인하고, 과거 이력 JSON의 경로·ID는 일괄 변경하지 않습니다.

```powershell
ollama list
adb devices -l
.\start.cmd
```

`start.cmd` 터미널은 켜 둡니다. 브라우저는 `http://127.0.0.1:8770`입니다. 앱의 준비 상태에서 AI·영상·OCR 상태를 확인합니다. Windows OCR 언어·USB 드라이버·Ollama 모델·ADB는 setup이 대신 설치하지 않습니다. 준비 상태 성공만으로 OCR 인식이나 AI 분석 완료를 판정하지 않습니다. 한글 PDF는 맑은 고딕을 확인합니다.

복원한 이력이 보이는지 건수·ID·대표 캡처/보고서를 대조합니다. 현재 Mac 기준은 ZIP 24개, 관찰 2개였으며 집 PC의 기존 이력이 다르면 그 PC의 사전 기록을 기준으로 합니다.

## 3. 고객 프로젝트와 새 wheel 재설치

분석기 서버와 다른 PowerShell에서:

```powershell
Set-Location $CustomerRoot
# 고객 소스 ZIP을 쓴 경우: 설치 전에 무결성 확인
py -3 scripts/verify_customer_delivery.py
# 새 PC/새 폴더에 가상환경이 없을 때만 생성
if (-not (Test-Path .\.venv\Scripts\python.exe)) { py -3 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw '고객 의존성 설치 실패' }
.\.venv\Scripts\python.exe -m pip install --force-reinstall --no-deps .\vendor\qa_blindspot_capture-0.4.7-py3-none-any.whl
if ($LASTEXITCODE -ne 0) { throw '수집기 재설치 실패' }
.\.venv\Scripts\python.exe -m pip check
Get-FileHash -Algorithm SHA256 .\vendor\qa_blindspot_capture-0.4.7-py3-none-any.whl
.\.venv\Scripts\qa-capture.exe doctor --project .
.\.venv\Scripts\python.exe -m pytest tests/test_guest.py tests/test_guest_extended.py --collect-only -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest validation -q -p no:cacheprovider -o qa_capture=false -o addopts=
```

Git 소스에는 `verify_customer_delivery.py`가 없을 수 있습니다. 이 스크립트와 MANIFEST는 고객 소스 ZIP에 생성된 무결성 자료이며, ZIP 사용 시 실행합니다. 파일을 수정한 뒤 검사하면 해시가 달라지는 것이 정상입니다. 설치 전에 검사하세요.

수집 목록이 정확히 20개이고 준비 조건 검사 3건이 통과하는지 확인합니다. `tests/`에는 기존 다른 실험 파일도 보존되어 있으므로 **20개 검증은 위 두 테스트 파일을 명시**합니다. 새 wheel 재설치에는 `--force-reinstall --no-deps`가 필요합니다. 단순 `pip install`이나 버전 0.4.7 표시만으로 최신 코드를 확인하지 않습니다.

현재 `pytest.ini`의 `qa_capture_tc_csv = test_data/guest_blindspot_20.csv`를 확인합니다. 평소 pytest 명령을 유지할 수 있으며, 실행한 TC ID와 정확히 같은 명세만 QA ZIP에 들어갑니다. 기존 로그 옵션과 Allure도 유지합니다. `qa-capture init`은 이미 설정된 이 프로젝트에서 다시 실행할 필요가 없습니다.

`settings.py`의 UDID를 `adb devices -l`과 맞추고 Appium 서버(기본 4723)·UiAutomator2를 준비합니다. 기존 Appium 환경이 정상이라면 재설치하지 않습니다. `EXPECTED_LOGIN_STATE='any'`는 저장된 로그인 정보를 유지하는 공통 테스트입니다. `guest` ID는 과거 이력 연결용이며 비로그인 판정이 아닙니다. 비로그인 전용 확인은 직접 로그아웃 후 `logged_out`, 로그인 전용은 `logged_in`을 지정합니다. 화면 지표를 못 읽으면 unknown으로 기록하며 상태를 추측하지 않습니다.

## 4. 새 결과가 필요할 때만 실제 단말 실행

AI 검증에 기존 20개 ZIP을 사용할 경우 이 절은 건너뛸 수 있습니다. 새 wheel의 수집까지 확인하려면 먼저 첫 두 TC로 짧게 확인합니다. 아래 명령은 실제 앱을 조작합니다.

```powershell
Set-Location $CustomerRoot
.\.venv\Scripts\python.exe scripts/run_reports.py --tc-csv test_data/guest_batches/01_original.csv tests/test_guest.py::test_t_day_a tests/test_guest.py::test_t_day_b
```

새 `test-artifacts/실행ID/`의 `run-summary.json`, QA ZIP·Allure ZIP·로그를 확인합니다. QA ZIP의 TC 2개 모두 제목·기대 결과와 공통 분류, 로그인 준비 메모가 있는지 확인합니다. 실행 스크립트는 매번 새 폴더를 만들며 기존 결과를 지우지 않습니다.

이상이 없고 전체 새 결과가 필요하면:

```powershell
.\.venv\Scripts\python.exe scripts/run_reports.py --tc-csv test_data/guest_blindspot_20.csv tests/test_guest.py tests/test_guest_extended.py
```

이전 전체 실행은 약 15분 32초였으며 Windows·단말·네트워크에 따라 달라집니다. `run-summary.json`의 종료 코드와 실제 각 TC의 pytest/Allure 결과를 확인합니다. 시험 실행 실패를 AI 분석 실패나 통과로 바꾸지 않습니다. 새 ZIP은 실행된 20개 명세를 포함해야 하며 TC CSV를 별도 업로드하지 않아도 됩니다.

화면 관찰도 확인할 때는 먼저 기존처럼 `--prepare-log --observation-log test-artifacts/live-observation.log`로 로그를 준비하고 관찰 화면에서 절대 Windows 경로와 20개 CSV를 선택합니다. 관찰 준비 완료 후 같은 `--observation-log`를 사용해 실행합니다. 기존 방식·자동 로그 모드를 섞어 중복 로그를 쓰지 않습니다. 일반 캡처는 테스트 전후 버퍼 구간을 저장하며 연속 영상은 기존 녹화를 유지합니다. 최대 수집 시간·600장 한도와 장시간 실행 시 누락을 확인합니다. ZIP AI 분석만 확인하는 이번 기본 절차에는 화면 관찰 녹화가 필요하지 않습니다.

## 5. 20개 TC AI 분석 검증 순서

1. 분석기에서 확인용 이름으로 **QA 수집 결과 ZIP**을 새로 가져옵니다. Allure ZIP은 다른 입력이며, 실제 검사 기록 비교에는 QA ZIP을 사용합니다.
2. TC가 20개인지 확인합니다. 새 ZIP이면 제목·기대 결과가 자동 표시되어야 합니다. 위에 적은 기존 20개 ZIP이면 ‘TC CSV 추가 · 업데이트’에서 `test_data/guest_blindspot_20.csv`를 한 번 반영합니다. 원본 이력은 수정하지 않습니다.
3. CSV 연결 전 비어 있던 기대 결과가 실제 원문으로 표시되는지 확인합니다. 공통 분류와 guest ID는 별개이며, 과거 ZIP에는 새 로그인 메모를 소급 생성하지 않습니다.
4. 먼저 규칙 분석을 실행해 보고서가 열리는지 확인합니다. 이는 AI 분석 완료가 아닙니다.
5. ‘분석’에서 설치된 **모델 1개**를 선택하고 AI 검토를 켭니다. 기존 설정·모델·이미지 옵션은 유지합니다. `max_images=0`이면 XML·검사 기록 중심이고 이미지는 AI에 전달하지 않습니다. 이미지 판단이 필요하면 이미지 지원 모델과 실제 max_images 설정을 확인한 뒤 별도 검증으로 기록합니다.
6. 첫 AI 점검은 ‘이번 분석 대상 TC’에서 기존 4개를 선택해 응답·처리 상태·소요 시간과 메모리를 확인합니다. 그 다음 같은 ZIP에서 20개 전체를 선택해 새 분석을 실행하거나, 자원이 부족하면 4개씩 5묶음으로 확인합니다. 5묶음 검증 결과를 단일 20개 전체 실행 성능으로 기록하지 않습니다.
7. 실행 전 안내의 예상 처리량·시간·한도를 확인하고 분석을 시작합니다. **ZIP 분석의 설정과 화면 관찰의 요청 한도는 다릅니다.** 관찰의 40/96회나 예전 요청 수 추정치를 ZIP에 그대로 적용하지 않습니다.
8. 일부 완료라면 ‘고급 · 수집 기록과 상세 진단’ 및 TC별 분석 범위에서 남은 배치·오류·제외 이유를 확인합니다. 이어 분석이 제공되면 같은 자료 개정·동일 단일 모델·설정을 유지해 이어갑니다. 중간에 CSV·기대조건·모델을 바꾸면 기존 이어 분석 조건이 달라지므로 새 분석으로 기록합니다. 자동 이어 분석도 횟수·시간 제한과 미처리가 남을 수 있습니다.
9. Windows 작업 관리자의 메모리·CPU·GPU 전용/공유 메모리를 시작 전, 모델 첫 로딩 후, 분석 중 최대, 종료 후에 기록합니다. Ollama 모델 메모리와 Python·브라우저 사용량을 구분하고 다른 무거운 작업은 줄입니다. 20개가 동시에 실행돼 메모리가 20배가 되는 구조는 아니지만 처리 시간은 길어질 수 있습니다.
10. 완료 후 20개 각각의 처리 상태와 미처리 이유, AI 응답/오류·후보 근거를 확인합니다. 상태가 완료여도 모든 기대 결과가 해석됐다는 뜻은 아닙니다. 후보 0건을 전체 TC 검증 충분으로 판정하지 않습니다. 제목을 정확히 비교한 B와 표시만 확인한 A의 검사 기록 차이를 원본 XML·캡처·소스와 대조합니다. 과거 A의 실제 실패도 그대로 해석합니다.
11. HTML·CSV·JSON 보고서를 내려받아 TC 수·기대 결과·원본 근거 참조·한글이 맞는지 확인합니다. 새 수집 ZIP은 HTML의 ‘실행 준비 상태 · 로그인 표시’에서 상태 메모를 확인합니다. 화면 관찰을 따로 검증했다면 PDF·OCR·영상도 별도로 대조합니다.

`Windows_AI_검증기록_20261020.md`에 결과를 기록할 수 있습니다. 표의 전체 실행 시간은 시작 버튼부터 종료까지, 이어 분석 횟수와 대기 포함 여부도 함께 적습니다. 실행하지 않은 항목은 미검증으로 남깁니다.

## 6. 검증 후 정리

- 실제 20개 원본 ZIP·CSV와 이전 이력·백업은 유지합니다.
- 이번에 만든 **확인용 이력만** 이름과 ID를 대조한 뒤 화면의 삭제 확인 절차로 삭제합니다. 분석 중이라면 먼저 중지/종료를 확인합니다.
- 짧은 확인용 실행의 `test-artifacts/해당 실행ID/`와 다운로드 보고서도 필요가 없을 때 해당 경로만 삭제합니다. 전체 `qa-results`, `test-artifacts`, `review-data`나 기존 Allure 결과를 일괄 삭제하지 않습니다.
- 기존 이력 건수·ID·대표 파일이 그대로인지 확인합니다. 집 PC에서 새로 만든 실제 고객 결과는 확인용인지 보관할 결과인지 구분합니다.

## 집 Codex에 전달할 문장

> 이 폴더의 WINDOWS_HANDOFF_20261020.md와 두 프로젝트 전체 코드를 먼저 확인해 주세요. 최신 기준은 20261020.01 빌드이며 수집기 wheel 체크섬을 대조하고 기존 가상환경에 강제 재설치해 주세요. 기존 기능·로그인 정보·이력·원본 ZIP은 보존하세요. Windows에서 준비 상태·설치·첫 두 TC의 명세 자동 연결과 로그인 메모·보고서를 확인한 뒤, 실제 20개 ZIP으로 단일 모델 AI 분석의 시간·완료율·미처리·오류·메모리와 후보 근거를 검증해 주세요. 기존 20개 ZIP에는 TC CSV를 한 번 반영해야 합니다. 현재 Mac에서 최신 첫 두 TC는 통과했지만 최신 전체20 단말 재실행과 전체20 AI 분석·Windows 실환경은 아직 미검증입니다. 임의로 한도를 크게 늘리거나 검증 조건을 약하게 만들지 말고 병목·실패 원인을 먼저 확인해 주세요. 확인용으로 만든 이력·파일만 끝나면 삭제하고 기존 이력 전후 대조를 해주세요. 이번 Git 작업에는 기존 staging된 삭제도 있을 수 있으므로 커밋·push 전에 목록을 검토하세요.
