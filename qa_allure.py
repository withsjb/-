"""Allure attachments and optional local log; never creates a device session."""
from datetime import datetime, timezone
from pathlib import Path
import json
import pytest
import allure

MAX_BYTES = 8_000_000


def pytest_addoption(parser):
    parser.addoption('--qa-observation-log',default=None,
                     help='Append source-time START/END lines to a local observation log')


def _event(item,kind,status=''):
    filename=item.config.getoption('--qa-observation-log')
    if not filename:return
    config=item.config
    config._qa_log_seq=getattr(config,'_qa_log_seq',0)+1
    at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    line=f'{at} seq={config._qa_log_seq} {kind} {item.nodeid}'+(f' {status}' if status else '')
    try:
        path=Path(filename);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('a',encoding='utf8') as stream:stream.write(line+'\n')
    except OSError as error:
        reporter=config.pluginmanager.getplugin('terminalreporter')
        if reporter:reporter.write_line(f'[QA log] {type(error).__name__}: {error}',yellow=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item,nextitem):
    item._qa_report_status='ERROR'
    _event(item,'START')
    yield
    _event(item,'END',item._qa_report_status)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome=yield
    report=outcome.get_result()
    if report.failed:item._qa_report_status='ERROR' if report.when!='call' else 'FAILED'
    elif report.skipped and getattr(item,'_qa_report_status','ERROR') not in ('FAILED',):
        item._qa_report_status='SKIPPED'
    elif report.when=='call' and report.passed:item._qa_report_status='PASSED'
    if report.when not in ('setup','call'):return
    driver=next((item.funcargs.get(name) for name in ('driver','home_screen','appium_driver')
                 if item.funcargs.get(name) is not None),None)
    if driver is None:return
    errors=[]
    for name,read,kind in [
        ('screen',lambda:driver.get_screenshot_as_png(),allure.attachment_type.PNG),
        ('hierarchy',lambda:driver.page_source,allure.attachment_type.XML)]:
        try:
            data=read()
            size=len(data.encode('utf8')) if isinstance(data,str) else len(data)
            if size>MAX_BYTES:raise ValueError('attachment exceeds 8 MB')
            allure.attach(data,name=f'{report.when}-{name}',attachment_type=kind)
        except Exception as error:
            errors.append({'attachment':name,'stage':report.when,'error':f'{type(error).__name__}: {str(error)[:300]}'})
    if errors:
        # Preserve original test verdict even when optional capture fails.
        try:allure.attach(json.dumps(errors,ensure_ascii=False),name='capture-diagnostics',attachment_type=allure.attachment_type.JSON)
        except Exception:pass
