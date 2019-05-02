import numpy
import json
import csv
import os
import glob
import collections

IDLE_LISTEN_UC = 6.4

TRAE_TYPE    = "TRA"
CRIT_PKT_RT  = "Crit.Pkt. Rate"
PDR          = "PDR"


LATENCY_MIN  = "Latency min (s)"
LATENCY_MEAN = "Latency mean (s)"
LATENCY_MAX  = "Latency max (s)"
LATENCY_99   = "Latency 99% (s)"
TOTAL_ELP_RX = "Total elapsed rx cells"
TOTAL_DIS_RX = "Avg. total disabled rx cells"
TOTAL_DRT_RX = "Avg. disabled rx cells (%)"
TOTAL_IDL_RX = "Avg. total idle listen rx cells"
TOTAL_REC_RX = "Avg. total receive rx cells"
TOTAL_TSCH_TX = "Avg. total amount of packet transmissions"
TOTAL_IVR_RX = "Avg. idle listen ratio"
TOTAL_IDL_EN = "Avg. total idle listen energy"
TOTAL_IDL_RED_ABS = "Avg. total idle listen energy saved"
TOTAL_IDL_RED = "Total idle listening reduction (%)"
AVG_DROP_Q = "Avg. packets lost (Queue full)"
AVG_DROP_RE = "Avg. packets lost (Retransmissions)"
AVG_DROP = "Avg. packets lost"
APP_PKT_REC  = "Avg. packets received"
AVG_NET_LTE = "Avg. network lifetime"
AVG_NET_LTE_PER = "Avg. network lifetime increase (%)"

allKpis = []

