#a circuit has diode
V1 0 1 0 SIN (0 1V 1kHz )
r2 1 2 1
d1 2 0 DNOM
d2 1 0 DNOM
c1 2 0 5p
*
.MODEL DNOM D(IS=1E-14)
*
.TRAN 10ns 10ms
.PRINT tran V(2) V(1)
.end
