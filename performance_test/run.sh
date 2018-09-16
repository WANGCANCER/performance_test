rm -rf data/*
fab -f test_tcp_link.py -P start
echo "***************************************************************************"
cat data/link_num.txt|awk -F ":" {'print $2'}|awk '{sum+=$1} END{print sum}'