for filename in glob.glob("*.kpi"):
    config = collections.OrderedDict(
            [(TRAE_TYPE, ""),
            (CRIT_PKT_RT, 0),
            (PDR, 0),]
    )
    with open(filename, 'r') as kpi_json_file:
        mergedKpis = collections.OrderedDict(
            [(LATENCY_MIN, []),
            (LATENCY_MEAN, []),
            (LATENCY_MAX,  []),
            (LATENCY_99,   []),
            (TOTAL_ELP_RX, []),
            (TOTAL_DIS_RX, []),
            (TOTAL_DRT_RX, []),
            (TOTAL_IDL_RX, []),
            (TOTAL_REC_RX, []),
            (TOTAL_IVR_RX, []),
            (TOTAL_IDL_EN, []),
            (TOTAL_IDL_RED, []),
            (TOTAL_IDL_RED_ABS, []),
            (AVG_DROP, []),
            (AVG_DROP_Q, []),
            (AVG_DROP_RE, []),
            (APP_PKT_REC,  []),
            (TOTAL_TSCH_TX,[]),
            (AVG_NET_LTE,  []),]
        ) 

        kpis = json.load(kpi_json_file)
        config[CRIT_PKT_RT] = kpis["0"]['config']['Critical Packet Prob.']
        config[TRAE_TYPE] = kpis["0"]['config']['TRA']
        config[PDR] = kpis["0"]['config']['pdr']

        for run in kpis:

            #LAT
            mergedKpis[LATENCY_MIN]   .append(next((x["min"] for x in kpis[run]["global-stats"]["e2e-upstream-latency"] if x["name"] == "E2E Upstream Latency"), 0))
            mergedKpis[LATENCY_MEAN]  .append(next((x["mean"] for x in kpis[run]["global-stats"]["e2e-upstream-latency"] if x["name"] == "E2E Upstream Latency"), 0))
            mergedKpis[LATENCY_MAX]   .append(next((x["max"] for x in kpis[run]["global-stats"]["e2e-upstream-latency"] if x["name"] == "E2E Upstream Latency"), 0))
            mergedKpis[LATENCY_99]    .append(next((x["99%"] for x in kpis[run]["global-stats"]["e2e-upstream-latency"] if x["name"] == "E2E Upstream Latency"), 0))
            
            #TRX
            mergedKpis[TOTAL_ELP_RX]  .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total elapsed track rx cells"), 0))
            mergedKpis[TOTAL_DIS_RX]  .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total disabled track rx cells"), 0))
            mergedKpis[TOTAL_DRT_RX]  .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total disabled cell ratio"), 0))
            mergedKpis[TOTAL_IDL_RX]  .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total idle listen track rx cells"), 0))
            mergedKpis[TOTAL_REC_RX]   .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total receive track rx cells"), 0))
            mergedKpis[TOTAL_IVR_RX]   .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total idle listen ratio"), 0))
            mergedKpis[TOTAL_IDL_EN]   .append(next((x["value"] for x in kpis[run]["global-stats"]["global-track-statistics"] if x["name"] == "Total idle listen track rx cells"), 0) * IDLE_LISTEN_UC)
            
            #DROPS
            tsch_tx = 0
            for mote in kpis[run]:
                if "num_tsch_tx" in kpis[run][mote]:
                    tsch_tx += kpis[run][mote]['num_tsch_tx']
                if "packet_drops" in kpis[run][mote]:
                    total = 0
                    queue = 0
                    retransmissions = 0

                    if 'txqueue_full' in kpis[run][mote]['packet_drops']:
                        queue += kpis[run][mote]['packet_drops']['txqueue_full']
                    if 'max_retries' in kpis[run][mote]['packet_drops']:
                        retransmissions += kpis[run][mote]['packet_drops']['max_retries']
                    total += sum(kpis[run][mote]['packet_drops'].values())

            mergedKpis[TOTAL_TSCH_TX]  .append(tsch_tx)
            mergedKpis[AVG_DROP].append(total)
            mergedKpis[AVG_DROP_Q].append(queue)
            mergedKpis[AVG_DROP_RE].append(retransmissions)

            #APP
            mergedKpis[APP_PKT_REC].append(next((x["total"] for x in kpis[run]["global-stats"]["app_packets_received"] if x["name"] == "Number of application packets received"), 0))

            # POWER
            mergedKpis[AVG_NET_LTE].append(kpis[run]["global-stats"]["network_lifetime"][0]["min"])
        # do averages

        averagedKPIs = collections.OrderedDict(
            [(LATENCY_MIN, {"val": 0, "dev":0 }),
            (LATENCY_MEAN, {"val": 0, "dev":0}),
            (LATENCY_MAX,  {"val": 0, "dev":0}),
            (LATENCY_99,   {"val": 0, "dev":0}),
            (TOTAL_ELP_RX, {"val": 0, "dev":0}),
            (TOTAL_DIS_RX, {"val": 0, "dev":0}),
            (TOTAL_DRT_RX, {"val": 0, "dev":0}),
            (TOTAL_IDL_RX, {"val": 0, "dev":0}),
            (TOTAL_REC_RX, {"val": 0, "dev":0}),
            (TOTAL_IVR_RX, {"val": 0, "dev":0}),
            (TOTAL_IDL_EN,{"val": 0, "dev":0}),
            (TOTAL_IDL_RED,{"val": 0, "dev":0}),
            (TOTAL_IDL_RED_ABS, {"val": 0, "dev":0}),
            (AVG_DROP, {"val": 0, "dev":0}),
            (AVG_DROP_RE, {"val": 0, "dev":0}),
            (AVG_DROP_Q, {"val": 0, "dev":0}),
            (APP_PKT_REC,  {"val": 0, "dev":0}),
            (TOTAL_TSCH_TX ,  {"val": 0, "dev":0}),
            (AVG_NET_LTE, {"val": 0, "dev":0})]
        ) 

        #values

        averagedKPIs[LATENCY_MIN]["val"]  = min(mergedKpis[LATENCY_MIN])
        averagedKPIs[LATENCY_MEAN]["val"] = sum(mergedKpis[LATENCY_MEAN]) / len(mergedKpis[LATENCY_MEAN])
        averagedKPIs[LATENCY_MAX]["val"]  = max(mergedKpis[LATENCY_MAX])
        averagedKPIs[LATENCY_99]["val"]   = numpy.percentile(mergedKpis[LATENCY_99], 99)
        averagedKPIs[TOTAL_ELP_RX]["val"] = sum(mergedKpis[TOTAL_ELP_RX]) / len(mergedKpis[TOTAL_ELP_RX])
        averagedKPIs[TOTAL_DIS_RX]["val"] = sum(mergedKpis[TOTAL_DIS_RX]) / float(len(mergedKpis[TOTAL_DIS_RX]))
        averagedKPIs[TOTAL_DRT_RX]["val"] = sum(mergedKpis[TOTAL_DRT_RX]) / len(mergedKpis[TOTAL_DRT_RX])
        averagedKPIs[TOTAL_IDL_RX]["val"] = sum(mergedKpis[TOTAL_IDL_RX]) / float(len(mergedKpis[TOTAL_IDL_RX]))
        averagedKPIs[TOTAL_REC_RX]["val"] = sum(mergedKpis[TOTAL_REC_RX]) / float(len(mergedKpis[TOTAL_REC_RX]))
        averagedKPIs[TOTAL_IVR_RX]["val"] = sum(mergedKpis[TOTAL_IVR_RX]) / len(mergedKpis[TOTAL_IVR_RX])
        averagedKPIs[TOTAL_IDL_EN]["val"] = sum(mergedKpis[TOTAL_IDL_EN]) / len(mergedKpis[TOTAL_IDL_EN])
        averagedKPIs[AVG_DROP]["val"] = sum(mergedKpis[AVG_DROP]) / float(len(mergedKpis[AVG_DROP]))
        averagedKPIs[AVG_DROP_Q]["val"] = sum(mergedKpis[AVG_DROP_Q]) / float(len(mergedKpis[AVG_DROP_Q]))
        averagedKPIs[AVG_DROP_RE]["val"] = sum(mergedKpis[AVG_DROP_RE]) / float(len(mergedKpis[AVG_DROP_RE]))
        averagedKPIs[APP_PKT_REC]["val"]  = sum(mergedKpis[APP_PKT_REC])  / float(len(mergedKpis[APP_PKT_REC]))
        averagedKPIs[TOTAL_TSCH_TX]["val"]  = sum(mergedKpis[TOTAL_TSCH_TX])  / float(len(mergedKpis[TOTAL_TSCH_TX]))
        averagedKPIs[AVG_NET_LTE]["val"]  = sum(mergedKpis[AVG_NET_LTE])  / float(len(mergedKpis[AVG_NET_LTE]))
        
        #stdev

        averagedKPIs[LATENCY_MIN] ["dev"] = numpy.std(mergedKpis[LATENCY_MIN])
        averagedKPIs[LATENCY_MEAN]["dev"] = numpy.std(mergedKpis[LATENCY_MEAN])
        averagedKPIs[LATENCY_MAX] ["dev"] = numpy.std(mergedKpis[LATENCY_MAX])
        averagedKPIs[LATENCY_99]  ["dev"] = numpy.std(mergedKpis[LATENCY_99])
        averagedKPIs[TOTAL_ELP_RX]["dev"] = numpy.std(mergedKpis[TOTAL_ELP_RX])        
        averagedKPIs[TOTAL_DIS_RX]["dev"] = numpy.std(mergedKpis[TOTAL_DIS_RX])
        averagedKPIs[TOTAL_DRT_RX]["dev"] = numpy.std(mergedKpis[TOTAL_DRT_RX])
        averagedKPIs[TOTAL_IDL_RX]["dev"] = numpy.std(mergedKpis[TOTAL_IDL_RX])
        averagedKPIs[TOTAL_REC_RX]["dev"] = numpy.std(mergedKpis[TOTAL_REC_RX])
        averagedKPIs[TOTAL_IVR_RX]["dev"] = numpy.std(mergedKpis[TOTAL_IVR_RX])
        averagedKPIs[TOTAL_IDL_EN]["dev"] = numpy.std(mergedKpis[TOTAL_IDL_EN])
        averagedKPIs[AVG_DROP]["dev"] = numpy.std(mergedKpis[AVG_DROP])
        averagedKPIs[AVG_DROP_Q]["dev"] = numpy.std(mergedKpis[AVG_DROP_Q])
        averagedKPIs[AVG_DROP_RE]["dev"] = numpy.std(mergedKpis[AVG_DROP_RE])
        averagedKPIs[APP_PKT_REC]["dev"]  = numpy.std(mergedKpis[APP_PKT_REC])
        averagedKPIs[TOTAL_TSCH_TX]["dev"]  = numpy.std(mergedKpis[TOTAL_TSCH_TX])
        averagedKPIs[AVG_NET_LTE]["dev"]  = numpy.std(mergedKpis[AVG_NET_LTE])


        allKpis += [{'config': config, 'kpis': averagedKPIs, 'mergedKpi': mergedKpis, 'kpifile': kpis}]

