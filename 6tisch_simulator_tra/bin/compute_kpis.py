from __future__ import division

# =========================== adjust path =====================================

import os
import sys

import netaddr

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

# ========================== imports ==========================================

import json
import glob
import numpy as np

from SimEngine import SimLog
import SimEngine.Mote.MoteDefines as d

# =========================== defines =========================================

DAGROOT_ID = 0  # we assume first mote is DAGRoot
DAGROOT_IP = 'fd00::1:0'
BATTERY_AA_CAPACITY_mAh = 2821.5

# =========================== decorators ======================================

def openfile(func):
    def inner(inputfile):
        with open(inputfile, 'r') as f:
            return func(f)
    return inner

# =========================== helpers =========================================

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def init_mote():
    return {
        'upstream_num_tx': 0,
        'upstream_num_rx': 0,
        'upstream_num_lost': 0,
        'join_asn': None,
        'join_time_s': None,
        'sync_asn': None,
        'sync_time_s': None,
        'charge_asn': None,
        'upstream_pkts': {},
        'latencies': [],
        'num_tsch_tx': 0,
        'hops': [],
        'charge': None,
        'packet_drops': {},
        'lifetime_AA_years': None,
        'avg_current_uA': None,
    }

# =========================== KPIs ============================================

@openfile
def kpis_all(inputfile):
    config = {
        'pdr': 0,
        'Critical Packet Prob.': 0,
        'TRA': 'none'
    }
    allstats = {} # indexed by run_id, mote_id

    file_settings = json.loads(inputfile.readline())  # first line contains settings

    # === gather raw stats

    for line in inputfile:
        logline = json.loads(line)

        # shorthands
        run_id = logline['_run_id']
        if '_asn' in logline: # TODO this should be enforced in each line
            asn = logline['_asn']
        if '_mote_id' in logline: # TODO this should be enforced in each line
            mote_id = logline['_mote_id']

        # populate
        if run_id not in allstats:
            allstats[run_id] = {}
        if '_mote_id' in logline and mote_id not in allstats[run_id]:
            allstats[run_id][mote_id] = init_mote()

        if   logline['_type'] == SimLog.LOG_TSCH_SYNCED['type']:
            # sync'ed

            # shorthands
            mote_id    = logline['_mote_id']

            # only log non-dagRoot sync times
            if mote_id == DAGROOT_ID:
                continue

            allstats[run_id][mote_id]['sync_asn']  = asn
            allstats[run_id][mote_id]['sync_time_s'] = asn*file_settings['tsch_slotDuration']

        elif logline['_type'] == 'config':
            config['pdr'] = logline['pdr']
            config['Critical Packet Prob.'] = logline['crPktProb']
            config['TRA'] = logline['trae']

        elif logline['_type'] == SimLog.LOG_SECJOIN_JOINED['type']:
            # joined

            # shorthands
            mote_id    = logline['_mote_id']

            # only log non-dagRoot join times
            if mote_id == DAGROOT_ID:
                continue

            # populate
            assert allstats[run_id][mote_id]['sync_asn'] is not None
            allstats[run_id][mote_id]['join_asn']  = asn
            allstats[run_id][mote_id]['join_time_s'] = asn*file_settings['tsch_slotDuration']

        elif logline['_type'] == SimLog.LOG_APP_TX['type']:
            # packet transmission

            # shorthands
            mote_id    = logline['_mote_id']
            dstIp      = logline['packet']['net']['dstIp']
            appcounter = logline['packet']['app']['appcounter']

            # only log upstream packets
            if dstIp != DAGROOT_IP: 
                continue

            # populate
            assert allstats[run_id][mote_id]['join_asn'] is not None
            if appcounter not in allstats[run_id][mote_id]['upstream_pkts']:
                allstats[run_id][mote_id]['upstream_pkts'][appcounter] = {
                    'hops': 0,
                }

            allstats[run_id][mote_id]['upstream_pkts'][appcounter]['tx_asn'] = asn

        elif logline['_type'] == SimLog.LOG_TSCH_TXDONE['type']:
            mote_id    = logline['_mote_id']
            if logline['packet'] is None or logline['packet']['type'] not in d.TRACKED_TYPES:
                continue

            allstats[run_id][mote_id]['num_tsch_tx'] += 1

        elif logline['_type'] == SimLog.LOG_APP_RX['type']:
            # packet reception

            # shorthands
            mote_id    = netaddr.IPAddress(logline['packet']['net']['srcIp']).words[-1]
            dstIp      = logline['packet']['net']['dstIp']
            hop_limit  = logline['packet']['net']['hop_limit']
            appcounter = logline['packet']['app']['appcounter']
            pkt_type   = logline['packet']['type']

            # only log upstream packets
            if dstIp != DAGROOT_IP:
                continue

            allstats[run_id][mote_id]['upstream_pkts'][appcounter]['hops']   = (
                d.IPV6_DEFAULT_HOP_LIMIT - hop_limit + 1
            )
            allstats[run_id][mote_id]['upstream_pkts'][appcounter]['rx_asn'] = asn
            allstats[run_id][mote_id]['upstream_pkts'][appcounter]['type']   = pkt_type

        elif logline['_type'] == SimLog.LOG_PACKET_DROPPED['type']:
            # packet dropped

            # shorthands
            mote_id    = logline['_mote_id']
            reason     = logline['reason']
            packet     = logline['packet']

            if packet['type'] in d.TRACKED_TYPES:
                # populate
                if reason not in allstats[run_id][mote_id]['packet_drops']:
                    allstats[run_id][mote_id]['packet_drops'][reason] = 0

                allstats[run_id][mote_id]['packet_drops'][reason] += 1

        elif logline['_type'] == SimLog.LOG_BATT_CHARGE['type']:
            # battery charge

            # shorthands
            mote_id    = logline['_mote_id']
            charge     = logline['charge']

            # only log non-dagRoot charge
            if mote_id == DAGROOT_ID:
                continue

            # populate
            if allstats[run_id][mote_id]['charge'] is not None:
                assert charge >= allstats[run_id][mote_id]['charge']

            allstats[run_id][mote_id]['charge_asn'] = asn
            allstats[run_id][mote_id]['charge']     = charge

        elif logline['_type'] == SimLog.LOG_TRACK_ELAPSED_RX_TOTAL['type']:
            mote_id    = logline['_mote_id']
            if logline['trackId'] == 0:
                allstats[run_id][mote_id]['num_elapsed_rx_cells'] = logline['num_elapsed_rx']

        elif logline['_type'] == SimLog.LOG_TRACK_DISABLED_RX_TOTAL['type']:
            mote_id    = logline['_mote_id']
            if logline['trackId'] == 0:

                allstats[run_id][mote_id]['num_disabled_rx_cells'] = logline['num_disabled_rx']

        elif logline['_type'] == SimLog.LOG_TRACK_IDLE_LISTEN_RX_TOTAL['type']:
            mote_id    = logline['_mote_id']
            if logline['trackId'] == 0:

                allstats[run_id][mote_id]['num_idle_listen_rx_cells'] = logline['num_idle_listen_rx']

        elif logline['_type'] == SimLog.LOG_TRACK_RECEIVE_RX_TOTAL['type']:
            mote_id    = logline['_mote_id']
            if logline['trackId'] == 0:
            
                allstats[run_id][mote_id]['num_receive_rx_cells'] = logline['num_receive_rx']

    # === compute advanced motestats

    for (run_id, per_mote_stats) in allstats.items():
        for (mote_id, motestats) in per_mote_stats.items():
            if 'num_idle_listen_rx_cells' in motestats:
                motestats['idle_rx_ratio'] = motestats['num_idle_listen_rx_cells'] / float(motestats['num_receive_rx_cells'])
            if mote_id != 0:
                if (motestats['sync_asn'] is not None) and (motestats['charge_asn'] is not None):
                    # avg_current, lifetime_AA
                    if (
                            (motestats['charge'] <= 0)
                            or
                            (motestats['charge_asn'] == motestats['sync_asn'])
                        ):
                        motestats['lifetime_AA_years'] = 'N/A'
                    else:
                        motestats['avg_current_uA'] = motestats['charge']/float((motestats['charge_asn']-motestats['sync_asn']) * file_settings['tsch_slotDuration'])
                        assert motestats['avg_current_uA'] > 0
                        motestats['lifetime_AA_years'] = (BATTERY_AA_CAPACITY_mAh*1000/float(motestats['avg_current_uA']))/(24.0*365)
                if motestats['join_asn'] is not None:
                    # latencies, upstream_num_tx, upstream_num_rx, upstream_num_lost
                    for (appcounter, pktstats) in allstats[run_id][mote_id]['upstream_pkts'].items():
                        motestats['upstream_num_tx']      += 1
                        if 'rx_asn' in pktstats:
                            motestats['upstream_num_rx']  += 1
                            thislatency = (pktstats['rx_asn']-pktstats['tx_asn'])*file_settings['tsch_slotDuration']
                            motestats['latencies']  += [thislatency]
                            motestats['hops']       += [pktstats['hops']]
                        else:
                            motestats['upstream_num_lost'] += 1
                    if (motestats['upstream_num_rx'] > 0) and (motestats['upstream_num_tx'] > 0):
                        motestats['latency_min_s'] = min(motestats['latencies'])
                        motestats['latency_avg_s'] = sum(motestats['latencies'])/float(len(motestats['latencies']))
                        motestats['latency_max_s'] = max(motestats['latencies'])
                        motestats['upstream_reliability'] = motestats['upstream_num_rx']/float(motestats['upstream_num_tx'])
                        motestats['avg_hops'] = sum(motestats['hops'])/float(len(motestats['hops']))

    # === network stats
    for (run_id, per_mote_stats) in allstats.items():

        #-- define stats
        total_idle_track_rx_cells = 0
        total_active_track_rx_cells = 0
        total_elapsed_track_rx_cells = 0
        total_disabled_track_rx_cells = 0
        app_packets_sent = 0
        app_packets_received = 0
        app_packets_lost = 0
        joining_times = []
        us_latencies = []
        current_consumed = []
        lifetimes = []
        slot_duration = file_settings['tsch_slotDuration']

        #-- compute stats

        for (mote_id, motestats) in per_mote_stats.items():

            # counters

            if 'num_idle_listen_rx_cells' in motestats:
                total_idle_track_rx_cells += motestats['num_idle_listen_rx_cells']
            if 'num_elapsed_rx_cells' in motestats:
                total_elapsed_track_rx_cells += motestats['num_elapsed_rx_cells']
            if 'num_receive_rx_cells' in motestats:
                total_active_track_rx_cells += motestats['num_receive_rx_cells']
            if 'num_disabled_rx_cells' in motestats:
                total_disabled_track_rx_cells += motestats['num_disabled_rx_cells']

            if mote_id == DAGROOT_ID:
                continue

            app_packets_sent += motestats['upstream_num_tx']
            app_packets_received += motestats['upstream_num_rx']
            app_packets_lost += motestats['upstream_num_lost']

            # joining times

            if motestats['join_asn'] is not None:
                joining_times.append(motestats['join_asn'])

            # latency

            us_latencies += motestats['latencies']

            # current consumed

            current_consumed.append(motestats['charge'])
            if motestats['lifetime_AA_years'] is not None:
                lifetimes.append(motestats['lifetime_AA_years'])

        #-- save stats
        allstats[run_id]['config'] = config
        allstats[run_id]['global-stats'] = {
            'global-track-statistics': [
                {
                    'name': 'Total disabled track rx cells',
                    'unit': 'cells',
                    'value': total_disabled_track_rx_cells
                },
                {
                    'name': 'Total elapsed track rx cells',
                    'unit': 'cells',
                    'value': total_elapsed_track_rx_cells
                },
                {
                    'name': 'Total disabled cell ratio',
                    'unit': 'disabled / elapsed',
                    'value': total_disabled_track_rx_cells / float(total_elapsed_track_rx_cells)
                },
                {
                    'name': 'Total idle listen track rx cells',
                    'unit': 'cells',
                    'value': total_idle_track_rx_cells
                },
                {
                    'name': 'Total receive track rx cells',
                    'unit': 'cells',
                    'value':  total_active_track_rx_cells
                },
                {
                    'name': 'Total idle listen ratio',
                    'unit': 'Idle listen / Receive',
                    'value': total_idle_track_rx_cells / float(total_active_track_rx_cells)
                }
            ],
            'e2e-upstream-delivery': [
                {
                    'name': 'E2E Upstream Delivery Ratio',
                    'unit': '%',
                    'value': 1 - app_packets_lost / app_packets_sent if (app_packets_lost > 0 or app_packets_sent > 0) else '#N//A'
                },
                {
                    'name': 'E2E Upstream Loss Rate',
                    'unit': '%',
                    'value':  app_packets_lost / app_packets_sent if (app_packets_lost > 0 or app_packets_sent > 0) else '#N//A'
                }
            ],
            'e2e-upstream-latency': [
                {
                    'name': 'E2E Upstream Latency',
                    'unit': 's',
                    'mean': mean(us_latencies),
                    'min': min(us_latencies),
                    'max': max(us_latencies),
                    '99%': np.percentile(us_latencies, 99)
                },
                {
                    'name': 'E2E Upstream Latency',
                    'unit': 'slots',
                    'mean': mean(us_latencies) / slot_duration,
                    'min': min(us_latencies) / slot_duration,
                    'max': max(us_latencies) / slot_duration,
                    '99%': np.percentile(us_latencies, 99) / slot_duration
                }
            ],
            'current-consumed': [
                {
                    'name': 'Current Consumed',
                    'unit': 'mA',
                    'mean': mean(current_consumed),
                    '99%': np.percentile(current_consumed, 99)
                }
            ],
            'network_lifetime':[
                {
                    'name': 'Network Lifetime',
                    'unit': 'years',
                    'min': min(lifetimes),
                    'total_capacity_mAh': BATTERY_AA_CAPACITY_mAh,
                }
            ],
            'joining-time': [
                {
                    'name': 'Joining Time',
                    'unit': 'slots',
                    'min': min(joining_times),
                    'max': max(joining_times),
                    'mean': mean(joining_times),
                    '99%': np.percentile(joining_times, 99)
                }
            ],
            'app-packets-sent': [
                {
                    'name': 'Number of application packets sent',
                    'total': app_packets_sent
                }
            ],
            'app_packets_received': [
                {
                    'name': 'Number of application packets received',
                    'total': app_packets_received
                }
            ],
            'app_packets_lost': [
                {
                    'name': 'Number of application packets lost',
                    'total': app_packets_lost
                }
            ]
        }

    # === remove unnecessary stats

    for (run_id, per_mote_stats) in allstats.items():
        for (mote_id, motestats) in per_mote_stats.items():
            if 'sync_asn' in motestats:
                del motestats['sync_asn']
            if 'charge_asn' in motestats:
                del motestats['charge_asn']
                del motestats['charge']
            if 'join_asn' in motestats:
                del motestats['upstream_pkts']
                del motestats['hops']
                del motestats['join_asn']

    return allstats

# =========================== main ============================================

def main():

    # FIXME: This logic could be a helper method for other scripts
    # Identify simData having the latest results. That directory should have
    # the latest "mtime".
    subfolders = list(
        map(
            lambda x: os.path.join('simData', x),
            os.listdir('simData')
        )
    )
    subfolder = max(subfolders, key=os.path.getmtime)
    for infile in glob.glob(os.path.join(subfolder, '*.dat')):
        print 'generating KPIs for {0}'.format(infile)

        # gather the kpis
        kpis = kpis_all(infile)

        # print on the terminal
        print json.dumps(kpis, indent=4)

        # add to the data folder
        outfile = '{0}.kpi'.format(infile)
        with open(outfile, 'w') as f:
            f.write(json.dumps(kpis, indent=4))
        print 'KPIs saved in {0}'.format(outfile)

if __name__ == '__main__':
    main()
