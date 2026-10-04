"""Optional pytest bridge: stdlib + the customer's pytest only.

Register from root conftest.py and keep `python -m pytest ...` commands.
Uses an already-created driver on pytest's thread; never creates an Appium session.
Screenshot/XML read commands add latency. Command-boundary capture is opt-in.
The observer HTTP timeout applies only to sending events. Appium read commands
use the customer's existing driver transport timeout; no thread or hard timeout
is injected. The current context is read, never switched.
"""
import base64
import json
import math
import os
from pathlib import Path
import sys
import time
import urllib.request
from urllib.parse import urlparse
import uuid

import pytest

PLUGIN_NAME = "qa_external_bridge"
MAX_IMAGE_BYTES = 600_000
MAX_XML_CHARS = 120_000
MAX_XML_JSON_BYTES = 180_000
MAX_BODY_BYTES = 1_000_000
CAPTURE_PHASES = frozenset(("setup_complete", "call_start", "call_end"))
CAPTURE_COMMANDS = frozenset(("clickElement", "goBack", "forward"))
_MISSING = object()


class ObserverBridge:
    def __init__(self, connection_path, *, capture_phases=("setup_complete", "call_end"),
                 driver_fixtures=("home_screen", "driver", "appium_driver"),
                 max_captures=120, timeout=2.0, capture_after_commands=False,
                 max_command_captures=6):
        self.connection_path = Path(connection_path).expanduser()
        self.capture_phases = frozenset(capture_phases) & CAPTURE_PHASES
        self.driver_fixtures = tuple(driver_fixtures)
        self.max_captures = max(0, int(max_captures))
        self.timeout = max(0.1, min(float(timeout), 10.0))
        self.capture_after_commands = bool(capture_after_commands)
        self.max_command_captures = max(0, int(max_command_captures))
        self.session_id = uuid.uuid4().hex
        self.seq = 0
        self.disabled = False
        self.parallel = False
        self.warned = False
        self.capture_count = 0
        self.command_capture_count = 0
        self._capturing = False
        self.active_nodeid = None
        self.config = None
        self.connection = None
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _disable(self, reason):
        self.disabled = True
        if self.warned:
            return
        self.warned = True
        # warnings.warn could fail a customer test under -W error; use terminal only.
        message = "[QA observer] 관찰 연결을 중단했습니다. pytest는 계속 실행합니다. " + reason
        try:
            self.config.get_terminal_writer().line(message, yellow=True)
        except Exception:
            try:
                print(message, file=sys.stderr)
            except Exception:
                pass

    def _load_connection(self):
        try:
            with self.connection_path.open("rb") as stream:
                raw = stream.read(16_385)
            if len(raw) > 16_384:
                raise ValueError("connection file too large")
            data = json.loads(raw)
            url = data["url"].rstrip("/")
            parsed = urlparse(url)
            if (parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1")
                    or parsed.username or parsed.password or parsed.path or parsed.query
                    or parsed.fragment or not parsed.port):
                raise ValueError("local HTTP URL with port required")
            token = data["token"]
            if not isinstance(token, str) or not 1 <= len(token) <= 4096 or "\n" in token or "\r" in token:
                raise ValueError("invalid observer token")
            self.connection = {"url": url, "token": token}
        except Exception as exc:
            self._disable("연결 파일 확인: " + type(exc).__name__)

    def send(self, kind, **fields):
        if self.disabled or self.connection is None:
            return False
        try:
            payload = dict(session=self.session_id, seq=self.seq + 1, pid=os.getpid(), kind=kind, **fields)
            raw = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
            if len(raw) > MAX_BODY_BYTES:
                raise ValueError("event exceeds transfer limit")
            request = urllib.request.Request(
                self.connection["url"] + "/api/probe", raw,
                {"Content-Type": "application/json", "Authorization": "Bearer " + self.connection["token"]},
            )
            with self.opener.open(request, timeout=self.timeout) as response:
                result = json.loads(response.read(65_537))
            if not isinstance(result, dict) or not result.get("run_id"):
                raise ValueError("observer acknowledgement missing")
            self.seq += 1
            return True
        except Exception as exc:
            # Never resume after a possibly lost boundary. Later attribution is unsafe.
            self._disable("전송 오류: " + type(exc).__name__)
            return False

    def pytest_sessionstart(self, session):
        self.config = session.config
        if hasattr(session.config, "workerinput"):
            self._disable("xdist 작업자에서는 관찰하지 않습니다. 순차 실행을 사용하세요.")
            return
        self.parallel = bool(session.config.getoption("numprocesses", default=0))
        self._load_connection()
        self.send("session_start", parallel=self.parallel, runtime_context={})

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item, nextitem):
        enabled = not self.disabled and not self.parallel
        self.command_capture_count = 0
        if enabled and self.send("test_start", nodeid=item.nodeid):
            self.active_nodeid = item.nodeid
        try:
            yield
        finally:
            if enabled and self.active_nodeid == item.nodeid:
                self.send("test_end", nodeid=item.nodeid)
            self.active_nodeid = None

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_call(self, item):
        self._capture(item, "call_start")
        restore = self._wrap_driver(item)
        try:
            yield
        finally:
            restore()

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_makereport(self, item, call):
        result = yield
        report = result.get_result()
        if report.when == "setup" and report.passed:
            self._capture(item, "setup_complete")
        elif report.when == "call":
            self._capture(item, "call_end")

    def pytest_runtest_logreport(self, report):
        if self.parallel or self.active_nodeid != report.nodeid:
            return
        duration = float(report.duration)
        self.send("test_report", nodeid=report.nodeid, phase=report.when,
                  outcome=report.outcome, wasxfail=str(getattr(report, "wasxfail", ""))[:500],
                  wasxfail_present=hasattr(report, "wasxfail"),
                  duration=duration if math.isfinite(duration) and duration >= 0 else 0.0)

    def pytest_sessionfinish(self, session, exitstatus):
        self.send("session_end", exit_code=int(exitstatus))

    def _find_driver(self, item):
        # funcargs contains resolved fixtures. Never call getfixturevalue to create one.
        for name in self.driver_fixtures:
            driver = item.funcargs.get(name)
            if driver is not None and callable(getattr(driver, "get_screenshot_as_png", None)):
                return driver
        return None

    def _wrap_driver(self, item):
        def noop():
            pass
        if (self.disabled or self.parallel or not self.capture_after_commands
                or self.active_nodeid != item.nodeid):
            return noop
        try:
            driver = self._find_driver(item)
            original = getattr(driver, "execute", None)
            if driver is None or not callable(original):
                return noop
            previous = vars(driver).get("execute", _MISSING)

            def execute(command, *args, **kwargs):
                # Original return/exception and command arguments are preserved.
                result = original(command, *args, **kwargs)
                if (command in CAPTURE_COMMANDS and not self._capturing
                        and not self.disabled and self.command_capture_count < self.max_command_captures):
                    self.command_capture_count += 1
                    self._capture(item, "after_command", command=command)
                return result

            driver.execute = execute

            def restore():
                try:
                    if driver.execute is execute:
                        if previous is _MISSING:
                            del driver.execute
                        else:
                            driver.execute = previous
                except Exception as exc:
                    self._disable("드라이버 관찰 해제 오류: " + type(exc).__name__)
            return restore
        except Exception as exc:
            self._disable("드라이버 관찰 연결 오류: " + type(exc).__name__)
            return noop

    def _capture(self, item, phase, command=""):
        if (self.disabled or self.parallel or self._capturing
                or (phase not in self.capture_phases and not (phase == "after_command" and self.capture_after_commands))
                or self.active_nodeid != item.nodeid or self.capture_count >= self.max_captures):
            return
        self._capturing = True
        try:
            driver = self._find_driver(item)
            if driver is None:
                return
            self.capture_count += 1
            evidence = self._read_evidence(driver, phase)
            evidence["command"] = command
            self.send("evidence", nodeid=item.nodeid, phase=phase, evidence=evidence)
        except Exception as exc:
            self._disable("화면 자료 수집 오류: " + type(exc).__name__)
        finally:
            self._capturing = False

    @staticmethod
    def _read_evidence(driver, phase):
        evidence = {
            "origin": "pytest_driver", "phase": phase, "image_format": "png",
            "image_base64": "", "image_status": "unavailable", "xml": "",
            "xml_status": "unavailable", "serial": "", "driver_context": "unknown",
            "capture_started": time.time(),
        }
        try:
            capabilities = driver.capabilities
            if isinstance(capabilities, dict):
                for key in ("udid", "appium:udid", "deviceUDID"):
                    value = capabilities.get(key)
                    if isinstance(value, str) and value:
                        evidence["serial"] = value[:200]
                        break
        except Exception:
            pass
        try:
            context = driver.current_context
            if isinstance(context, str) and context:
                evidence["driver_context"] = context[:200]
        except Exception:
            pass
        try:
            png = driver.get_screenshot_as_png()
            if not isinstance(png, (bytes, bytearray)) or not png.startswith(b"\x89PNG\r\n\x1a\n"):
                evidence["image_status"] = "error"
            elif len(png) > MAX_IMAGE_BYTES:
                evidence["image_status"] = "too_large"
            else:
                evidence["image_base64"] = base64.b64encode(png).decode("ascii")
                evidence["image_status"] = "ok"
        except Exception:
            evidence["image_status"] = "error"
        evidence["capture_finished"] = time.time()
        evidence["xml_started"] = time.time()
        try:
            xml = driver.page_source
            if not isinstance(xml, str) or not xml.strip():
                evidence["xml_status"] = "unavailable"
            elif (len(xml) > MAX_XML_CHARS
                  or len(json.dumps(xml, ensure_ascii=False).encode("utf-8")) > MAX_XML_JSON_BYTES):
                evidence["xml_status"] = "too_large"
            else:
                evidence["xml"] = xml
                evidence["xml_status"] = "ok"
        except Exception:
            evidence["xml_status"] = "error"
        evidence["xml_finished"] = time.time()
        return evidence


def register(config, connection_path, **options):
    """Register once from an existing pytest_configure; no pip entry point needed."""
    if config.pluginmanager.hasplugin(PLUGIN_NAME):
        return
    try:
        plugin = ObserverBridge(connection_path, **options)
        config.pluginmanager.register(plugin, PLUGIN_NAME)
    except Exception as exc:
        try:
            print("[QA observer] 등록하지 못했습니다. pytest는 계속 실행합니다: " + type(exc).__name__, file=sys.stderr)
        except Exception:
            pass
