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
BE_TX_PERIOD = "BE Period"


LATENCY_MIN_CR  = "Latency min (s), Critical"
LATENCY_MEAN_CR = "Latency mean (s), Critical"
LATENCY_MAX_CR  = "Latency max (s), Critical"
LATENCY_99_CR   = "Latency 99% (s), Critical"
LATENCY_MIN_BE  = "Latency min (s), Best effort"
LATENCY_MEAN_BE = "Latency mean (s), Best effort"
LATENCY_MAX_BE  = "Latency max (s), Best effort"
LATENCY_99_BE   = "Latency 99% (s), Best effort"
TOTAL_ELP_RX = "Total elapsed rx cells"
TOTAL_DIS_RX = "Avg. total disabled rx cells"
TOTAL_DRT_RX = "Avg. disabled rx cells (%)"
TOTAL_IDL_RX = "Avg. total idle listen rx cells"
TOTAL_REC_RX = "Avg. total receive rx cells"
TOTAL_IVR_RX = "Avg. idle listen ratio"
TOTAL_IDL_EN = "Avg. total idle listen energy"
TOTAL_IDL_RED_ABS = "Avg. total idle listen energy saved"
TOTAL_IDL_RED = "Total idle listening reduction (%)"

AVG_DROP_4 = "drop4"
AVG_DROP_3 = "drop3"
AVG_DROP_2 = "drop2"
AVG_DROP_1 = "drop1"
AVG_DROP_0 = "drop0"


AVG_DROP_Q = "Avg. packets lost (Queue full)"
AVG_DROP_RE = "Avg. packets lost (Retransmissions)"

AVG_DROP_CR = "Avg. critical packets lost"
APP_PKT_REC_CR  = "Avg. critical packets received"
APP_PKT_REC_BE  = "Avg. best effort packets received"
AVG_DROP_BE = "Avg. best effort packets lost"
TOTAL_TSCH_TX = "Avg. total amount of packet transmissions"
AVG_NET_LTE = "Avg. network lifetime"


allKpis = []

