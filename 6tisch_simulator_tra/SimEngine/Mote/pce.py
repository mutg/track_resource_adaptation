"""
    Very simple and fake Path Computation Entity
"""

import MoteDefines as d
import random
import SimEngine

class PCE(object):
    CURRENT_SLOT = 1
    TRACK_CELL_NUM = 3

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
            cb  = self._buildOneTrack,
            uniqueTag = 'build_track',
            intraSlotOrder = d.INTRASLOTORDER_STARTSLOT
        )

    def _schedule_convergence_check(self):
        self.engine.scheduleAtAsn(
            asn = self.engine.asn + 1,
            cb = self._check_convergence,
            uniqueTag = 'check_convergence',
            intraSlotOrder = d.INTRASLOTORDER_STARTSLOT
        )

    def _check_convergence(self):
        if all((mote.id == 0 or mote.rpl.getPreferredParent() is not None) for mote in self.engine.motes):
            print "Converged at ", self.engine.asn
            # build track from mote 3 to sink
            # self._build_track(self.engine.motes[3])
            # enable critical app on mote 3
        else:
            self._schedule_convergence_check()

    def _get_most_hops_mote(self): 
        allmotes = {m.get_mac_addr():m  for m in self.engine.motes}

        motes_with_parents = list(filter(lambda m: m.rpl.getPreferredParent() is not None, 
            self.engine.motes
        ))

        # create sets
        parent_motes_set = set([allmotes[m.rpl.getPreferredParent()].id for m in motes_with_parents])
        motes_with_parents_set = set([m.id for m in motes_with_parents])

        non_parent_mote_ids = list(motes_with_parents_set.difference(parent_motes_set))

        # get mote with most hops to sink

        most_hops = None
        previous_hop_counter = 0
        for i in non_parent_mote_ids:
            m = self.engine.motes[i]
            source = m
            dest = None
            hop_counter = 0
            while True:
                dest = allmotes[source.rpl.getPreferredParent()]
                hop_counter += 1
                source = dest
                if dest is self.mote:
                    break

            if hop_counter > previous_hop_counter:
                most_hops = m
                previous_hop_counter = hop_counter
        
        return most_hops

    def _build_track_random(self, sourceMote):
        # build track from source mote to sink
        # need to loop through chain of RPL parents from source to destination
        # and add cell bundles

        # we need to build a list of motes keyed by mac-address first though
        allmotes = {m.get_mac_addr():m  for m in self.engine.motes}
        

        for mote in self.engine.motes:
            allmotes[mote.get_mac_addr()] = mote

        sender = sourceMote
        receiver = None

        # go through parent motes up to sink and add cell bundles
        while True:

            receiver = allmotes[sender.rpl.getPreferredParent()]
            
            bundle = self._get_random_available_cells_between_two_motes(sender, receiver, self.TRACK_CELL_NUM, 0)

            for cell in bundle:
                sender.tsch.addCell(
                    slotOffset       = cell[0],
                    channelOffset    = cell[1],
                    neighbor         = receiver.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_TX ],
                    trackId          = 0,
                    slotframe_handle = 0,
                )
                receiver.tsch.addCell(
                    slotOffset       = cell[0],
                    channelOffset    = cell[1],
                    neighbor         = sender.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_RX ],
                    trackId           = 0,
                    slotframe_handle = 0
                )
            
            sender = receiver
            if sender == self.mote:
                break
    
    def _build_track(self, sourceMote):
        # need to loop through chain of RPL parents from source to destination
        # and add cell bundles

        # we need to build a list of motes keyed by mac-address first though
        allmotes = {m.get_mac_addr():m  for m in self.engine.motes}
        
        for mote in self.engine.motes:
            allmotes[mote.get_mac_addr()] = mote

        sender = sourceMote
        receiver = None

        # go through parent motes up to sink and add cell bundles
        available = self._get_available_slots_global()
        print "all: ", available
        while True:
            receiver = allmotes[sender.rpl.getPreferredParent()]

            slots = [available.pop(0) for _ in range(0, self.TRACK_CELL_NUM)]

            for slot in slots:
                chan = random.randint(0, self.engine.settings.phy_numChans - 1)
                sender.tsch.addCell(
                    slotOffset       = slot,
                    channelOffset    = chan,
                    neighbor         = receiver.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_TX ],
                    trackId          = 0,
                    slotframe_handle = 0,
                )
                receiver.tsch.addCell(
                    slotOffset       = slot,
                    channelOffset    = chan,
                    neighbor         = sender.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_RX ],
                    trackId          = 0,
                    slotframe_handle = 0
                )
            
            sender = receiver
            if sender == self.mote:
                break

    def _buildTwoTracks(self):
        self._build_track_specified([3,2,1,0], 0, self.TRACK_CELL_NUM)
        self._build_track_specified([4,2], None)

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

    def _build_track_daisy_chain(self):
        mote_list = [3,2,1,0]
        availableslots = self._get_available_slots_global()
        for _ in range(0, self.TRACK_CELL_NUM):
            for idx, mote_id in enumerate(mote_list):
                if idx >= (len(mote_list)-1):
                    break

                sender = self.engine.motes[mote_id]
                receiver = self.engine.motes[mote_list[idx+1]]

                slot = availableslots.pop(0)
                chan = random.randint(0, self.engine.settings.phy_numChans-1)

                sender.tsch.addCell(
                    slotOffset       = slot,
                    channelOffset    = chan,
                    neighbor         = receiver.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_TX ],
                    trackId          = 0,
                    slotframe_handle = 0,
                )
                receiver.tsch.addCell(
                    slotOffset       = slot,
                    channelOffset    = chan,
                    neighbor         = sender.get_mac_addr(),
                    cellOptions      = [ d.CELLOPTION_RX ],
                    trackId          = 0,
                    slotframe_handle = 0
                )

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