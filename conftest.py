import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import settings
import locator



@pytest.fixture
def driver():
    """각 TC마다 앱 세션을 시작하고 종료합니다. 앱 데이터는 초기화하지 않습니다."""
    if not settings.UDID or settings.UDID == "YOUR_DEVICE_UDID":
        pytest.fail("settings.py의 UDID를 실제 단말 ID로 변경하세요.", pytrace=False)

    options = UiAutomator2Options().load_capabilities({
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": settings.DEVICE_NAME,
        "appium:udid": settings.UDID,
        "appium:appPackage": settings.APP_PACKAGE,
        "appium:appActivity": settings.APP_ACTIVITY,
        "appium:noReset": True,
        "appium:newCommandTimeout": 120,
    })
    app = webdriver.Remote(settings.APPIUM_URL, options=options)
    try:
        # 이전 TC의 화면 상태에 의존하지 않도록 앱 프로세스만 재시작합니다.
        # 로그인 등 저장된 앱 데이터는 유지됩니다.
        app.terminate_app(settings.APP_PACKAGE)
        app.activate_app(settings.APP_PACKAGE)
        app.implicitly_wait(0)
        yield app
    finally:
        app.quit()


@pytest.fixture
def home_screen(driver):
    """첫 안내/로그인 팝업이 있다면 기존 처리 코드를 이 대기 앞에 추가하세요."""
    WebDriverWait(driver, settings.WAIT_SECONDS).until(
        EC.visibility_of_element_located(locator.HOME_LOGO),
        message="메인 로고가 보이지 않습니다. 초기 팝업/현재 화면/로케이터를 확인하세요.",
    )
    return driver

