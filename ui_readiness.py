"""Read-only screen readiness and explicit authentication indicators for this app."""
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import locator


def _visible(driver, target):
    elements = driver.find_elements(*target)
    return next((e for e in elements if e.is_displayed()), None)


class HomeReady:
    def __init__(self, stable_seconds=1.0, clock=time.monotonic):
        self.stable_seconds = stable_seconds
        self.clock = clock
        self.since = None

    def __call__(self, driver):
        try:
            # A logo alone may be visible while the home page is still loading.
            controls = [_visible(driver, target) for target in
                        (locator.HOME_LOGO, locator.MEMBERSHIP_TAB, locator.T_DAY, locator.HOME_SEARCH)]
            ready = (all(e is not None and e.is_enabled() for e in controls)
                     and not _visible(driver, locator.LOADING_INDICATOR))
        except (NoSuchElementException, StaleElementReferenceException):
            ready = False
        now = self.clock()
        if not ready:
            self.since = None
            return False
        if self.since is None:
            self.since = now
        return driver if now - self.since >= self.stable_seconds else False


def wait_home(driver, timeout, stable_seconds=1.0):
    return WebDriverWait(driver, timeout, poll_frequency=.5).until(
        HomeReady(stable_seconds),
        message='메인 화면 준비 실패: 로고·멤버십 탭·T day·검색 버튼 또는 로딩 표시를 확인하세요. 자동 재탭이나 로그인 변경은 수행하지 않습니다.')


def authentication_state(driver):
    """Report home UI indicators, never read or save account credentials/name."""
    try:
        user = _visible(driver, locator.USER_INFO)
        text = user.text.strip() if user is not None else ''
        login_prompt = '로그인' in text
        member = text.endswith('님') and _visible(driver, locator.POINT_INFO) is not None
        if member and not login_prompt:
            return 'logged_in'
        if login_prompt and not member:
            return 'logged_out'
    except (NoSuchElementException, StaleElementReferenceException):
        pass
    return 'unknown'


def check_authentication(driver, expected='any'):
    if expected not in ('any', 'logged_in', 'logged_out'):
        raise ValueError('EXPECTED_LOGIN_STATE는 any, logged_in, logged_out 중 하나여야 합니다.')
    state = authentication_state(driver)
    if expected != 'any' and state != expected:
        raise AssertionError(f'로그인 준비 조건 불일치: 예상={expected}, 화면 확인={state}. 단말의 로그인 상태를 직접 확인하세요.')
    return state
