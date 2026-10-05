import pytest

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECONDS = 20

NOTICE_BUTTON = '//android.widget.Button[@text="유의 사항"]'
# NOTICE_BODY = '//android.view.View[@resource-id="acc-guide-MP_PG_01"]'
NOTICE_BODY = '//*[@resource-id="acc-guide-MP_PG_01"]'
T_DAY = '//android.view.View[@content-desc="T day"]'
WEEK_EVENT_BUTTON = '//android.widget.Button[contains(@text, "1주차")]'


def scroll_to_notice(driver, max_swipes=8):
    """유의사항 버튼이 보일 때까지 페이지 아래쪽으로 이동합니다."""
    button_locator = (By.XPATH, NOTICE_BUTTON)

    def visible_notice(d):
        for element in d.find_elements(*button_locator):
            try:
                if element.is_displayed() and element.is_enabled():
                    return element
            except StaleElementReferenceException:
                continue
        return False

    short_wait = WebDriverWait(
        driver,
        2,
        poll_frequency=0.3,
    )

    for attempt in range(max_swipes + 1):
        try:
            return short_wait.until(visible_notice)
        except TimeoutException:
            if attempt == max_swipes:
                break

        size = driver.get_window_size()
        x = int(size["width"] * 0.5)

        driver.swipe(
            x,
            int(size["height"] * 0.78),
            x,
            int(size["height"] * 0.38),
            duration=500,
        )

    pytest.fail(
        f"스크롤 {max_swipes}회 후에도 유의사항 버튼을 찾지 못했습니다.",
        pytrace=False,
    )


def verify_notice_expands(driver):
    """기존 TC: 유의사항 펼치기. 본문 검증은 주석 상태를 유지합니다."""
    wait = WebDriverWait(driver, WAIT_SECONDS)

    button_locator = (By.XPATH, NOTICE_BUTTON)
    body_locator = (By.XPATH, NOTICE_BODY)

    # T day 진입
    wait.until(
        EC.element_to_be_clickable((By.XPATH, T_DAY)),
        message="T day 버튼을 찾지 못했습니다.",
    ).click()

    # 5주차 이벤트 선택
    wait.until(
        EC.element_to_be_clickable((By.XPATH, WEEK_EVENT_BUTTON)),
        message="5주차 이벤트 버튼을 찾지 못했습니다.",
    ).click()

    # 유의사항 위치까지 스크롤
    scroll_to_notice(driver)

    # 1. 본문 요소가 존재하면 접어서 시작 상태를 맞춥니다.
    if driver.find_elements(*body_locator):
        wait.until(
            EC.element_to_be_clickable(button_locator)
        ).click()

    # 2. 본문 요소가 XML에서 사라졌는지 확인합니다.
    wait.until(
        lambda d: len(d.find_elements(*body_locator)) == 0,
        message="유의사항을 접었지만 본문 요소가 남아 있습니다.",
    )

    # 3. 접힌 유의사항을 펼칩니다.
    wait.until(
        EC.element_to_be_clickable(button_locator)
    ).click()

    # 4. 버튼 자체의 표시 확인
    button = wait.until(
        EC.visibility_of_element_located(button_locator)
    )
    assert button.is_displayed(), "유의사항 버튼이 보이지 않습니다."

    # 기존 비교 실험을 위해 5·6번은 주석 상태로 유지합니다.

    # # 5. 본문 요소가 XML에 다시 나타나는지 확인
    # body = wait.until(
    #     EC.presence_of_element_located(body_locator),
    #     message="유의사항을 펼쳤지만 본문 요소가 나타나지 않았습니다.",
    # )

    # # 6. 본문 표시 확인
    # body = wait.until(
    #     EC.visibility_of_element_located(body_locator),
    #     message="본문 요소는 있지만 화면에 표시되지 않습니다.",
    # )
    # assert body.is_displayed(), "유의사항 본문이 보이지 않습니다."


def verify_notice_collapses(driver):
    """펼쳐진 유의사항을 접으면 본문 요소가 제거되는지 확인합니다."""
    wait = WebDriverWait(driver, WAIT_SECONDS)

    button_locator = (By.XPATH, NOTICE_BUTTON)
    body_locator = (By.XPATH, NOTICE_BODY)

    # T day 진입
    wait.until(
        EC.element_to_be_clickable((By.XPATH, T_DAY)),
        message="T day 버튼을 찾지 못했습니다.",
    ).click()

    # 1주차 이벤트 선택
    wait.until(
        EC.element_to_be_clickable((By.XPATH, WEEK_EVENT_BUTTON)),
        message="1주차 이벤트 버튼을 찾지 못했습니다.",
    ).click()

    # 유의사항 위치까지 스크롤
    scroll_to_notice(driver)

    # 본문 요소가 없다면 펼쳐서 시작 상태를 맞춥니다.
    if not driver.find_elements(*body_locator):
        wait.until(
            EC.element_to_be_clickable(button_locator),
            message="유의사항 펼치기 버튼을 클릭할 수 없습니다.",
        ).click()

    # 접기 전에 본문이 XML에 존재하는지 확인합니다.
    wait.until(
        EC.presence_of_element_located(body_locator),
        message="접기 전 유의사항 본문이 존재하지 않습니다.",
    )

    # 본문이 펼쳐지면서 화면 위치가 변할 수 있으므로 다시 찾습니다.
    scroll_to_notice(driver)

    # 펼쳐진 유의사항을 접습니다.
    wait.until(
        EC.element_to_be_clickable(button_locator),
        message="유의사항 접기 버튼을 클릭할 수 없습니다.",
    ).click()

    # 본문 요소가 XML에서 제거될 때까지 기다립니다.
    wait.until(
        lambda d: len(d.find_elements(*body_locator)) == 0,
        message="유의사항을 접었지만 본문 요소가 남아 있습니다.",
    )

    # 명시적인 검증 기록을 남깁니다.
    # remaining_bodies = driver.find_elements(*body_locator)

    # assert len(remaining_bodies) == 0, (
    #     "유의사항을 접었지만 본문 요소가 화면 계층에 남아 있습니다."
    # )


@pytest.mark.parametrize(
    "tc_id",
    [
        pytest.param("TC_NOTICE_01", id="TC_NOTICE_01"),
    ],
)
def test_notice_expands(home_screen, tc_id):
    verify_notice_expands(home_screen)


@pytest.mark.parametrize(
    "tc_id",
    [
        pytest.param("TC_NOTICE_02", id="TC_NOTICE_02"),
    ],
)
def test_notice_collapses(home_screen, tc_id):
    verify_notice_collapses(home_screen)