# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# import settings
# import locator


# # def test_tc01_home(home_screen, qa_observer):
# #     """TC01: 대상 앱 실행 및 메인 로고 노출 확인."""
# #     driver = home_screen

# #     qa_observer.attach(driver, coverage="partial")

# #     with qa_observer.step(
# #         "메인 화면 확인",
# #         screen="메인",
# #         state="기본상태",
# #     ):
# #         with qa_observer.check(
# #             "app.foreground",
# #             "대상 앱이 전면에 표시됨",
# #             settings.APP_PACKAGE,
# #         ) as record:
# #             actual = driver.current_package
# #             record["actual"] = actual

# #             assert actual == settings.APP_PACKAGE, (
# #                 "대상 앱이 전면에 없습니다."
# #             )

# #         with qa_observer.check(
# #             "home.logo",
# #             "메인 로고 노출",
# #             True,
# #         ) as record:
# #             actual = driver.find_element(
# #                 *locator.HOME_LOGO
# #             ).is_displayed()

# #             record["actual"] = actual
# #             assert actual, "메인 로고 미노출"

# def test_tc02_menu_open_close(home_screen, qa_web_observer):
#     """TC02: 전체메뉴 열기 → 닫기 → 메인 복귀 확인."""
#     driver = home_screen
#     wait = WebDriverWait(driver, settings.WAIT_SECONDS)
#     obs = qa_web_observer

#     # 웹 버전은 coverage 인자를 받지 않습니다.
#     obs.attach(driver)

#     with obs.step("전체메뉴 열기", screen="메인"):
#         open_button = wait.until(
#             EC.element_to_be_clickable(locator.MENU_OPEN)
#         )

#         # 반환된 행동 ID로 이후 검증을 연결합니다.
#         open_action_id = obs.action(
#             "click",
#             "menu.open",
#             lambda: open_button.click(),
#         )

#     with obs.step("전체메뉴 확인 및 닫기", screen="전체메뉴"):

#         def verify_menu_open():
#             close_button = wait.until(
#                 EC.element_to_be_clickable(locator.MENU_CLOSE),
#                 message="전체메뉴 닫기 버튼이 나타나지 않았습니다.",
#             )
#             return close_button.is_displayed()

#         # 웹 버전 check는 검증 함수를 받아 직접 실행합니다.
#         obs.check(
#             open_action_id,
#             "전체메뉴 닫기 버튼 노출",
#             verify_menu_open,
#         )

#         # 화면이 안정된 뒤 추가 근거를 수집합니다.
#         obs.capture("전체메뉴 표시 완료")

#         close_action_id = obs.action(
#             "click",
#             "menu.close",
#             lambda: wait.until(
#                 EC.element_to_be_clickable(locator.MENU_CLOSE)
#             ).click(),
#         )

#     with obs.step(
#         "전체메뉴 종료 및 메인 복귀 확인",
#         screen="메인",
#     ):

#         def verify_home_return():
#             closed = wait.until(
#                 EC.invisibility_of_element_located(
#                     locator.MENU_CLOSE
#                 ),
#                 message="전체메뉴가 닫히지 않았습니다.",
#             )

#             logo = wait.until(
#                 EC.visibility_of_element_located(
#                     locator.HOME_LOGO
#                 ),
#                 message="전체메뉴 종료 후 메인 로고 미노출",
#             )

#             return bool(closed and logo.is_displayed())

#         obs.check(
#             close_action_id,
#             "전체메뉴 종료 및 메인 로고 노출",
#             verify_home_return,
#         )

#         obs.capture("메인 복귀 완료")

# def test_TC_QM_01_quic_menu_Tday(home_screen, qa_web_observer):
#     """TC02: 전체메뉴 열기 → 닫기 → 메인 복귀 확인."""
#     driver = home_screen
#     wait = WebDriverWait(driver, settings.WAIT_SECONDS)
#     obs = qa_web_observer

#     # 웹 버전은 coverage 인자를 받지 않습니다.
#     obs.attach(driver)

#     with obs.step("전체메뉴 열기", screen="메인"):
#         open_button = wait.until(
#             EC.element_to_be_clickable(locator.MENU_OPEN)
#         )

#         # 반환된 행동 ID로 이후 검증을 연결합니다.
#         open_action_id = obs.action(
#             "click",
#             "menu.open",
#             lambda: open_button.click(),
#         )

#     with obs.step("전체메뉴 확인 및 닫기", screen="전체메뉴"):

#         def verify_menu_open():
#             close_button = wait.until(
#                 EC.element_to_be_clickable(locator.MENU_CLOSE),
#                 message="전체메뉴 닫기 버튼이 나타나지 않았습니다.",
#             )
#             return close_button.is_displayed()

#         # 웹 버전 check는 검증 함수를 받아 직접 실행합니다.
#         obs.check(
#             open_action_id,
#             "전체메뉴 닫기 버튼 노출",
#             verify_menu_open,
#         )

#         # 화면이 안정된 뒤 추가 근거를 수집합니다.
#         obs.capture("전체메뉴 표시 완료")

#         close_action_id = obs.action(
#             "click",
#             "menu.close",
#             lambda: wait.until(
#                 EC.element_to_be_clickable(locator.MENU_CLOSE)
#             ).click(),
#         )

#     with obs.step(
#         "전체메뉴 종료 및 메인 복귀 확인",
#         screen="메인",
#     ):

#         def verify_home_return():
#             closed = wait.until(
#                 EC.invisibility_of_element_located(
#                     locator.MENU_CLOSE
#                 ),
#                 message="전체메뉴가 닫히지 않았습니다.",
#             )

#             logo = wait.until(
#                 EC.visibility_of_element_located(
#                     locator.HOME_LOGO
#                 ),
#                 message="전체메뉴 종료 후 메인 로고 미노출",
#             )

#             return bool(closed and logo.is_displayed())

#         obs.check(
#             close_action_id,
#             "전체메뉴 종료 및 메인 로고 노출",
#             verify_home_return,
#         )

#         obs.capture("메인 복귀 완료")