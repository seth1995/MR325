from normal_device import Element


class MOS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def isMOS():
        return True

    def ErrorOK(self, var):
        dd = self.dd
        ss = self.ss
        gg = self.gg
        G = var.G
        U = var.U
        x = var.x
        if dd != -1 and ss != -1:
            vds = x[dd, 0] - x[ss, 0]
        elif dd == -1 and ss != -1:
            vds = -x[ss, 0]
        elif dd != -1 and ss == -1:
            vds = x[dd, 0]
        else:
            vds = 0

        if gg != -1 and ss != -1:
            vgs = x[gg, 0] - x[ss, 0]
        elif gg == -1 and ss != -1:
            vgs = -x[ss, 0]
        elif gg != -1 and ss == -1:
            vgs = x[gg, 0]
        else:
            vgs = 0

        deta_vgs = abs(vgs - self.vgs)
        deta_vds = abs(vds - self.vds)
        # print "debug",var.DC_Ele.value
        # print deta_vds
        # print deta_vgs

        if deta_vgs < var.MOS_abError and \
                deta_vds < var.MOS_abError:
            return True
        else:
            return False

    def getVds(self, var):
        dd = self.dd
        ss = self.ss
        x = var.x
        if dd != -1 and ss != -1:
            self.vds = x[dd, 0] - x[ss, 0]
        elif dd == -1 and ss != -1:
            self.vds = -x[ss, 0]
        elif dd != -1 and ss == -1:
            self.vds = x[dd, 0]
        else:
            self.vds = 0

    def getVgs(self, var):
        ss = self.ss
        gg = self.gg
        x = var.x
        if gg != -1 and ss != -1:
            self.vgs = x[gg, 0] - x[ss, 0]
        elif gg == -1 and ss != -1:
            self.vgs = -x[ss, 0]
        elif gg != -1 and ss == -1:
            self.vgs = x[gg, 0]
        else:
            self.vgs = 0

    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+"
        self.I = 0
        Node_list = var.Node_list
        Element.getDevice(self, pat, var)
        self.D = int(self.word_set[0])
        self.G = int(self.word_set[1])
        self.S = int(self.word_set[2])
        self.W = eval(self.word_set[3])
        self.L = eval(self.word_set[4])
        self.vds = 0
        self.vgs = 0
        #self.VTH = 0.7
        #self.K = 3.835e-4
        Node_list = var.Node_list
        if self.D == 0:
            self.dd = -1
        elif self.D in Node_list:
            self.dd = Node_list.index(self.D)
        else:
            self.dd = len(Node_list)
            Node_list.append(self.D)
            var.node_counter += 1

        if self.G == 0:
            self.gg = -1
        elif self.G in Node_list:
            self.gg = Node_list.index(self.G)
        else:
            self.gg = len(Node_list)
            Node_list.append(self.G)
            var.node_counter += 1
        if self.S == 0:
            self.ss = -1
        elif self.S in Node_list:
            self.ss = Node_list.index(self.S)
        else:
            self.ss = len(Node_list)
            Node_list.append(self.S)
            var.node_counter += 1

    def printMOS(self):
        print self.type
        print "D", self.D
        print "G", self.G
        print "S", self.S
        print "dd", self.dd
        print "gg", self.gg
        print "ss", self.ss
        print "K", self.K
        print "VTH", self.VTH


