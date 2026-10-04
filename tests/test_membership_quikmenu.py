# import pytest

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# WAIT_SECONDS = 20

# # 공통 로케이터 — 실제 값 입력
# HOME_LOGO = '//android.widget.ImageView[@content-desc="T 멤버십 홈"]'
# QUICKMENU_AREA = '//android.view.View[@resource-id="quickMenu"]'

# # 항목별 로케이터 — 실제 값 입력
# QUICKMENU_LOCATORS = {
#     "t_day": {
#         "button": '//android.view.View[@content-desc="T day"]',
#         "destination": '//android.widget.TextView[@resource-id="subHeaderTitle"]',
#     },
#     "vip_pick": {
#         "button": '//android.view.View[@content-desc="VIP PICK"]',
#         "destination": '//android.widget.TextView[@resource-id="subHeaderTitle"]',
#     },
#     "club": {
#         "button": '//android.view.View[@content-desc="클럽 멤버십"]',
#         "destination": '//android.widget.TextView[@resource-id="subHeaderTitle"]',
#     },
#     "long_term": {
#         "button": '//android.view.View[@content-desc="T 장기고객"]',
#         "destination": '//android.widget.TextView[@resource-id="subHeaderTitle"]',
#     },
# }


# def validate_locators(menu_key):
#     """빈 로케이터로 테스트가 실행되거나 성공 처리되지 않도록 확인."""
#     menu = QUICKMENU_LOCATORS[menu_key]

#     required = {
#         "HOME_LOGO": HOME_LOGO,
#         "QUICKMENU_AREA": QUICKMENU_AREA,
#         f"{menu_key}.button": menu["button"],
#         f"{menu_key}.destination": menu["destination"],
#     }

#     missing = [
#         name
#         for name, value in required.items()
#         if not value.strip()
#     ]

#     if missing:
#         pytest.fail(
#             "로케이터를 입력해 주세요: " + ", ".join(missing),
#             pytrace=False,
#         )

#     return menu


# @pytest.mark.parametrize(
#     "menu_key, menu_name",
#     [
#         pytest.param(
#             "t_day",
#             "T day",
#             id="TC_QM_01",
#         ),
#         pytest.param(
#             "vip_pick",
#             "VIP PICK",
#             id="TC_QM_02",
#         ),
#         pytest.param(
#             "club",
#             "클럽 멤버십",
#             id="TC_QM_03",
#         ),
#         pytest.param(
#             "long_term",
#             "T 장기고객",
#             id="TC_QM_04",
#         ),
#     ],
# )
# def test_quickmenu_entry_and_return(
#     home_screen,
#     menu_key,
#     menu_name,
# ):
#     """메인 → 퀵메뉴 → 목적지 진입 검증 → 메인 복귀 검증."""
#     driver = home_screen
#     wait = WebDriverWait(driver, WAIT_SECONDS)
#     menu = validate_locators(menu_key)

#     # 1. 메인 화면과 퀵메뉴 영역 확인
#     home_logo = wait.until(
#         EC.visibility_of_element_located(
#             (By.XPATH, HOME_LOGO)
#         ),
#         message="메인 로고가 표시되지 않았습니다.",
#     )
#     assert home_logo.is_displayed()

#     quickmenu = wait.until(
#         EC.visibility_of_element_located(
#             (By.XPATH, QUICKMENU_AREA)
#         ),
#         message="메인 퀵메뉴 영역이 표시되지 않았습니다.",
#     )
#     assert quickmenu.is_displayed()

#     # 2. 퀵메뉴 항목 클릭
#     menu_button = wait.until(
#         EC.element_to_be_clickable(
#             (By.XPATH, menu["button"])
#         ),
#         message=f"{menu_name} 퀵메뉴가 클릭 가능한 상태가 아닙니다.",
#     )
#     menu_button.click()

#     # 3. 목적지 화면 진입 확인
#     # 메인 화면에도 있는 같은 문구가 아닌,
#     # 목적지 화면만 식별하는 요소를 사용해야 합니다.
#     destination = wait.until(
#         EC.visibility_of_element_located(
#             (By.XPATH, menu["destination"])
#         ),
#         message=f"{menu_name} 목적지 화면 진입 확인 실패",
#     )
#     assert destination.is_displayed(), (
#         f"{menu_name} 목적지 식별 요소가 보이지 않습니다."
#     )

#     # 4. 메인 복귀
#     # 현재 뼈대는 Android 뒤로가기를 사용합니다.
#     # 앱에서 상단 뒤로가기/닫기 버튼을 눌러야 한다면
#     # 이 부분을 해당 버튼 클릭으로 변경하세요.
#     driver.back()

#     # 5. 목적지 화면 종료 확인
#     destination_closed = wait.until(
#         EC.invisibility_of_element_located(
#             (By.XPATH, menu["destination"])
#         ),
#         message=f"{menu_name} 목적지 화면이 종료되지 않았습니다.",
#     )
#     assert destination_closed

#     # 6. 메인 로고와 퀵메뉴 영역 재노출 확인
#     returned_logo = wait.until(
#         EC.visibility_of_element_located(
#             (By.XPATH, HOME_LOGO)
#         ),
#         message=f"{menu_name} 종료 후 메인 로고가 보이지 않습니다.",
#     )
#     assert returned_logo.is_displayed()

#     returned_quickmenu = wait.until(
#         EC.visibility_of_element_located(
#             (By.XPATH, QUICKMENU_AREA)
#         ),
#         message=f"{menu_name} 종료 후 퀵메뉴 영역이 보이지 않습니다.",
#     )
#     assert returned_quickmenu.is_displayed()