from appium.webdriver.common.appiumby import AppiumBy

# 첫 로그인 안내/권한 팝업 처리가 끝난 메인 화면 기준입니다.
# 아래 접근성 이름은 예시이므로 현재 앱의 실제 locator로 교체하세요.
# XPath 사용 예: (AppiumBy.XPATH, '//android.view.View[@content-desc="T 멤버십 홈"]')
HOME_LOGO = (AppiumBy.ID, "com.tms:id/mLogoImage")
MENU_OPEN = (AppiumBy.ID, "com.tms:id/mMenuButton")
MENU_CLOSE = (AppiumBy.ID, "com.tms:id/mLoginClose")