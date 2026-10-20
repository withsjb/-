"""기존 공통 화면 4개와 함께 실행하는 추가 16개 TC(guest는 기존 식별자).

앱 데이터·로그인은 초기화하지 않으며 구매·쿠폰 발급·계정 변경은 수행하지 않습니다.
기존 home_screen fixture와 수집기·Allure 설정을 그대로 사용합니다.
"""
import pytest
import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WAIT_SECONDS = 20
HOME_LOGO = '//android.widget.ImageView[@content-desc="T 멤버십 홈"]'
MEMBERSHIP_TAB = '//android.widget.LinearLayout[@content-desc="T 멤버십"]'
SEARCH_BUTTON = '//android.widget.ImageView[@content-desc="통합검색"]'
MENU_BUTTON = '//android.widget.ImageView[@content-desc="전체메뉴 열기"]'
T_DAY = '//android.view.View[@content-desc="T day"]'
DESTINATION = '//*[@resource-id="subHeaderTitle"]'
DESTINATION_BACK = '//*[@resource-id="subHeaderBackBtn"]'
POPULAR_SEARCH = '//android.widget.TextView[@text="인기 검색어"]'


def visible(driver, xpath, timeout=WAIT_SECONDS):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath)),
        message=f"표시 요소를 찾지 못했습니다: {xpath}",
    )


def click(driver, xpath):
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, xpath)),
        message=f"클릭할 요소를 찾지 못했습니다: {xpath}",
    ).click()


def open_day(driver):
    click(driver, MEMBERSHIP_TAB)
    click(driver, T_DAY)
    return visible(driver, DESTINATION, timeout=settings.NAVIGATION_WAIT_SECONDS)


def leave_day(driver, toolbar=False):
    if toolbar:
        click(driver, DESTINATION_BACK)
    else:
        driver.back()
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.invisibility_of_element_located((By.XPATH, DESTINATION)),
        message="T day 종료 후 목적지 제목이 닫히지 않았습니다.",
    )
    return visible(driver, HOME_LOGO)


def leave_search(driver):
    driver.back()
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.invisibility_of_element_located((By.XPATH, POPULAR_SEARCH)),
        message="검색 종료 후 인기 검색어 영역이 닫히지 않았습니다.",
    )
    return visible(driver, HOME_LOGO)


@pytest.mark.guest_home
@pytest.mark.parametrize(
    "tc_id,xpath",
    [
        pytest.param("TC_GUEST_HOME_LOGO", HOME_LOGO, id="TC_GUEST_HOME_LOGO"),
        pytest.param("TC_GUEST_HOME_TAB", MEMBERSHIP_TAB, id="TC_GUEST_HOME_TAB"),
        pytest.param("TC_GUEST_HOME_SEARCH", SEARCH_BUTTON, id="TC_GUEST_HOME_SEARCH"),
        pytest.param("TC_GUEST_HOME_MENU", MENU_BUTTON, id="TC_GUEST_HOME_MENU"),
    ],
)
def test_home_controls(home_screen, tc_id, xpath):
    element = visible(home_screen, xpath)
    assert element.is_displayed(), "메인 화면의 필수 요소가 보이지 않습니다."


@pytest.mark.guest_quickmenu
@pytest.mark.parametrize(
    "tc_id,label",
    [
        pytest.param("TC_GUEST_QUICK_DAY", "T day", id="TC_GUEST_QUICK_DAY"),
        pytest.param("TC_GUEST_QUICK_VIP", "VIP PICK", id="TC_GUEST_QUICK_VIP"),
        pytest.param("TC_GUEST_QUICK_CLUB", "클럽 멤버십", id="TC_GUEST_QUICK_CLUB"),
        pytest.param("TC_GUEST_QUICK_LONG", "T 장기고객", id="TC_GUEST_QUICK_LONG"),
    ],
)
def test_quickmenu_labels(home_screen, tc_id, label):
    click(home_screen, MEMBERSHIP_TAB)
    menu = visible(home_screen, f'//android.view.View[@content-desc="{label}"]')
    assert menu.is_displayed(), "퀵메뉴 항목이 보이지 않습니다."
    assert menu.get_attribute("content-desc") == label, "퀵메뉴 이름이 다릅니다."


@pytest.mark.guest_day_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_RETURN", id="TC_GUEST_DAY_RETURN")])
@pytest.mark.guest_flow_a
def test_day_returns_home(home_screen, tc_id):
    title = open_day(home_screen)
    assert title.text == "T day", "목적지 제목이 T day와 다릅니다."
    logo = leave_day(home_screen)
    assert logo.is_displayed(), "T day 종료 후 메인 로고가 보이지 않습니다."
    menu = visible(home_screen, T_DAY)
    assert menu.is_displayed(), "복귀 후 T day 퀵메뉴가 보이지 않습니다."