for filename in glob.glob("*.kpi"):
    config = collections.OrderedDict(
            [(TRAE_TYPE, ""),
            (CRIT_PKT_RT, 0),
            (PDR, 0),
            (BE_TX_PERIOD, 0),]
    )
    with open(filename, 'r') as kpi_json_file:
        mergedKpis = collections.OrderedDict(
            [(LATENCY_MIN_BE, []),
            (LATENCY_MEAN_BE, []),
            (LATENCY_MAX_BE,  []),
            (LATENCY_99_BE,   []),
            (LATENCY_MIN_CR, []),
            (LATENCY_MEAN_CR, []),
            (LATENCY_MAX_CR,  []),
            (LATENCY_99_CR,   []),
            (TOTAL_ELP_RX, []),
            (TOTAL_DIS_RX, []),
            (TOTAL_DRT_RX, []),
            (TOTAL_IDL_RX, []),
            (TOTAL_REC_RX, []),
            (TOTAL_IVR_RX, []),
            (TOTAL_IDL_EN, []),
            (TOTAL_IDL_RED, []),
            (TOTAL_IDL_RED_ABS, []),
            (AVG_DROP_CR, []),
            (AVG_DROP_BE, []),
            (APP_PKT_REC_CR,  []),
            (APP_PKT_REC_BE,  []),
            (AVG_DROP_0,  []),
            (AVG_DROP_1,  []),
            (AVG_DROP_2,  []),
            (AVG_DROP_3,  []),
            (AVG_DROP_4,  []),
            (AVG_DROP_Q, []),
            (AVG_DROP_RE, []),
            (TOTAL_TSCH_TX,[]),
            (AVG_NET_LTE,  []),
            ]
        ) 

        kpis = json.load(kpi_json_file)
        config[CRIT_PKT_RT] = kpis["0"]['config']['Critical Packet Prob.']
        config[TRAE_TYPE] = kpis["0"]['config']['TRA']
        config[BE_TX_PERIOD] = kpis["0"]['config']['bePeriod']
        config[PDR] = kpis["0"]['config']['pdr']

        for run in kpis:

            #LAT
            mergedKpis[LATENCY_MIN_BE]   .append(kpis[run]["4"]["latency_min_s"])
            mergedKpis[LATENCY_MEAN_BE]  .append(kpis[run]["4"]["latency_avg_s"])
            mergedKpis[LATENCY_MAX_BE]   .append(kpis[run]["4"]["latency_max_s"])
            mergedKpis[LATENCY_99_BE]    .append(numpy.percentile(kpis[run]["4"]["latencies"],99))
    
            mergedKpis[LATENCY_MIN_CR]   .append(kpis[run]["3"]["latency_min_s"])
            mergedKpis[LATENCY_MEAN_CR]  .append(kpis[run]["3"]["latency_avg_s"])
            mergedKpis[LATENCY_MAX_CR]   .append(kpis[run]["3"]["latency_max_s"])
            mergedKpis[LATENCY_99_CR]    .append(numpy.percentile(kpis[run]["3"]["latencies"],99))

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
                if 'num_tsch_tx' in kpis[run][mote]:
                    tsch_tx += kpis[run][mote]['num_tsch_tx']
                if "packet_drops" in kpis[run][mote]:
                    queue = 0
                    retransmissions = 0
                    if 'txqueue_full' in kpis[run][mote]['packet_drops']:
                        queue += kpis[run][mote]['packet_drops']['txqueue_full']

                    if 'max_retries' in kpis[run][mote]['packet_drops']:
                        retransmissions += kpis[run][mote]['packet_drops']['max_retries']

                    mergedKpis["drop"+ str(mote)].append(queue + retransmissions)

                    
            mergedKpis[TOTAL_TSCH_TX]  .append(tsch_tx)

            mergedKpis[AVG_DROP_CR].append(kpis[run]["3"]["upstream_num_lost"])
            mergedKpis[AVG_DROP_BE].append(kpis[run]["4"]["upstream_num_lost"])

            mergedKpis[AVG_DROP_Q].append(queue)
            mergedKpis[AVG_DROP_RE].append(retransmissions)
            mergedKpis[AVG_NET_LTE].append(kpis[run]["global-stats"]["network_lifetime"][0]["min"])

            #APP
            mergedKpis[APP_PKT_REC_BE].append(kpis[run]["4"]["upstream_num_rx"])
            mergedKpis[APP_PKT_REC_CR].append(kpis[run]["3"]["upstream_num_rx"])


        # do averages

        averagedKPIs = collections.OrderedDict(
            [(LATENCY_MIN_CR, {"val": 0, "dev":0 }),
            (LATENCY_MEAN_CR, {"val": 0, "dev":0}),
            (LATENCY_MAX_CR,  {"val": 0, "dev":0}),
            (LATENCY_99_CR,   {"val": 0, "dev":0}),
            (LATENCY_MIN_BE, {"val": 0, "dev":0 }),
            (LATENCY_MEAN_BE, {"val": 0, "dev":0}),
            (LATENCY_MAX_BE,  {"val": 0, "dev":0}),
            (LATENCY_99_BE,   {"val": 0, "dev":0}),
            (TOTAL_ELP_RX, {"val": 0, "dev":0}),
            (TOTAL_DIS_RX, {"val": 0, "dev":0}),
            (TOTAL_DRT_RX, {"val": 0, "dev":0}),
            (TOTAL_IDL_RX, {"val": 0, "dev":0}),
            (TOTAL_REC_RX, {"val": 0, "dev":0}),
            (TOTAL_IVR_RX, {"val": 0, "dev":0}),
            (TOTAL_IDL_EN,{"val": 0, "dev":0}),
            (TOTAL_IDL_RED,{"val": 0, "dev":0}),
            (TOTAL_IDL_RED_ABS, {"val": 0, "dev":0}),
            (AVG_DROP_0,  {"val": 0, "dev":0}),
            (AVG_DROP_1,  {"val": 0, "dev":0}),
            (AVG_DROP_2,  {"val": 0, "dev":0}),
            (AVG_DROP_3,  {"val": 0, "dev":0}),
            (AVG_DROP_4,  {"val": 0, "dev":0}),
            (AVG_DROP_CR, {"val": 0, "dev":0}),
            (AVG_DROP_BE, {"val": 0, "dev":0}),
            (APP_PKT_REC_CR,  {"val": 0, "dev":0}),
            (APP_PKT_REC_BE,  {"val": 0, "dev":0}),
            (AVG_DROP_RE, {"val": 0, "dev":0}),
            (AVG_DROP_Q, {"val": 0, "dev":0}),
            (TOTAL_TSCH_TX ,  {"val": 0, "dev":0}),
            (AVG_NET_LTE, {"val": 0, "dev":0}) ]
        ) 

        #values

        averagedKPIs[LATENCY_MIN_CR]["val"]  = min(mergedKpis[LATENCY_MIN_CR])
        averagedKPIs[LATENCY_MEAN_CR]["val"] = sum(mergedKpis[LATENCY_MEAN_CR]) / len(mergedKpis[LATENCY_MEAN_CR])
        averagedKPIs[LATENCY_MAX_CR]["val"]  = max(mergedKpis[LATENCY_MAX_CR])
        averagedKPIs[LATENCY_99_CR]["val"]   = numpy.percentile(mergedKpis[LATENCY_99_CR], 99)
        averagedKPIs[LATENCY_MIN_BE]["val"]  = min(mergedKpis[LATENCY_MIN_BE])
        averagedKPIs[LATENCY_MEAN_BE]["val"] = sum(mergedKpis[LATENCY_MEAN_BE]) / len(mergedKpis[LATENCY_MEAN_BE])
        averagedKPIs[LATENCY_MAX_BE]["val"]  = max(mergedKpis[LATENCY_MAX_BE])
        averagedKPIs[LATENCY_99_BE]["val"]   = numpy.percentile(mergedKpis[LATENCY_99_BE], 99)
        averagedKPIs[TOTAL_ELP_RX]["val"] = sum(mergedKpis[TOTAL_ELP_RX]) / len(mergedKpis[TOTAL_ELP_RX])
        averagedKPIs[TOTAL_DIS_RX]["val"] = sum(mergedKpis[TOTAL_DIS_RX]) / float(len(mergedKpis[TOTAL_DIS_RX]))
        averagedKPIs[TOTAL_DRT_RX]["val"] = sum(mergedKpis[TOTAL_DRT_RX]) / len(mergedKpis[TOTAL_DRT_RX])
        averagedKPIs[TOTAL_IDL_RX]["val"] = sum(mergedKpis[TOTAL_IDL_RX]) / float(len(mergedKpis[TOTAL_IDL_RX]))
        averagedKPIs[TOTAL_REC_RX]["val"] = sum(mergedKpis[TOTAL_REC_RX]) / float(len(mergedKpis[TOTAL_REC_RX]))
        averagedKPIs[TOTAL_IVR_RX]["val"] = sum(mergedKpis[TOTAL_IVR_RX]) / len(mergedKpis[TOTAL_IVR_RX])
        averagedKPIs[TOTAL_IDL_EN]["val"] = sum(mergedKpis[TOTAL_IDL_EN]) / len(mergedKpis[TOTAL_IDL_EN])
        averagedKPIs[AVG_DROP_0]["val"] = sum(mergedKpis[AVG_DROP_0]) / float(len(mergedKpis[AVG_DROP_0]))
        averagedKPIs[AVG_DROP_1]["val"] = sum(mergedKpis[AVG_DROP_1]) / float(len(mergedKpis[AVG_DROP_1]))
        averagedKPIs[AVG_DROP_2]["val"] = sum(mergedKpis[AVG_DROP_2]) / float(len(mergedKpis[AVG_DROP_2]))
        averagedKPIs[AVG_DROP_3]["val"] = sum(mergedKpis[AVG_DROP_3]) / float(len(mergedKpis[AVG_DROP_3]))
        averagedKPIs[AVG_DROP_4]["val"] = sum(mergedKpis[AVG_DROP_4]) / float(len(mergedKpis[AVG_DROP_4]))
        averagedKPIs[AVG_DROP_CR]["val"] = sum(mergedKpis[AVG_DROP_CR]) / float(len(mergedKpis[AVG_DROP_CR]))
        averagedKPIs[AVG_DROP_BE]["val"] = sum(mergedKpis[AVG_DROP_BE]) / float(len(mergedKpis[AVG_DROP_BE]))
        averagedKPIs[APP_PKT_REC_CR]["val"]  = sum(mergedKpis[APP_PKT_REC_CR])  / float(len(mergedKpis[APP_PKT_REC_CR]))
        averagedKPIs[APP_PKT_REC_BE]["val"]  = sum(mergedKpis[APP_PKT_REC_BE])  / float(len(mergedKpis[APP_PKT_REC_BE]))
        averagedKPIs[AVG_DROP_Q]["val"] = sum(mergedKpis[AVG_DROP_Q]) / float(len(mergedKpis[AVG_DROP_Q]))
        averagedKPIs[AVG_DROP_RE]["val"] = sum(mergedKpis[AVG_DROP_RE]) / float(len(mergedKpis[AVG_DROP_RE]))
        averagedKPIs[TOTAL_TSCH_TX]["val"]  = sum(mergedKpis[TOTAL_TSCH_TX])  / float(len(mergedKpis[TOTAL_TSCH_TX]))
        averagedKPIs[AVG_NET_LTE]["val"]  = sum(mergedKpis[AVG_NET_LTE])  / float(len(mergedKpis[AVG_NET_LTE]))

        #stdev

        averagedKPIs[LATENCY_MIN_CR] ["dev"] = numpy.std(mergedKpis[LATENCY_MIN_CR])
        averagedKPIs[LATENCY_MEAN_CR]["dev"] = numpy.std(mergedKpis[LATENCY_MEAN_CR])
        averagedKPIs[LATENCY_MAX_CR] ["dev"] = numpy.std(mergedKpis[LATENCY_MAX_CR])
        averagedKPIs[LATENCY_99_CR]  ["dev"] = numpy.std(mergedKpis[LATENCY_99_CR])
        averagedKPIs[LATENCY_MIN_BE] ["dev"] = numpy.std(mergedKpis[LATENCY_MIN_BE])
        averagedKPIs[LATENCY_MEAN_BE]["dev"] = numpy.std(mergedKpis[LATENCY_MEAN_BE])
        averagedKPIs[LATENCY_MAX_BE] ["dev"] = numpy.std(mergedKpis[LATENCY_MAX_BE])
        averagedKPIs[LATENCY_99_BE]  ["dev"] = numpy.std(mergedKpis[LATENCY_99_BE])
        averagedKPIs[TOTAL_ELP_RX]["dev"] = numpy.std(mergedKpis[TOTAL_ELP_RX])        
        averagedKPIs[TOTAL_DIS_RX]["dev"] = numpy.std(mergedKpis[TOTAL_DIS_RX])
        averagedKPIs[TOTAL_DRT_RX]["dev"] = numpy.std(mergedKpis[TOTAL_DRT_RX])
        averagedKPIs[TOTAL_IDL_RX]["dev"] = numpy.std(mergedKpis[TOTAL_IDL_RX])
        averagedKPIs[TOTAL_REC_RX]["dev"] = numpy.std(mergedKpis[TOTAL_REC_RX])
        averagedKPIs[TOTAL_IVR_RX]["dev"] = numpy.std(mergedKpis[TOTAL_IVR_RX])
        averagedKPIs[TOTAL_IDL_EN]["dev"] = numpy.std(mergedKpis[TOTAL_IDL_EN])
        averagedKPIs[AVG_DROP_0]["dev"] = numpy.std(mergedKpis[AVG_DROP_0])
        averagedKPIs[AVG_DROP_1]["dev"] = numpy.std(mergedKpis[AVG_DROP_1])
        averagedKPIs[AVG_DROP_2]["dev"] = numpy.std(mergedKpis[AVG_DROP_2])
        averagedKPIs[AVG_DROP_3]["dev"] = numpy.std(mergedKpis[AVG_DROP_3])
        averagedKPIs[AVG_DROP_4]["dev"] = numpy.std(mergedKpis[AVG_DROP_4])
        averagedKPIs[AVG_DROP_CR]["dev"] = numpy.std(mergedKpis[AVG_DROP_CR])
        averagedKPIs[AVG_DROP_BE]["dev"] = numpy.std(mergedKpis[AVG_DROP_BE])
        averagedKPIs[AVG_DROP_Q]["dev"] = numpy.std(mergedKpis[AVG_DROP_Q])
        averagedKPIs[AVG_DROP_RE]["dev"] = numpy.std(mergedKpis[AVG_DROP_RE])
        averagedKPIs[APP_PKT_REC_CR]["dev"]  = numpy.std(mergedKpis[APP_PKT_REC_CR])
        averagedKPIs[APP_PKT_REC_BE]["dev"]  = numpy.std(mergedKpis[APP_PKT_REC_BE])
        averagedKPIs[TOTAL_TSCH_TX]["dev"]  = numpy.std(mergedKpis[TOTAL_TSCH_TX])
        averagedKPIs[AVG_NET_LTE]["dev"]  = numpy.std(mergedKpis[AVG_NET_LTE])


        allKpis += [{'config': config, 'kpis': averagedKPIs, 'mergedKpi': mergedKpis, 'kpifile': kpis}]

