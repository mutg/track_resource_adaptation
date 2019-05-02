"""
TRAE - Track Resource Adaptation Engine v01
"""
import sys
import SimEngine
from Printer import logPrint

class TRAE(object): 
    def __new__(cls, mote):
        settings    = SimEngine.SimSettings.SimSettings()
        class_name  = 'TRAE{0}'.format(settings.trae)
        return getattr(sys.modules[__name__], class_name)(mote)

class TRAEBase(object):

    def __init__(self, mote):
        self.mote = mote
        self.engine = SimEngine.SimEngine.SimEngine()
        self.track_has_packet_pending_rx = {}
        self.track_has_packet_pending_tx = {}
        self.track_rx_bundles = {}
        self.track_tx_bundles = {}

    def register_track_cell(self, cell):
        assert cell.trackId != None
        trackId = cell.trackId
        
        if cell.is_rx_on():
            if trackId not in self.track_rx_bundles:
                self.track_rx_bundles[trackId] = []      
                self.track_has_packet_pending_rx[trackId] = False
            self.track_rx_bundles[trackId].append(cell)
        elif cell.is_tx_on():
            if trackId not in self.track_tx_bundles:
                self.track_tx_bundles[trackId] = []      
                self.track_has_packet_pending_tx[trackId] = False      
            self.track_tx_bundles[trackId].append(cell)

        logPrint('Registered cell -> [slotOffset:', cell.slot_offset ,  "trackId: ", cell.trackId, '] on mote ', self.mote.id)

    def doSetPendingBit(self, cell):
        result = self.track_has_packet_pending_rx[cell.trackId] and not self._is_last_tx_cell(cell)
        return result

    def delete_track_cell(self, cell):
        """ assert cell.trackId != None """
        trackId = cell.trackId
        assert trackId in self.track_rx_bundles

        if cell in self.track_rx_bundles[trackId]:
            self.track_rx_bundles[trackId].remove(cell)

    def indicate_tx_cell_elapsed(self, cell):
        pass

    def indicate_acked_tx(self, cell, pending_bit):
        pass

    def indicate_non_acked_tx(self, cell):
        pass

    def indicate_idle_rx_cell(self, cell):
        pass

    def indicate_active_rx_cell(self, cell, pending_bit):
        pass

    def indicate_rx_cell_elapsed(self, cell):
        pass

    def get_has_packet_pending_rx(self, trackId):
        return self.track_has_packet_pending_rx[trackId]

    def get_has_packet_pending_tx(self, trackId):
        return self.track_has_packet_pending_tx[trackId]

    def _get_next_rx_cells(self, currentCell):
        cells = []
        for _cell in self.track_rx_bundles[currentCell.trackId]:
            if _cell.slot_offset > currentCell.slot_offset:
                cells.append(_cell)
        return cells

    def _is_first_rx_cell(self, cell):
        for _cell in self.track_rx_bundles[cell.trackId]:
            if cell.slot_offset > _cell.slot_offset:
                return False
        return True

    def _is_first_tx_cell(self, cell):
        for _cell in self.track_tx_bundles[cell.trackId]:
            if cell.slot_offset > _cell.slot_offset:
                return False
        return True

    def _get_next_tx_cells(self, currentCell):
        cells = []
        for _cell in self.track_tx_bundles[currentCell.trackId]:
            if _cell.slot_offset > currentCell.slot_offset:
                cells.append(_cell)
        return cells

    def _get_size_of_rx_bundle(self, trackId):
        return len(self.track_rx_bundles[trackId])

    def _get_index_of_cell(self, cell):
        bundle = self.track_rx_bundles[cell.trackId]
        return bundle.index(cell, 0)

    def _is_last_tx_cell(self, cell):
        for _cell in self.track_tx_bundles[cell.trackId]:
            if cell.slot_offset < _cell.slot_offset:
                return False
        return True

    def _is_last_rx_cell(self, cell):
        for _cell in self.track_rx_bundles[cell.trackId]:
            if cell.slot_offset < _cell.slot_offset:
                return False
        return True

