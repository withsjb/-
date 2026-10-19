"""Run existing pytest tests and retain each run's local evidence separately."""
from datetime import datetime
from pathlib import Path
import argparse,json,shutil,subprocess,sys,uuid

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tc-csv',type=Path,help='Optional existing TC CSV copied beside Allure results')
    parser.add_argument('--observation-log',type=Path,help='Optional prepared live log path inside this project; existing lines are preserved')
    parser.add_argument('--prepare-log',action='store_true',help='Create only the selected observation log, without running pytest')
    args,pytest_args=parser.parse_known_args()
    if pytest_args[:1]==['--']:pytest_args=pytest_args[1:]
    if any(x.split('=')[0] in ('--alluredir','--clean-alluredir','--qa-observation-log','-o','--override-ini') for x in pytest_args):
        parser.error('Result paths and ini overrides are managed by this script. Run pytest directly for custom paths.')
    tc=args.tc_csv.expanduser().resolve() if args.tc_csv else None
    if tc and (not tc.is_file() or tc.suffix.lower()!='.csv'):parser.error('--tc-csv must reference an existing CSV')
    live=args.observation_log.expanduser().resolve() if args.observation_log else None
    if live and not live.is_relative_to(ROOT):parser.error('--observation-log must stay inside this project')
    if args.prepare_log:
        if not live:parser.error('--prepare-log requires --observation-log')
        live.parent.mkdir(parents=True,exist_ok=True);live.touch(exist_ok=True)
        print('OBSERVATION_LOG',live);return 0
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    folder=ROOT/'test-artifacts'/stamp;results=folder/'allure-results';results.mkdir(parents=True)
    log_path=live or folder/'observation.log';log_path.parent.mkdir(parents=True,exist_ok=True);log_path.touch(exist_ok=True)
    command=[sys.executable,'-m','pytest','-vv','--capture=tee-sys',
        '--alluredir',str(results),'--qa-observation-log',str(log_path),
        '-o','qa_capture_output='+str((folder/'qa-results').relative_to(ROOT)),*pytest_args]
    print('RESULT_DIR',folder,flush=True)
    with (folder/'pytest.log').open('w',encoding='utf8') as log:
        process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                 text=True,encoding='utf8',errors='replace',bufsize=1)
        try:
            for line in process.stdout:print(line,end='',flush=True);log.write(line);log.flush()
            code=process.wait()
        except KeyboardInterrupt:
            if process.poll() is None:process.terminate()
            code=process.wait()
    if tc:shutil.copy2(tc,results/'test_cases.csv')
    archive=shutil.make_archive(str(folder/'allure-results'),'zip',root_dir=results)
    summary={'exit_code':code,'command':command,'allure_results':str(results),
        'allure_zip':archive,'qa_zips':[str(p) for p in (folder/'qa-results').glob('*.zip')],
        'observation_log':str(log_path),'html_report_generated':False}
    (folder/'run-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return code


if __name__=='__main__':raise SystemExit(main())