############### #
for allkpi in allKpis:
    if allkpi['config'][TRAE_TYPE] != 'Base':
        
        for baseAllKpi in allKpis:
            if (baseAllKpi["config"][TRAE_TYPE] == 'Base' and
            baseAllKpi['config'][PDR] == allkpi['config'][PDR]
            and baseAllKpi['config'][CRIT_PKT_RT] == allkpi['config'][CRIT_PKT_RT]
            and baseAllKpi['config'][BE_TX_PERIOD] == allkpi['config'][BE_TX_PERIOD]):
                dif = baseAllKpi['kpis'][TOTAL_IDL_RX]['val'] - allkpi['kpis'][TOTAL_IDL_RX]['val']
                elp = baseAllKpi['kpis'][TOTAL_ELP_RX]['val']
                allkpi['kpis'][TOTAL_IDL_RED]['val'] = 100*((dif / float(elp)))
                allkpi['kpis'][TOTAL_IDL_RED_ABS]['val'] = dif            

tratypes = ['Base', 'AllListenPendingBit', 'OneShotPendingBit']
crPktProb= [0.005]
beTxPeriod = [1, 2, 3]
pdrs=[0.95]


if not os.path.exists('series'):
    os.mkdir('series')

def sortFirst(val): 
    return val[0]  

