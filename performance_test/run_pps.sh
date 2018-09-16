fab -f test_pps.py -P test
sleep 60
for id in `cat ./ip_list/server_id`
do
  nova reboot $id
done
sleep 10
fab -f test_pps.py -P cat
