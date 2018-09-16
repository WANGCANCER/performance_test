rm -rf data/*
fab -f test_tps.py -P start
cat data/num.txt