mmmList = {}

metrics = [LATENCY_MIN_CR, LATENCY_MAX_CR, LATENCY_MEAN_CR,
LATENCY_99_CR, LATENCY_MIN_BE, LATENCY_MAX_BE, LATENCY_MEAN_BE,
LATENCY_99_BE, TOTAL_ELP_RX, TOTAL_DIS_RX,
TOTAL_DRT_RX, TOTAL_IDL_RX, TOTAL_REC_RX,
TOTAL_IVR_RX, TOTAL_IDL_EN, TOTAL_IDL_RED_ABS, TOTAL_IDL_RED, AVG_DROP_0, AVG_DROP_1, AVG_DROP_2, AVG_DROP_3, AVG_DROP_4, AVG_DROP_CR,
AVG_DROP_BE, APP_PKT_REC_CR, APP_PKT_REC_BE,
AVG_DROP_RE, AVG_DROP_Q, TOTAL_TSCH_TX, AVG_NET_LTE]

for tra in tratypes:
    for p in beTxPeriod:
        for kpi in allKpis:
            if kpi['config'][TRAE_TYPE] == tra and kpi['config'][BE_TX_PERIOD] == p:
                key = tra + str(p)
                if key not in mmmList:
                    mmmList[key] = {}
                if kpi['config'][PDR] not in mmmList[key]:
                    mmmList[key][kpi['config'][PDR]] = {el: 0 for el in metrics}
                for metric in metrics:
                    mmmList[key][kpi['config'][PDR]][metric] = kpi['kpis'][metric]["val"] 

