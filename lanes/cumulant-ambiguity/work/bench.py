import numpy as np, lw, time, sys
from scipy.optimize import linprog
n,L,d,N0,N1=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
rng=np.random.default_rng(0)
X=np.vstack([rng.standard_normal((N0,n)),lw.sample_extra(n,N1,rng)])
w0=np.zeros(len(X));w0[:N0]=1/N0
Ws,a,_=lw.make_net(n,L,0,np.random.default_rng(99).standard_normal((1<<16,n)))
hs,f=lw.forward(X,Ws,a); sd=np.sqrt(w0@(f-w0@f)**2)
t=time.time();A,b,r,nf=lw.constraint_matrix(hs,list(range(L)),d,w0);print('rank',r,'build',time.time()-t,flush=True)
for m in sys.argv[6:]:
  t=time.time();res=[linprog(s*f,A_eq=A,b_eq=b,bounds=(0,None),method=m) for s in (-1,1)]
  print(m,[x.status for x in res],(-res[0].fun-res[1].fun)/sd,time.time()-t,flush=True)
