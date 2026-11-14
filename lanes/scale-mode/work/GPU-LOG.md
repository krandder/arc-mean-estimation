# GPU-LOG

- 2026-11-02T11:41Z PENDING-CREATE vm=soup-gpu-scalemode-1-1102114114-28894 type=g2-standard-8 rate_usd_h=0.87 reserve_usd=2.26 group=scalemode run=scalemode-1 by=gpu-up.sh
- 2026-11-02T11:41Z CREATE vm=soup-gpu-scalemode-1-1102114114-28894 zone=us-west1-c type=g2-standard-8 gpu=1xnvidia-l4 model=SPOT max_run=6h rate_usd_h=0.87 (UNVERIFIED ceiling: on-demand list price, Billing API disabled; spot is lower) reserve_usd=2.26 spent_before_usd=0 group=scalemode run=scalemode-1 by=gpu-up.sh
- 2026-11-02T11:42Z READY vm=soup-gpu-scalemode-1-1102114114-28894 ip=34.168.238.119 gpu=NVIDIA L4, 580.178.04 startup=minimal 
- 2026-11-02T11:42Z RUN vm=soup-gpu-scalemode-1-1102114114-28894 timeout=2h cmd="bash -c export\ DEBIAN_FRONTEND=noninteractive\;\ apt-get\ update\ -q\ \>/dev/null\ \&\&\ apt-get\ install\ -y\ -q\ python3-venv\ python3-pip\ \>/dev/null\ \&\&"
- 2026-11-02T12:26Z RUN-END vm=soup-gpu-scalemode-1-1102114114-28894 rc=0
- 2026-11-02T12:27Z DELETE vm=soup-gpu-scalemode-1-1102114114-28894 zone=us-west1-c type=g2-standard-8 age_h=0.75 cost_usd=0.65 (rate ceiling x age) sync=skipped reason="gpu-run.sh finished rc=0: bash -c export\ DEBIAN_FRONTEND=noninteractive\;\ apt-get\ update\ -q\ \>/dev/nu"
- 2026-11-02T12:28Z PENDING-CREATE vm=soup-gpu-scalemode-2-1102122747-23229 type=g2-standard-8 rate_usd_h=0.87 reserve_usd=2.26 group=scalemode run=scalemode-2 by=gpu-up.sh
- 2026-11-02T12:28Z CREATE vm=soup-gpu-scalemode-2-1102122747-23229 zone=us-west1-c type=g2-standard-8 gpu=1xnvidia-l4 model=SPOT max_run=6h rate_usd_h=0.87 (UNVERIFIED ceiling: on-demand list price, Billing API disabled; spot is lower) reserve_usd=2.26 spent_before_usd=0.65 group=scalemode run=scalemode-2 by=gpu-up.sh
- 2026-11-02T12:28Z READY vm=soup-gpu-scalemode-2-1102122747-23229 ip=34.168.198.246 gpu=NVIDIA L4, 580.178.04 startup=minimal 
- 2026-11-02T12:29Z RUN vm=soup-gpu-scalemode-2-1102122747-23229 timeout=2h cmd="bash -c export\ DEBIAN_FRONTEND=noninteractive\;\ apt-get\ update\ -q\ \>/dev/null\ \&\&\ apt-get\ install\ -y\ -q\ python3-venv\ python3-pip\ \>/dev/null\ \&\&"
- 2026-11-02T12:57Z RUN-END vm=soup-gpu-scalemode-2-1102122747-23229 rc=0
- 2026-11-02T12:58Z DELETE vm=soup-gpu-scalemode-2-1102122747-23229 zone=us-west1-c type=g2-standard-8 age_h=0.50 cost_usd=0.43 (rate ceiling x age) sync=skipped reason="gpu-run.sh finished rc=0: bash -c export\ DEBIAN_FRONTEND=noninteractive\;\ apt-get\ update\ -q\ \>/dev/nu"
