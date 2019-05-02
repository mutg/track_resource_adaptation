import MoteDefines as d
import random
import SimEngine

class PCE(object):
    CURRENT_SLOT = 1
    TRACK_CELL_NUM = 2

    def __init__(self, mote):
        self.mote   = mote
        self.engine = SimEngine.SimEngine.SimEngine()
        self.settings = SimEngine.SimSettings.SimSettings()
        self.log    = SimEngine.SimLog.SimLog().log
        self._schedule_convergence_check()
        self._schedule_track_building()

    def receive_request(self, packet):
        pass

    def _schedule_track_building(self):
        self.engine.scheduleAtAsn(
            asn = self.settings.exec_startSend * 101,
            cb  = self._buildTwoTracks,
            uniqueTag = 'build_track',
            intraSlotOrder = d.INTRASLOTORDER_STARTSLOT
        )

    def _buildTwoTracks(self):
        self._build_track_specified([3,2,1,0], 0, self.TRACK_CELL_NUM)
        self._build_track_specified([4,2], 1, 2)

    def _buildOneTrack(self):
        self._build_track_specified([3,2,1, 0], 0, self.TRACK_CELL_NUM)

    def _build_track_specified(self, array, trackId, cellnum=1):
        for idx, mote_id in enumerate(array):
            if idx >= (len(array)-1):
                break

            sender = self.engine.motes[mote_id]
            receiver = self.engine.motes[array[idx+1]]
            
            for _ in range(0, cellnum):
                chan = random.randint(0, self.engine.settings.phy_numChans - 1)

                sender.tsch.addCell(
                    slotOffset       = self.CURRENT_SLOT,
                    channelOffset    = chan,
                    neighbor         = receiver.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_TX ],
                    trackId          = trackId,
                    slotframe_handle = 0,
                )
                receiver.tsch.addCell(
                    slotOffset       = self.CURRENT_SLOT,
                    channelOffset    = chan,
                    neighbor         = sender.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_RX ],
                    trackId          = trackId,
                    slotframe_handle = 0
                )
                self.CURRENT_SLOT += 1


    def _get_available_slots_global(self):
        busyslots = []
        for mote in self.engine.motes:
            for key in mote.tsch.slotframes: 
                slots = mote.tsch.slotframes[key].get_busy_slots()
                for slot in slots:
                    busyslots.append(slot)

        return list((set(range(self.engine.settings.tsch_slotframeLength))) - set(busyslots))

    def _get_random_available_cells_between_two_motes(self, sender, receiver, count=4, slotframe_handle=1):
        # first get a list of the available slots
        availableslots_sender = set(sender.tsch.get_available_slots(slotframe_handle))
        availableslots_receiver = set(receiver.tsch.get_available_slots(slotframe_handle))

        intersection = list(availableslots_sender.intersection(availableslots_receiver))
        
        randomCells = []
        for i in range(count):
            slot    = intersection[random.randint(0, len(intersection)-1)]
            intersection.remove(slot)
            channel = random.randint(0, self.engine.settings.phy_numChans-1)
            randomCells.append((slot, channel))

        return randomCells