class NMOS(MOS):
    def __init__(self, *av):

        MOS.__init__(self, *av)

    def getDevice(self, var):
        self.VTH = 0.7
        self.K = 3.835e-4
        self.type = "NMOS"
        self.vds = 0.1
        self.vgs = 0
        self.lam = 0.1
        MOS.getDevice(self, var)

    def Stamp(self, var):
        dd = self.dd
        gg = self.gg
        ss = self.ss
        G = var.G
        U = var.U
        gm = 0
        gds = 0
        vds = self.vds
        vgs = self.vgs
        Ids = 0
        kn = self.W / self.L * self.K * 0.5

        if (vgs > self.VTH) and (vds < (vgs - self.VTH)) and vds > 0:

            """
            gm=self.W/self.L*self.K*vds
            gds=self.W/self.L*self.K*(vgs-self.VTH-vds)
            Ids=self.W/self.L*self.K*((vgs-self.VTH)*vds-0.5*vds*vds)
            """
            self.state = "liner"

            gm = 2 * kn * vds * (1 + self.lam * vds)
            gds = 2 * kn * (vgs - self.VTH - vds) * (1 + self.lam * vds) + \
                self.lam * kn * (2 * (vgs - self.VTH) * vds - vds**2)

            Ids = kn * (2 * (vgs - self.VTH) * vds -
                        vds**2) * (1 + self.lam * vds)

        elif (vgs > self.VTH) and (vds < (vgs - self.VTH)) and vds < 0:
            gm = self.W / self.L * self.K * vds
            gds = self.W / self.L * self.K * (vgs - self.VTH - vds)
            Ids = self.W / self.L * self.K * \
                ((vgs - self.VTH) * vds - 0.5 * vds * vds)
          #  if (vds>0):
           #     I0*=(1+self.lam*vds)   #CLM
        elif (vds >= (vgs - self.VTH)) and (vgs > self.VTH) and vds > 0:
            """
            gds=0
            gm=self.W/self.L*self.K*(vgs-self.VTH)
            Ids=0.5*self.W/self.L*self.K*((vgs-self.VTH)*(vgs-self.VTH))
            """
            self.state = "sat."
            gds = kn * (vgs - self.VTH)**2 * self.lam
            gm = 2 * kn * (vgs - self.VTH) * (1 + self.lam * vds)
            Ids = kn * (vgs - self.VTH)**2 * (1 + self.lam * vds)
        elif (vds >= (vgs - self.VTH)) and (vgs > self.VTH) and vds < 0:
            gds = 0
            gm = self.W / self.L * self.K * (vgs - self.VTH)
            Ids = 0.5 * self.W / self.L * self.K * \
                ((vgs - self.VTH) * (vgs - self.VTH))

          #  I0 *= (1 + self.lam * vds)   #CLM
        I0 = Ids - gm * vgs - gds * vds
       # print "NMOS",Ids,I0
        if dd != -1:
            G[dd, dd] += gds
            if gg != -1:
                G[dd, gg] += gm
        if ss != -1:
            G[ss, ss] += gds + gm
            if gg != -1:
                G[ss, gg] -= gm
        if dd != -1 and ss != -1:
            G[dd, ss] -= gds + gm
            G[ss, dd] -= gds

        if dd != -1:
            U[dd, 0] -= I0
        if ss != -1:
            U[ss, 0] += I0
        """
        if I0<1e-3:
            print self.type

            print gm
            print gds
        """


