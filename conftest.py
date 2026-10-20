import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
import settings
from ui_readiness import wait_home, check_authentication
import json
import allure

pytest_plugins = ["qa_allure"]



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
        "appium:uiautomator2ServerInstallTimeout": 120000,
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
def home_screen(driver, record_property):
    """공통 메인의 준비 상태와 화면 로그인 표시를 확인하며 앱 데이터는 유지합니다."""
    wait_home(driver, settings.HOME_READY_TIMEOUT, settings.HOME_READY_STABLE_SECONDS)
    state = check_authentication(driver, settings.EXPECTED_LOGIN_STATE)
    record_property('qa_auth_state', state)
    record_property('qa_auth_policy', 'preserve')
    record = {'state': state, 'basis': 'home_ui_indicators', 'policy': 'preserve',
              'expected': settings.EXPECTED_LOGIN_STATE}
    # 상태 코드만 보관합니다. 이름·포인트·인증 정보는 이 기록에 넣지 않습니다.
    allure.attach(json.dumps(record, ensure_ascii=False), name='로그인 준비 상태',
                  attachment_type=allure.attachment_type.JSON)
    return driver
