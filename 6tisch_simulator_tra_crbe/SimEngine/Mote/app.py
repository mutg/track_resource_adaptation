"""
An application lives on each node
"""

# =========================== imports =========================================
from scipy.stats import poisson
from abc import abstractmethod
import random

# Mote sub-modules

# Simulator-wide modules
import SimEngine
import MoteDefines as d

import pce

# =========================== defines =========================================

# =========================== helpers =========================================

# =========================== body ============================================

def App(mote):
    """factory method for application
    """

    settings = SimEngine.SimSettings.SimSettings()

    # use mote.id to determine whether it is the root or not instead of using
    # mote.dagRoot because mote.dagRoot is not initialized when application is
    # instantiated
    if mote.id == 0:
        return AppRoot(mote)
    elif mote.id == 3:
        return AppCriticalTracked(mote)
    elif mote.id == 4:
        return AppPeriodicSlotFrame(mote)
    else:
        return globals()[settings.app](mote)

class AppBase(object):
    """Base class for Applications.
    """

    def __init__(self, mote, **kwargs):

        # store params
        self.mote       = mote

        # singletons (quicker access, instead of recreating every time)
        self.engine     = SimEngine.SimEngine.SimEngine()
        self.settings   = SimEngine.SimSettings.SimSettings()
        self.log        = SimEngine.SimLog.SimLog().log
        
        # local variables
        self.appcounter = 0

    #======================== public ==========================================

    @abstractmethod
    def startSendingData(self):
        """Starts the application process.

        Typically, this methods schedules an event to send a packet to the root.
        """
        raise NotImplementedError()  # abstractmethod

    def recvPacket(self, packet):
        """Receive a packet destined to this application
        """
        # log and mote stats
        self.log(
            SimEngine.SimLog.LOG_APP_RX,
            {
                '_mote_id': self.mote.id,
                'packet'  : packet
            }
        )

    #======================== private ==========================================

    def _generate_packet(
            self,
            dstIp,
            packet_type,
            packet_length,
        ):
        
        # create data packet
        dataPacket = {
            'type':              packet_type,
            'net': {
                'srcIp':         self.mote.get_ipv6_global_addr(),
                'dstIp':         dstIp,
                'packet_length': packet_length
            },
            'app': {
                'appcounter':    self.appcounter,
            }

        }

        # update appcounter
        self.appcounter += 1

        return dataPacket

    def _send_packet(self, dstIp, packet_length):
        
        # abort if I'm not ready to send DATA yet
        if self.mote.clear_to_send_EBs_DATA()==False:
            return
        
        # create
        packet = self._generate_packet(
            dstIp          = dstIp,
            packet_type    = d.PKT_TYPE_DATA,
            packet_length  = packet_length
        )
        
        # log
        self.log(
            SimEngine.SimLog.LOG_APP_TX,
            {
                '_mote_id':       self.mote.id,
                'packet':         packet,
            }
        )
        
        # send
        self.mote.sixlowpan.sendPacket(packet)

class AppRoot(AppBase):
    """Handle application packets from motes
    """
    # the payload length of application ACK
    APP_PK_LENGTH = 10

    def __init__(self, mote):
        super(AppRoot, self).__init__(mote)
        self.pce = pce.PCE(self.mote)
        

    #======================== public ==========================================

    def startSendingData(self):
        # nothing to schedule
        pass

    def recvPacket(self, packet):
        assert self.mote.dagRoot
        types = [d.PKT_TYPE_DATA, d.PKT_TYPE_DATA_TRACKED_CRITICAL, d.PKT_TYPE_DATA_TRACKED_BEFFORT]

        if packet['type'] in types:
            # log and update mote stats
            self.log(
                SimEngine.SimLog.LOG_APP_RX,
                {
                    '_mote_id': self.mote.id,
                    'packet'  : packet
                }
            )
        elif packet['type'] == "PCE_REQUEST":
            # send to pce
            self.pce.receive_request(packet)
            pass

    #======================== private ==========================================
    
    def _send_ack(self, destination, packet_length=None):

        if packet_length is None:
            packet_length = self.APP_PK_LENGTH

        self._send_packet(
            dstIp          = destination,
            packet_length  = packet_length
        )


class AppPeriodicSlotFrame(AppBase):

    def __init__(self, mote, **kwargs):
        super(AppPeriodicSlotFrame, self).__init__(mote)
        self.nextSend = self.settings.exec_startSend * 101
        self.TX_PERIOD = self.settings.beTxPeriod * 101
        self._schedule_transmission()
    
    def startSendingData(self):
        return

    def _schedule_transmission(self):
        self.engine.scheduleAtAsn(
            asn            = self.nextSend + random.randint(0, 10),
            cb             = self._send,
            uniqueTag      = "bepacket",
            intraSlotOrder = d.INTRASLOTORDER_ADMINTASKS
        )

    def _send(self):
        # create data packet
        packet = {
            'type':              d.PKT_TYPE_DATA,
            'net': {
                'srcIp':         self.mote.get_ipv6_global_addr(),
                'dstIp':         self.engine.motes[0].get_ipv6_global_addr(),
                'packet_length': self.settings.app_pkLength
            },
            'app': {
                'appcounter':    self.appcounter
            }

        }
        # update appcounter
        self.appcounter += 1 
            
        # log
        self.log(
            SimEngine.SimLog.LOG_APP_TX,
            {
                '_mote_id':       self.mote.id,
                'packet':         packet,
            }
        )
        
        # send  
        self.mote.sixlowpan.sendPacket(packet)
        self.nextSend += self.TX_PERIOD
        # resch
        self._schedule_transmission()