class PMOS(MOS):
    def __init__(self, *av):

        MOS.__init__(self, *av)

    def getDevice(self, var):

        self.VTH = 0.8
        self.K = 7.67e-4
        self.type = "PMOS"
        MOS.getDevice(self, var)
        self.vds = -0.1
        self.vgs = 0
        self.lam = 0.2
        """
        self.VTH = 0.7
        self.K = 3.835e-4
        self.type = "PMOS"
        MOS.getDevice(self, var)
        self.vds = -0.1
        self.vgs = 0
        self.lam = 0.1
        """

    def Stamp(self, var):
        dd = self.dd
        gg = self.gg
        ss = self.ss
        G = var.G
        U = var.U

        gm = 0
        gds = 0
        vds = self.vds
        vgs = self.vgs
        vsd = -self.vds
        vsg = -self.vgs
        VTH = self.VTH
        I0 = 0
        ISD = 0
        self.state = "None"
        kp = self.W / self.L * self.K * 0.5
        '''
         #liner  PMOS
        if (abs(vgs)>abs(self.VTH)) and (abs(vds)<(abs(vgs)-abs(self.VTH))):
            gm=self.W/self.L*self.K*abs(vds)
            gds=self.W/self.L*self.K*(abs(vgs)-abs(self.VTH)-abs(vds))
            I0=-self.W/self.L*self.K*((abs(vgs)-abs(self.VTH))*abs(vds)-0.5*vds*vds)-gm*vgs-gds*vds
            print "liner"
            #CLM
            if vds<0:
                I0*=(1-self.lam*vds)

        elif (abs(vds)>=(abs(vgs)-abs(self.VTH))) and (abs(vgs)>abs(self.VTH)):
            gds=0
            gm=self.W/self.L*self.K*(abs(vgs)-abs(self.VTH))
            I0=-0.5*self.W/self.L*self.K*((abs(vgs)-abs(self.VTH))*(abs(vgs)-abs(self.VTH)))-gm*vgs-gds*vds
            #CLM
            print "sat"

            I0*=(1-self.lam*vds)
        '''
        if (vsg > self.VTH) and (vsd < (vsg - self.VTH)) and vsd > 0:
            """
            gm = self.W / self.L * self.K * vsd
            gds = self.W / self.L * self.K * (vsg - VTH - vsd)
            ISD=self.W / self.L * self.K * ((vsg - VTH) * vsd - 0.5 * vsd * vsd)
            """
            gm = 2 * kp * vsd * (1 + self.lam * vsd)

            gds = 2 * kp * (vsg - self.VTH - vsd) * (1 + self.lam * vsd) + \
                self.lam * kp * (2 * (vsg - self.VTH) * vsd - vsd ** 2)

            ISD = kp * (2 * (vsg - self.VTH) * vsd -
                        vsd ** 2) * (1 + self.lam * vsd)

            self.state = "liner"

            # if (vsd>0):
            #    I0*=(1+self.lam*vsd)   #CLM
        elif (vsg > self.VTH) and (vsd < (vsg - self.VTH)) and vsd < 0:
            gm = self.W / self.L * self.K * vsd
            gds = self.W / self.L * self.K * (vsg - VTH - vsd)
            ISD = self.W / self.L * self.K * \
                ((vsg - VTH) * vsd - 0.5 * vsd * vsd)
            self.state = "liner"
        elif (vsd >= (vsg - self.VTH)) and (vsg > self.VTH) and vsd > 0:
            """
            gds = 0
            gm = self.W / self.L * self.K * (vsg - VTH)
            ISD=0.5 * self.W / self.L * self.K * ((vsg - VTH) * (vsg -VTH))
            """
            self.state = "sat."
            gds = kp * (vsg - self.VTH)**2 * self.lam
            gm = 2 * kp * (vsg - self.VTH) * (1 + self.lam * vsd)
            ISD = kp * (vsg - self.VTH)**2 * (1 + self.lam * vsd)
        elif (vsd >= (vsg - self.VTH)) and (vsg > self.VTH) and vsd < 0:
            gds = 0
            gm = self.W / self.L * self.K * (vsg - VTH)
            ISD = 0.5 * self.W / self.L * self.K * ((vsg - VTH) * (vsg - VTH))
            # I0 *= (1 + self.lam * vsd)   #CLM
        I0 = ISD - gm * vsg - gds * vsd
        I0 = -I0
        # I0=-ISD-gm*vgs-gds*vds
        """
        print "debug"
        print "gm",gm
        print "gds",gds
        print "I0",I0
        print "vds",self.vds
        print "vgs",self.vgs
        print "ISD",ISD
        print "state",self.state
        """
        if dd != -1:
            G[dd, dd] += gds
            if gg != -1:
                G[dd, gg] += gm
        if ss != -1:
            G[ss, ss] += gds + gm
            if gg != -1:
                G[ss, gg] -= gm
        if dd != -1 and ss != -1:
            G[dd, ss] -= gds + gm
            G[ss, dd] -= gds

        if dd != -1:
            U[dd, 0] -= I0
        if ss != -1:
            U[ss, 0] += I0
        """
        if I0<1e-3:
            print self.type

            print gm
            print gds
        """
