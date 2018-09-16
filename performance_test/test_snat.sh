fab -f test_iperf.py -P start
sleep 20
fab -f test_tps.py -P start
fab -f test_iperf.py -P check
fab -f test_tps.py -P check
