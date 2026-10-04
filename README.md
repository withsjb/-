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

## 가상환경 비활성화

```bash
deactivate
```