############### #
for allkpi in allKpis:
    if allkpi['config'][TRAE_TYPE] != 'Base':
        
        for baseAllKpi in allKpis:
            if (baseAllKpi["config"][TRAE_TYPE] == 'Base' and
            baseAllKpi['config'][PDR] == allkpi['config'][PDR] 
            and baseAllKpi['config'][CRIT_PKT_RT] == allkpi['config'][CRIT_PKT_RT]):
                for index, value in enumerate(allkpi['mergedKpi'][TOTAL_IDL_RX]):
                    dif = baseAllKpi['mergedKpi'][TOTAL_IDL_RX][index] - value
                    elp = allkpi['mergedKpi'][TOTAL_ELP_RX][index]
                    allkpi['mergedKpi'][TOTAL_IDL_RED].append(100*((dif / float(elp))))
                    allkpi['mergedKpi'][TOTAL_IDL_RED_ABS].append(baseAllKpi['mergedKpi'][TOTAL_IDL_RX][index] - value)
        allkpi['kpis'][TOTAL_IDL_RED]["val"] = sum(allkpi['mergedKpi'][TOTAL_IDL_RED]) / len(allkpi['mergedKpi'][TOTAL_IDL_RED])
        allkpi['kpis'][TOTAL_IDL_RED]["dev"] = numpy.std(allkpi['mergedKpi'][TOTAL_IDL_RED])
        allkpi['kpis'][TOTAL_IDL_RED_ABS]["val"] = sum(allkpi['mergedKpi'][TOTAL_IDL_RED_ABS]) / len(allkpi['mergedKpi'][TOTAL_IDL_RED_ABS])
        allkpi['kpis'][TOTAL_IDL_RED_ABS]["dev"] = numpy.std(allkpi['mergedKpi'][TOTAL_IDL_RED_ABS])