class TRAEAllListenPendingBit(TRAEBase):

    def __init__(self, mote):
        super(TRAEAllListenPendingBit, self).__init__(mote)
        
    def indicate_tx_cell_elapsed(self, cell):
        if self._is_first_tx_cell(cell):
            for cell in self._get_next_tx_cells(cell):
                cell.set_send(True)

    def indicate_acked_tx(self, cell, pending_bit):
        self.track_has_packet_pending_tx[cell.trackId] = pending_bit
        logPrint('Acked TX on mote', self.mote.id, ', packet pending = ', pending_bit)
        for cell in self._get_next_tx_cells(cell):
            cell.set_send(pending_bit)

    def indicate_non_acked_tx(self, cell):
        logPrint('_____Non acked TX on mote', self.mote.id, ', packet pending = ', self.track_has_packet_pending_tx[cell.trackId])

    def indicate_idle_rx_cell(self, cell):
        if self._is_first_rx_cell(cell):
            """ Start of slotframe """
            _cells = self.track_rx_bundles[cell.trackId]
            for _cell in _cells:
                _cell.set_listen(True)
        elif self._is_last_rx_cell(cell):
            self.track_has_packet_pending_rx[cell.trackId] = False            

    def indicate_active_rx_cell(self, cell, pending_bit):
        # read the pending packet bit from packet
        pending_packet = pending_bit
        
        self.track_has_packet_pending_rx[cell.trackId] = pending_packet and self._is_last_rx_cell(cell) != True

        for _followingCell in self._get_next_rx_cells(cell):
            _followingCell.set_listen(pending_packet)

        logPrint('Received packet on mote ', self.mote.id,
        ' cell ', (self._get_index_of_cell(cell) + 1) ,'/', self._get_size_of_rx_bundle(cell.trackId), ' # pending_bit=',pending_packet)

class TRAEOneShotPendingBit(TRAEBase):

    def __init__(self, mote):
        super(TRAEOneShotPendingBit, self).__init__(mote)
        
    def indicate_acked_tx(self, cell, pending_bit):
        self.track_has_packet_pending_tx[cell.trackId] = pending_bit
        logPrint('Acked TX on mote', self.mote.id, ', pending packet = ', self.track_has_packet_pending_tx[cell.trackId])
        for cell in self._get_next_tx_cells(cell):
            cell.set_send(pending_bit)

    def indicate_non_acked_tx(self, cell):
        logPrint('!!!!Non acked TX on mote', self.mote.id, ', pending packet = ', self.track_has_packet_pending_tx[cell.trackId])
        for cell in self._get_next_tx_cells(cell):
            cell.set_send(self.track_has_packet_pending_tx[cell.trackId])

    def indicate_tx_cell_elapsed(self, cell):
        if self._is_first_tx_cell(cell):
            for cell in self._get_next_tx_cells(cell):
                cell.set_send(True)

    def indicate_idle_rx_cell(self, cell):
        pending = self.track_has_packet_pending_rx[cell.trackId]
        if self._is_first_rx_cell(cell):
            for cell in self._get_next_rx_cells(cell):
                cell.set_listen(pending)
        elif self._is_last_rx_cell(cell):
            self.track_has_packet_pending_rx[cell.trackId] = False

    def indicate_active_rx_cell(self, cell, pending_bit):
        pending_packet = pending_bit
        
        self.track_has_packet_pending_rx[cell.trackId] = pending_packet and not self._is_last_rx_cell(cell)

        logPrint('Received packet on mote ', self.mote.id,
        ' cell ', (self._get_index_of_cell(cell) + 1) ,'/', self._get_size_of_rx_bundle(cell.trackId), '# pending_bit=',pending_packet)

        next_cells = self._get_next_rx_cells(cell)

        for _cell in next_cells:
            _cell.set_listen(pending_packet)
            