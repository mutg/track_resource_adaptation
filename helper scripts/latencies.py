import numpy
import json
import csv
import os
import glob
import matplotlib

if not os.path.exists('latencies'):
    os.mkdir('latencies')

for filename in glob.glob("*.kpi"):

    with open(filename, 'r') as kpi_json_file:
        kpis = json.load(kpi_json_file)

        with open('latencies/' + filename, "wb") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE, escapechar=' ')

            for v in kpis['0']['3']['latencies']:
                filewriter.writerow([v])
            csvfile.close()
        kpi_json_file.close()

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