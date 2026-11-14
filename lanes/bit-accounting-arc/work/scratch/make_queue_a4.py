"""Build the A4 queue files from the A2 ones: same commands; (1) pre-A4 reference-anchored local outputs and the
references are moved aside on the VM (kept in /root/runs/P1_superseded_A4, not deleted); (2) a job waits while the
same command is still running from the A2 queue (unaffected unrestricted/output cells keep running), then skips it
because its JSON exists; (3) --fixlam=... syntax (review r1 #7)."""
import os

Q = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/queue'
DONE = '/home/agent/workspaces/mats/work/bit-accounting-arc/gpu_src/queue_done'
WAIT = 'wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }'
MOVE = ('mkdir -p /root/runs/P1_superseded_A4/REF\n'
        'for f in /root/runs/P1/VR_*_local_*.json; do [ -e "$f" ] && mv "$f" /root/runs/P1_superseded_A4/; done\n'
        'for f in /root/runs/P1/REF/REF_*.json; do [ -e "$f" ] && mv "$f" /root/runs/P1_superseded_A4/REF/; done\n')


def src(name):
    p = os.path.join(Q, name)
    if not os.path.exists(p):
        p = os.path.join(DONE, name)
    return open(p).read()


s = src('21_eval.sh')
s = s.replace('# PREREG Part P1 evaluation runs (amendments A1, A2: restarted with AMAX 256 and fp32 linear paths; same '
              'commands as 10_eval.sh).',
              '# PREREG Part P1 evaluation runs (amendments A1-A4; same commands as 10_eval.sh; --fixlam=... syntax).')
a = 'nrun() { ps -eo args | grep -c "[r]un_vr.py\\|[r]ef_curve.py"; }'
assert a in s
s = s.replace(a, '# A4: outputs made with the pre-A4 Jacobian frame are moved aside (not deleted)\n' + MOVE + a + '\n' + WAIT)
a = 'run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_$VM.log 2>&1; }'
assert a in s
s = s.replace(a, 'run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_$VM.log 2>&1; }')
s = s.replace('--fixlam -2,-3.5,-5', '--fixlam=-2,-3.5,-5').replace('--fixlam -1,-2.5,-4', '--fixlam=-1,-2.5,-4')
assert '--fixlam=' in s
open(os.path.join(Q, '31_eval.sh'), 'w').write(s)

m = src('23_vmB_milestone.sh')
a = 'run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_milestone.log 2>&1; }'
assert a in m
m = m.replace(a, WAIT + '\nrun() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> '
              '$O/chain_milestone.log 2>&1; }\nsleep 60   # let 31_eval.sh move the pre-A4 outputs aside first')
m = m.replace('# VM B only: seed-4000 certificate runs', '# (A4 rerun) VM B only: seed-4000 certificate runs')
open(os.path.join(Q, '33_vmB_milestone.sh'), 'w').write(m)

h = src('24_h1.sh')
a = 'run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_h1_$VM.log 2>&1; }'
assert a in h
h = h.replace(a, WAIT + '\nrun() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> '
              '$O/chain_h1_$VM.log 2>&1; }\nsleep 60   # let 31_eval.sh move the pre-A4 outputs aside first')
h = h.replace('# Amendment A3:', '# Amendment A3 (rerun after A4):')
open(os.path.join(Q, '34_h1.sh'), 'w').write(h)

e = src('22_vm1_early.sh')
e = e.replace('# VM 1 only: run two cells', '# (A4) VM 1 only: run two cells')
open(os.path.join(Q, '32_vm1_early.sh'), 'w').write(e)
for f in ('31_eval.sh', '32_vm1_early.sh', '33_vmB_milestone.sh', '34_h1.sh'):
    os.chmod(os.path.join(Q, f), 0o755)
print('ok')
