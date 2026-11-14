#!/bin/bash
cd /home/agent/workspaces/mats/work/moment-matching
until grep -q "relu_L2_net0" runs/cg_n6_d6.log; do sleep 30; done
P=$(ps -eo pid,args | grep "[c]g.py --n 6 --d 6 --only relu_L1_net0" | awk '{print $1}')
[ -n "$P" ] && kill $P
