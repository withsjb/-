"""기존 home_screen fixture를 사용하는 T 멤버십 테스트."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECONDS = 20
HOME_LOGO = '//android.widget.ImageView[@content-desc="T 멤버십 홈"]'
MEMBERSHIP_TAB = '//android.widget.LinearLayout[@content-desc="T 멤버십"]'
T_DAY = '//android.view.View[@content-desc="T day"]'
DESTINATION = '//android.widget.TextView[@resource-id="subHeaderTitle"]'
SEARCH_BUTTON = '//android.widget.ImageView[@content-desc="통합검색"]'
POPULAR_SEARCH = '//android.widget.TextView[@text="인기 검색어"]'
MENU_BUTTON = '//android.widget.ImageView[@content-desc="전체메뉴 열기"]'


def click(driver, xpath):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, xpath)),
        message=f"클릭할 요소를 찾지 못했습니다: {xpath}",
    ).click()


def visible(driver, xpath):
    return WebDriverWait(driver, WAIT_SECONDS).until(
        EC.visibility_of_element_located((By.XPATH, xpath)),
        message=f"표시 요소를 찾지 못했습니다: {xpath}",
    )


def open_t_day(driver):
    click(driver, MEMBERSHIP_TAB)
    click(driver, T_DAY)
    return visible(driver, DESTINATION)


def return_from_t_day(driver):
    driver.back()
    WebDriverWait(driver, WAIT_SECONDS).until(
        EC.invisibility_of_element_located((By.XPATH, DESTINATION)),
        message="뒤로가기 후 제목 영역이 닫히지 않았습니다.",
    )
    visible(driver, T_DAY)


@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_A", id="TC_GUEST_DAY_A")])
def test_t_day_a(home_screen, tc_id):
    driver = home_screen
    destination = open_t_day(driver)
    assert destination.is_displayed(), "목적지 제목 요소가 보이지 않습니다."
    return_from_t_day(driver)


@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_DAY_B", id="TC_GUEST_DAY_B")])
def test_t_day_b(home_screen, tc_id):
    driver = home_screen
    destination = open_t_day(driver)
    assert destination.is_displayed(), "목적지 제목 요소가 보이지 않습니다."
    assert destination.text == "T day", "목적지 제목이 T day와 다릅니다."
    return_from_t_day(driver)


@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_A", id="TC_GUEST_SEARCH_A")])
def test_search_a(home_screen, tc_id):
    driver = home_screen
    click(driver, SEARCH_BUTTON)
    driver.back()
    menu = visible(driver, MENU_BUTTON)
    assert menu.is_displayed(), "검색 종료 후 전체메뉴 버튼이 보이지 않습니다."


@pytest.mark.parametrize("tc_id", [pytest.param("TC_GUEST_SEARCH_B", id="TC_GUEST_SEARCH_B")])
def test_search_b(home_screen, tc_id):
    driver = home_screen
    click(driver, SEARCH_BUTTON)
    popular = visible(driver, POPULAR_SEARCH)
    assert popular.is_displayed(), "검색 화면의 인기 검색어가 보이지 않습니다."
    driver.back()
    menu = visible(driver, MENU_BUTTON)
    assert menu.is_displayed(), "검색 종료 후 전체메뉴 버튼이 보이지 않습니다."
