"""VIP PICK 검증 강도 비교. 기존 home_screen fixture와 수집 설정을 사용합니다."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECONDS = 20
HOME_LOGO = '//android.widget.ImageView[@content-desc="T 멤버십 홈"]'
QUICKMENU_AREA = '//android.view.View[@resource-id="quickMenu"]'
VIP_PICK_BUTTON = '//android.view.View[@content-desc="VIP PICK"]'
DESTINATION = '//*[@resource-id="subHeaderTitle"]'


def open_vip_pick(driver):
    """메인에서 VIP PICK으로 진입하고 제목 요소가 표시될 때까지 기다립니다."""
    wait = WebDriverWait(driver, WAIT_SECONDS)
    wait.until(EC.visibility_of_element_located((By.XPATH, HOME_LOGO)))
    wait.until(EC.visibility_of_element_located((By.XPATH, QUICKMENU_AREA)))
    wait.until(EC.element_to_be_clickable((By.XPATH, VIP_PICK_BUTTON))).click()
    return wait.until(
        EC.visibility_of_element_located((By.XPATH, DESTINATION)),
        message="목적지 제목 요소가 표시되지 않았습니다.",
    )


def return_to_home(driver):
    wait = WebDriverWait(driver, WAIT_SECONDS)
    driver.back()
    wait.until(EC.invisibility_of_element_located((By.XPATH, DESTINATION)))
    wait.until(EC.visibility_of_element_located((By.XPATH, HOME_LOGO)))
    wait.until(EC.visibility_of_element_located((By.XPATH, QUICKMENU_AREA)))


@pytest.mark.parametrize("tc_id", [pytest.param("TC_VIP_01", id="TC_VIP_01")])
def test_vip_pick_a(home_screen, tc_id):
    destination = open_vip_pick(home_screen)
    assert destination.is_displayed(), "목적지 제목 요소가 보이지 않습니다."
    return_to_home(home_screen)


@pytest.mark.parametrize("tc_id", [pytest.param("TC_VIP_02", id="TC_VIP_02")])
def test_vip_pick_b(home_screen, tc_id):
    destination = open_vip_pick(home_screen)
    assert destination.is_displayed(), "목적지 제목 요소가 보이지 않습니다."
    assert destination.text == "VIP PICK", "목적지 제목이 VIP PICK과 다릅니다."
    return_to_home(home_screen)
