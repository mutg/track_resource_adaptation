start cmd /k python runSim.py --config=configs/Sim2/config_pdr_100_oneshot.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_100_base.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_100_allListen.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_90_oneshot.json
ping 127.0.0.1 -n 5 > nul

python runSim.py --config=configs/Sim2/config_pdr_90_base.json

start cmd /k python runSim.py --config=configs/Sim2/config_pdr_90_allListen.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_80_oneshot.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_80_base.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_80_allListen.json
ping 127.0.0.1 -n 5 > nul

python runSim.py --config=configs/Sim2/config_pdr_70_oneshot.json

start cmd /k python runSim.py --config=configs/Sim2/config_pdr_70_base.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_70_allListen.json
ping 127.0.0.1 -n 5 > nul
start cmd /k  python runSim.py --config=configs/Sim2/config_pdr_75_allListen.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_75_oneshot.json
ping 127.0.0.1 -n 5 > nul

python runSim.py --config=configs/Sim2/config_pdr_75_base.json

start cmd /k python runSim.py --config=configs/Sim2/config_pdr_85_base.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_85_oneshot.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_85_allListen.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_95_oneshot.json
ping 127.0.0.1 -n 5 > nul
start cmd /k python runSim.py --config=configs/Sim2/config_pdr_95_base.json
ping 127.0.0.1 -n 5 > nul
python runSim.py --config=configs/Sim2/config_pdr_95_allListen.json