tratypes = ['Base', 'AllListenPendingBit', 'OneShotPendingBit']
crPktProb= [0.001, 0.005, 0.01]
pdrs=[1.0,0.95,0.9,0.85,0.8,0.75,0.7]

if not os.path.exists('series'):
    os.mkdir('series')

def sortFirst(val): 
    return val[0]  



mmmList = {}

metrics = [LATENCY_MIN, LATENCY_MAX, LATENCY_MEAN,
LATENCY_99, TOTAL_ELP_RX, TOTAL_DIS_RX,
TOTAL_DRT_RX, TOTAL_IDL_RX, TOTAL_REC_RX,
TOTAL_IVR_RX, TOTAL_IDL_EN, TOTAL_IDL_RED, TOTAL_IDL_RED_ABS, AVG_DROP,
AVG_DROP_RE, AVG_DROP_Q, APP_PKT_REC, TOTAL_TSCH_TX, AVG_NET_LTE]

for tra in tratypes:
    for p in crPktProb:
        for kpi in allKpis:
            if kpi['config'][TRAE_TYPE] == tra and kpi['config'][CRIT_PKT_RT] == p:
                key = tra + str(p)
                if key not in mmmList:
                    mmmList[key] = {}
                if kpi['config'][PDR] not in mmmList[key]:
                    mmmList[key][kpi['config'][PDR]] = {el: 0 for el in metrics}
                for metric in metrics:
                    mmmList[key][kpi['config'][PDR]][metric] = kpi['kpis'][metric]["val"] 

def metricTokey(metric):
    if metric == LATENCY_MIN:
        return 'lmin'
    if metric == LATENCY_MAX:
        return 'lmax'
    if metric == LATENCY_MEAN:
        return 'lavg'
    if metric == LATENCY_99:
        return 'l99'
    if metric == TOTAL_ELP_RX:
        return 'elprx'
    if metric == TOTAL_DIS_RX:
        return 'disrx'
    if metric == TOTAL_DRT_RX:
        return 'dispr'
    if metric == TOTAL_IDL_RX:
        return 'idlrx'
    if metric == TOTAL_REC_RX:
        return 'recrx'
    if metric == TOTAL_IVR_RX:
        return 'idlratio'
    if metric == TOTAL_IDL_EN:
        return 'idlen'
    if metric == TOTAL_IDL_RED:
        return 'idlenred'
    if metric == TOTAL_IDL_RED_ABS:
        return 'idlenredabs'
    if metric == AVG_DROP:
        return 'drop'
    if metric == AVG_DROP_RE:
        return 'redrop'
    if metric == AVG_DROP_Q:
        return 'qdrop'
    if metric == APP_PKT_REC:
        return 'recpkt'
    if metric == TOTAL_TSCH_TX:
        return 'tschtxavg'
    if metric == AVG_NET_LTE:
        return 'avglife'