@pytest.mark.guest_day_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_TOOLBAR", id="TC_GUEST_DAY_TOOLBAR")])
@pytest.mark.guest_flow_a
def test_day_toolbar_back(home_screen, tc_id):
    title = open_day(home_screen)
    assert title.text == "T day", "목적지 제목이 T day와 다릅니다."
    logo = leave_day(home_screen, toolbar=True)
    assert logo.is_displayed(), "상단 뒤로가기 후 메인 로고가 보이지 않습니다."
    menu = visible(home_screen, MENU_BUTTON)
    assert menu.is_displayed(), "상단 뒤로가기 후 전체메뉴 버튼이 보이지 않습니다."


@pytest.mark.guest_day_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_REENTER", id="TC_GUEST_DAY_REENTER")])
@pytest.mark.guest_flow_b
def test_day_reentry(home_screen, tc_id):
    for _ in range(2):
        title = open_day(home_screen)
        assert title.text == "T day", "재진입한 화면 제목이 T day와 다릅니다."
        logo = leave_day(home_screen)
        assert logo.is_displayed(), "각 진입 종료 후 메인 로고가 보이지 않습니다."


@pytest.mark.guest_day_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_AFTER_SEARCH", id="TC_GUEST_DAY_AFTER_SEARCH")])
@pytest.mark.guest_flow_b
def test_day_after_search(home_screen, tc_id):
    click(home_screen, SEARCH_BUTTON)
    popular = visible(home_screen, POPULAR_SEARCH)
    assert popular.is_displayed(), "선행 검색 화면이 보이지 않습니다."
    leave_search(home_screen)
    title = open_day(home_screen)
    assert title.text == "T day", "검색 복귀 후 T day 목적지가 다릅니다."
    logo = leave_day(home_screen)
    assert logo.is_displayed(), "마지막 메인 복귀를 확인하지 못했습니다."


@pytest.mark.guest_search_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_TEXT", id="TC_GUEST_SEARCH_TEXT")])
@pytest.mark.guest_flow_a
def test_search_popular_text(home_screen, tc_id):
    click(home_screen, SEARCH_BUTTON)
    popular = visible(home_screen, POPULAR_SEARCH)
    assert popular.is_displayed(), "인기 검색어가 보이지 않습니다."
    assert popular.text == "인기 검색어", "인기 검색어 제목 문구가 다릅니다."
    leave_search(home_screen)


@pytest.mark.guest_search_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_CLOSE", id="TC_GUEST_SEARCH_CLOSE")])
@pytest.mark.guest_flow_b
def test_search_closes_and_returns_home(home_screen, tc_id):
    click(home_screen, SEARCH_BUTTON)
    popular = visible(home_screen, POPULAR_SEARCH)
    assert popular.is_displayed(), "검색 화면 진입을 확인하지 못했습니다."
    logo = leave_search(home_screen)
    assert logo.is_displayed(), "검색 종료 후 메인 로고가 보이지 않습니다."
    menu = visible(home_screen, MENU_BUTTON)
    assert menu.is_displayed(), "검색 종료 후 전체메뉴 버튼이 보이지 않습니다."


@pytest.mark.guest_search_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_REENTER", id="TC_GUEST_SEARCH_REENTER")])
@pytest.mark.guest_flow_b
def test_search_reentry(home_screen, tc_id):
    for _ in range(2):
        click(home_screen, SEARCH_BUTTON)
        popular = visible(home_screen, POPULAR_SEARCH)
        assert popular.is_displayed(), "검색 재진입 후 인기 검색어가 보이지 않습니다."
        logo = leave_search(home_screen)
        assert logo.is_displayed(), "검색 종료마다 메인으로 복귀하지 못했습니다."


@pytest.mark.guest_search_extra
@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_AFTER_DAY", id="TC_GUEST_SEARCH_AFTER_DAY")])
@pytest.mark.guest_flow_a
def test_search_after_day(home_screen, tc_id):
    title = open_day(home_screen)
    assert title.text == "T day", "선행 T day 화면 제목이 다릅니다."
    leave_day(home_screen)
    click(home_screen, SEARCH_BUTTON)
    popular = visible(home_screen, POPULAR_SEARCH)
    assert popular.is_displayed(), "T day 복귀 후 검색 화면이 보이지 않습니다."
    logo = leave_search(home_screen)
    assert logo.is_displayed(), "검색 종료 후 메인으로 복귀하지 못했습니다."
