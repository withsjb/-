import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECONDS = 20

HOME_LOGO = '//android.widget.ImageView[@content-desc="T 멤버십 홈"]'
QUICKMENU_AREA = '//android.view.View[@resource-id="quickMenu"]'
DESTINATION = '//android.widget.TextView[@resource-id="subHeaderTitle"]'

MENUS = {
    "t_day": {
        "button": '//android.view.View[@content-desc="T day"]',
    },
    "vip_pick": {
        "button": '//android.view.View[@content-desc="VIP PICK"]',
    },
    "club": {
        "button": '//android.view.View[@content-desc="클럽 멤버십"]',
    },
    "long_term": {
        "button": '//android.view.View[@content-desc="T 장기고객"]',
    },
}


@pytest.mark.parametrize(
    "menu_key",
    [
        pytest.param("t_day", id="TC_QM_01"),
        pytest.param("vip_pick", id="TC_QM_02"),
        pytest.param("club", id="TC_QM_03"),
        pytest.param("long_term", id="TC_QM_04"),
    ],
)
def test_quickmenu_entry_and_return(home_screen, menu_key):
    driver = home_screen
    wait = WebDriverWait(driver, WAIT_SECONDS)
    menu = MENUS[menu_key]

    required = [
        HOME_LOGO,
        QUICKMENU_AREA,
        DESTINATION,
        menu["button"],
    ]
    if any(not value.strip() for value in required):
        pytest.fail(
            "로케이터를 입력해 주세요.",
            pytrace=False,
        )

    def visible(xpath):
        return wait.until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    assert visible(HOME_LOGO).is_displayed()
    assert visible(QUICKMENU_AREA).is_displayed()

    wait.until(
        EC.element_to_be_clickable((By.XPATH, menu["button"]))
    ).click()

    assert visible(DESTINATION).is_displayed()

    if menu_key == "vip_pick":
        destination = visible(DESTINATION)
        assert destination.text == "VIP PICK", "목적지 제목이 vip pick와 다릅니다."

    driver.back()

    assert wait.until(
        EC.invisibility_of_element_located((By.XPATH, DESTINATION))
    )
    assert visible(HOME_LOGO).is_displayed()
    assert visible(QUICKMENU_AREA).is_displayed()