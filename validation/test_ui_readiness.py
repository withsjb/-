"""Readiness regressions with fake UI; never opens a device session."""
from types import SimpleNamespace
import pytest
from selenium.common.exceptions import StaleElementReferenceException
from ui_readiness import HomeReady, authentication_state, check_authentication
import locator

class Element:
    def __init__(self,text='',visible=True,enabled=True):self.text=text;self.visible=visible;self.enabled=enabled
    def is_displayed(self):return self.visible
    def is_enabled(self):return self.enabled

class Driver:
    def __init__(self,entries):self.entries=entries
    def find_elements(self,*target):
        result=self.entries.get(target,[])
        if isinstance(result,Exception):raise result
        return result

def home():return Driver({target:[Element()] for target in (locator.HOME_LOGO,locator.MEMBERSHIP_TAB,locator.T_DAY,locator.HOME_SEARCH)})

def test_logo_only_is_not_home_ready():
    d=Driver({locator.HOME_LOGO:[Element()]})
    assert not HomeReady(0)(d)

def test_ready_requires_stability_and_resets_for_loading_and_stale_elements():
    d=home();clock=SimpleNamespace(now=0);condition=HomeReady(1,lambda:clock.now)
    assert not condition(d)
    clock.now=.5;assert not condition(d)
    d.entries[locator.LOADING_INDICATOR]=[Element()];clock.now=1;assert not condition(d)
    del d.entries[locator.LOADING_INDICATOR];clock.now=2;assert not condition(d)
    clock.now=3;assert condition(d) is d
    d.entries[locator.HOME_LOGO]=StaleElementReferenceException();assert not condition(d)

def test_login_requires_explicit_ui_indicators_and_policy_is_checked():
    d=home();assert authentication_state(d)=='unknown'
    d.entries[locator.USER_INFO]=[Element('회원님')];assert authentication_state(d)=='unknown'
    d.entries[locator.POINT_INFO]=[Element()];assert authentication_state(d)=='logged_in'
    assert check_authentication(d,'any')=='logged_in'
    with pytest.raises(AssertionError):check_authentication(d,'logged_out')
    d.entries[locator.USER_INFO]=[Element('로그인 해주세요')];assert check_authentication(d,'logged_out')=='logged_out'
    d.entries[locator.USER_INFO]=[Element('로그인 안내 회원님')];assert authentication_state(d)=='unknown'
    with pytest.raises(ValueError):check_authentication(d,'guest')
