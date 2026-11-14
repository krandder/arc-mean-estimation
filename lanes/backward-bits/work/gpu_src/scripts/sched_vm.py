"""Run jobs with dependencies on P workers (VM-side). Jobs file: JSON list of {id, cmd, deps}, in priority order.
A job starts when all its deps finished with exit 0; jobs whose deps failed are skipped. Logs: <logdir>/<id>.log and
<logdir>/sched.log. usage: python sched.py jobs.json P logdir"""
import json
import os
import subprocess
import sys
import time

jobs = json.load(open(sys.argv[1]))
P = int(sys.argv[2])
logd = sys.argv[3]
os.makedirs(logd, exist_ok=True)
slog = open(os.path.join(logd, 'sched.log'), 'a')


def log(msg):
    slog.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + ' ' + msg + '\n')
    slog.flush()


done, failed, running = set(), set(), {}
pending = list(jobs)
log(f'start: {len(jobs)} jobs, P={P}')
while pending or running:
    for jid, (proc, t0, fh) in list(running.items()):
        rc = proc.poll()
        if rc is not None:
            fh.close()
            del running[jid]
            (done if rc == 0 else failed).add(jid)
            log(f'end {jid} rc={rc} {time.time() - t0:.0f}s')
    for j in [j for j in pending if any(d in failed for d in j['deps'])]:
        pending.remove(j)
        failed.add(j['id'])
        log(f"skip {j['id']} (a dependency failed)")
    while len(running) < P:
        ready = [j for j in pending if all(d in done for d in j['deps'])]
        if not ready:
            break
        j = ready[0]
        pending.remove(j)
        fh = open(os.path.join(logd, f"{j['id']}.log"), 'w')
        running[j['id']] = (subprocess.Popen(j['cmd'], shell=True, stdout=fh, stderr=subprocess.STDOUT), time.time(), fh)
        log(f"start {j['id']}")
    time.sleep(5)
log(f'all done: {len(done)} ok, {len(failed)} failed')
