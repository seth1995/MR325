Example AC Analysis
v1 1 0 ac 1
r1 1 2 10k
r2 2 3 100k
c 2 3 10n
e1 3 0 0 2 1e8
.ac dec 10 1 1e4
.plot ac vdb(3)
.plot ac vp(3)
.end