for key in mmmList:
    with open('series/' + "CSV_" + key + ".csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['x'] +  [metricTokey(metric) for metric in metrics])
        rows = []
        # values
        for pdr in mmmList[key]:
            rows += [[pdr] + [mmmList[key][pdr][metric] for metric in metrics]]
            
        rows.sort(key = sortFirst,)

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()


mmmList = {}

def renameTra(tra):
    if tra == 'Base':
        return 'None'
    if tra == 'OneShotPendingBit':
        return 'OneShot'
    if tra == 'AllListenPendingBit':
        return 'AllListen'

for pktRt in crPktProb:
    for p in pdrs:
        for kpi in allKpis:
            if kpi['config'][CRIT_PKT_RT] == pktRt and kpi['config'][PDR] == p:
                key = "rate_" + str(pktRt) + "_pdr_" + str(p)
                if key not in mmmList:
                    mmmList[key] = {}
                if kpi['config'][TRAE_TYPE] not in mmmList[key]:
                    mmmList[key][kpi['config'][TRAE_TYPE]] = {el: 0 for el in metrics}
                for metric in metrics:
                    mmmList[key][kpi['config'][TRAE_TYPE]][metric] = kpi['kpis'][metric]["val"] 


for key in mmmList:
    with open('series/' + "CSV_" + key + ".csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['x'] +  [metricTokey(metric) for metric in metrics])
        rows = []
        # values
        for traTypoe in mmmList[key]:
            rows += [[renameTra(traTypoe)] + [mmmList[key][traTypoe][metric] for metric in metrics]]
            

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()

mmmList = {}

for tra in tratypes:
    for p in pdrs:
        for kpi in allKpis:
            if kpi['config'][TRAE_TYPE] == tra and kpi['config'][PDR] == p:
                key = str(tra) + "_pdr_" + str(p)
                if key not in mmmList:
                    mmmList[key] = {}
                if kpi['config'][CRIT_PKT_RT] not in mmmList[key]:
                    mmmList[key][kpi['config'][CRIT_PKT_RT]] = {el: 0 for el in metrics}
                for metric in metrics:
                    mmmList[key][kpi['config'][CRIT_PKT_RT]][metric] = kpi['kpis'][metric]["val"] 


for key in mmmList:
    with open('series/' + "CSV_" + key + ".csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['x'] +  [metricTokey(metric) for metric in metrics])
        rows = []
        # values
        for rate in mmmList[key]:
            rows += [[rate] + [mmmList[key][rate][metric] for metric in metrics]]
            
        rows.sort(key = sortFirst,)

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()


mmmList = {}


for kpi in allKpis:
    for metric in metrics:
        for pdr in pdrs:
            if pdr not in mmmList:
                mmmList[pdr] = {}
            key = "tra_" + kpi['config'][TRAE_TYPE] + "_crPktRt_" + str(kpi['config'][CRIT_PKT_RT]) + "_" + metricTokey(metric)
            if pdr == kpi['config'][PDR]:
                mmmList[pdr][key] = kpi['kpis'][metric]['val']

for key in mmmList:
    with open('series/' + "CSV_all_vs_pdr.csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['pdr'] +  mmmList[pdrs[1]].keys())
        rows = []
        # values
        for p in mmmList:
            rows += [[p] + [mmmList[p][key] for key in mmmList[pdrs[1]].keys()]]
            
        rows.sort(key = sortFirst,)

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()


mmmList = {}


for kpi in allKpis:
    for metric in metrics:
        for rate in crPktProb:
            if rate not in mmmList:
                mmmList[rate] = {}
            key = "tra_" + kpi['config'][TRAE_TYPE] + "_pdr_" + str(kpi['config'][PDR]) + "_" + metricTokey(metric)
            if rate == kpi['config'][CRIT_PKT_RT]:
                mmmList[rate][key] = kpi['kpis'][metric]['val']

for key in mmmList:
    with open('series/' + "CSV_all_vs_rate.csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['rate'] +  mmmList[crPktProb[0]].keys())
        rows = []
        # values
        for r in mmmList:
            rows += [[r] + [mmmList[r][key] for key in mmmList[crPktProb[0]].keys()]]
            
        rows.sort(key = sortFirst,)

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()


mmmList = {}


for kpi in allKpis:
    for metric in metrics:
        for tra in tratypes:
            if tra not in mmmList:
                mmmList[tra] = {}
            key = "crPktProb_" + str(kpi['config'][CRIT_PKT_RT]) + "_pdr_" + str(kpi['config'][PDR]) + "_" + metricTokey(metric)
            if tra == kpi['config'][TRAE_TYPE]:
                mmmList[tra][key] = kpi['kpis'][metric]['val']

for key in mmmList:
    with open('series/' + "CSV_all_vs_tra.csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['tra'] +  mmmList[tratypes[1]].keys())
        rows = []
        # values
        for t in mmmList:
            rows += [[t] + [mmmList[t][key] for key in mmmList[tratypes[1]].keys()]]
            
        for row in rows:
            filewriter.writerow(row)
        csvfile.close()