def metricTokey(metric):
    if metric == LATENCY_MIN_BE:
        return 'lminbe'
    if metric == LATENCY_MAX_BE:
        return 'lmaxbe'
    if metric == LATENCY_MEAN_BE:
        return 'lavgbe'
    if metric == LATENCY_99_BE:
        return 'l99be'
    if metric == LATENCY_MIN_CR:
        return 'lmincr'
    if metric == LATENCY_MAX_CR:
        return 'lmaxcr'
    if metric == LATENCY_MEAN_CR:
        return 'lavgcr'
    if metric == LATENCY_99_CR:
        return 'l99cr'
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
    if metric == AVG_DROP_CR:
        return 'dropcr'
    if metric == AVG_DROP_BE:
        return 'dropbe'
    if metric == APP_PKT_REC_CR:
        return 'recpktcr'
    if metric == APP_PKT_REC_BE:
        return 'recpktbe'
    if metric == AVG_DROP_RE:
        return 'redrop'
    if metric == AVG_DROP_Q:
        return 'qdrop'
    if metric == AVG_NET_LTE:
        return 'avglife'
    if metric == TOTAL_TSCH_TX:
        return 'tschtxavg'
    if metric == TOTAL_IDL_RED_ABS:
        return 'idlenredabs'
    return metric

