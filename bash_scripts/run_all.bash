#!/bin/bash
cd /home/nhdandz/Documents/tupk/textsum2022/bash_scripts
bash algo_control.bash
sleep 5
bash root_kafka.bash
sleep 5
bash multi_kafka.bash
sleep 5
bash textrank.bash
sleep 5
bash lexrank.bash
sleep 5
bash lsa.bash
sleep 5
bash m_textrank.bash
sleep 5
bash m_lexrank.bash
sleep 5
bash m_lsa.bash
sleep 5
# bash longbart.bash
# sleep 5
# bash multibart.bash
# sleep 5
# bash simcls.bash
# sleep 5
# bash bart.bash
# sleep 5
# bash keyword.bash
# sleep 5
bash clustering.bash
sleep 5
# bash name_entities.bash
# sleep 5
# bash memsum.bash
# sleep 5
# bash primera.bash
# sleep 5
# bash bertext.bash
# sleep 5
bash single_kafka.bash
sleep 5
bash app_process_summary.bash
sleep 5
