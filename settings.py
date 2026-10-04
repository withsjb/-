"""기존 Appium 환경에 맞게 이 파일의 값과 로케이터만 변경하세요."""
from appium.webdriver.common.appiumby import AppiumBy

# 서버가 --base-path /wd/hub로 실행 중이면 끝에 /wd/hub를 붙이세요.
APPIUM_URL = "http://127.0.0.1:4723"

# adb devices에서 확인한 단말 ID를 입력하세요.
UDID = "RF9R408KHNB"
DEVICE_NAME = "Android"

# 예시 값입니다. 현재 설치된 앱에 따라 com.tms / com.tms.qa / com.tms.green 등으로 변경.
APP_PACKAGE = "com.tms"
APP_ACTIVITY = "com.tms.activity.MainActivityDefault"
WAIT_SECONDS = 20