for key in mmmList:
    with open('series/' + "CSV_" + key + ".csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['x'] +  [metricTokey(metric) for metric in metrics])
        rows = []
        # values
        for pr in mmmList[key]:
            rows += [[pr] + [mmmList[key][pr][metric] for metric in metrics]]
            
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

for pktRt in beTxPeriod:
    for p in pdrs:
        for kpi in allKpis:
            if kpi['config'][BE_TX_PERIOD] == pktRt and kpi['config'][PDR] == p:
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
        for rate in beTxPeriod:
            if rate not in mmmList:
                mmmList[rate] = {}
            key = "tra_" + kpi['config'][TRAE_TYPE] + "_pdr_" + str(kpi['config'][PDR]) + "_" + metricTokey(metric)
            if rate == kpi['config'][BE_TX_PERIOD]:
                mmmList[rate][key] = kpi['kpis'][metric]['val']

for key in mmmList:
    with open('series/' + "CSV_all_vs_rate.csv", "wb") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')
        # explain
        filewriter.writerow(['x'] +  mmmList[beTxPeriod[0]].keys())
        rows = []
        # values
        for r in mmmList:
            rows += [[r] + [mmmList[r][key] for key in mmmList[beTxPeriod[0]].keys()]]
            
        rows.sort(key = sortFirst,)

        for row in rows:
            filewriter.writerow(row)
        csvfile.close()


'''

if not os.path.exists('csv'):
    os.mkdir('csv')


if not os.path.exists('csv/avg'):
    os.mkdir('csv/avg')

with open('csv/avg/' + filename.split('.dat.')[0] + "_AVERAGE.csv", "wb") as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    # header
    filewriter.writerow(config.keys() + averagedKPIs.keys())
    # values
    filewriter.writerow(config.values() + [averagedKPIs[key]["val"] for key in averagedKPIs])

    csvfile.close()

if not os.path.exists('csv/dev'):
    os.mkdir('csv/dev')

with open('csv/dev/' + filename.split('.dat.')[0] + "_STD.csv", "wb") as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    # header
    filewriter.writerow(averagedKPIs.keys())
    # dev
    filewriter.writerow([averagedKPIs[key]["dev"] for key in averagedKPIs])

    csvfile.close()
'''