class AppCriticalTracked(AppBase):

    def __init__(self, mote, **kwargs):
        super(AppCriticalTracked, self).__init__(mote)
        self.trackID = 0

    def startSendingData(self):
        self._schedule_transmission()

    def _schedule_transmission(self):
        self.engine.scheduleAtAsn(
            asn            = self.engine.getAsn() + 1,
            cb             = self._send,
            uniqueTag      = "criticalpacket",
            intraSlotOrder = d.INTRASLOTORDER_ADMINTASKS
        )

    def _send(self):
        if self.engine.getAsn() >= self.settings.exec_startSend * 101:
            for _ in range(0, poisson.rvs(self.settings.crPktProb)):
                # OK to send
                # create data packet
                packet = {
                    'type':              d.PKT_TYPE_DATA_TRACKED_CRITICAL,
                    'net': {
                        'srcIp':         self.mote.get_ipv6_global_addr(),
                        'dstIp':         self.engine.motes[0].get_ipv6_global_addr(),
                        'packet_length': self.settings.app_pkLength
                    },
                    'app': {
                        'appcounter':    self.appcounter,
                        'track': self.trackID
                    }

                }
                
                
                # update appcounter
                self.appcounter += 1 
                    
                # log
                self.log(
                    SimEngine.SimLog.LOG_APP_TX,
                    {
                        '_mote_id':       self.mote.id,
                        'packet':         packet,
                    }
                )
                
                # send  
                self.mote.sixlowpan.sendPacket(packet)
        # resch
        self._schedule_transmission()
        


class AppPeriodic(AppBase):

    """Send a packet periodically

    Intervals are distributed uniformly between (pkPeriod-pkPeriodVar)
    and (pkPeriod+pkPeriodVar).

    The first timing to send a packet is randomly chosen between [next
    asn, (next asn + pkPeriod)].
    """

    def __init__(self, mote, **kwargs):
        super(AppPeriodic, self).__init__(mote)
        self.sending_first_packet = True

    #======================== public ==========================================

    def startSendingData(self):
        return
        if self.sending_first_packet:
            self._schedule_transmission()

    #======================== public ==========================================

    def _schedule_transmission(self):
        assert self.settings.app_pkPeriod >= 0
        if self.settings.app_pkPeriod == 0:
            return

        if self.sending_first_packet:
            # compute initial time within the range of [next asn, next asn+pkPeriod]
            delay = self.settings.tsch_slotDuration + (self.settings.app_pkPeriod * random.random())
            self.sending_first_packet = False
        else:
            # compute random delay
            assert self.settings.app_pkPeriodVar < 1
            delay = self.settings.app_pkPeriod * (1 + random.uniform(-self.settings.app_pkPeriodVar, self.settings.app_pkPeriodVar))

        # schedule
        self.engine.scheduleIn(
            delay           = delay,
            cb              = self._send_a_single_packet,
            uniqueTag       = (
                'AppPeriodic',
                'scheduled_by_{0}'.format(self.mote.id)
            ),
            intraSlotOrder  = d.INTRASLOTORDER_ADMINTASKS,
        )

    def _send_a_single_packet(self):
        if self.mote.rpl.dodagId == None:
            # it seems we left the dodag; stop the transmission
            self.sending_first_packet = True
            return

        self._send_packet(
            dstIp          = self.mote.rpl.dodagId,
            packet_length  = self.settings.app_pkLength
        )
        # schedule the next transmission
        self._schedule_transmission()

class AppBurst(AppBase):
    """Generate burst traffic to the root at the specified time (only once)
    """

    #======================== public ==========================================

    def startSendingData(self):
        # schedule app_burstNumPackets packets in app_burstTimestamp
        self.engine.scheduleIn(
            delay           = self.settings.app_burstTimestamp,
            cb              = self._send_burst_packets,
            uniqueTag       = (
                'AppBurst',
                'scheduled_by_{0}'.format(self.mote.id)
            ),
            intraSlotOrder  = d.INTRASLOTORDER_ADMINTASKS,
        )

    #======================== private ==========================================

    def _send_burst_packets(self):
        if self.mote.rpl.dodagId == None:
            # we're not part of the network now
            return

        for _ in range(0, self.settings.app_burstNumPackets):
            self._send_packet(
                dstIp         = self.mote.rpl.dodagId,
                packet_length = self.settings.app_pkLength
            )
