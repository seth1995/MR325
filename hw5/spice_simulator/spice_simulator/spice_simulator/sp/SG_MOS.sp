*MOS  small signal

V1 4 0 2 
V3 1 4 0 sin 0 0.1 50MEG 0
R1 2 3 2k


V2 3 0 3
C1 2 0 0.001p
MN1 2 1 0 2 1

.tran TR 0 100n 10p
.END