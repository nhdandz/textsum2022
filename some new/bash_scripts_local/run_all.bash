#!/bin/bash
# cd /home/hth/extend/TextSum/bash_scripts
bash /home/khmt/textsum/TextSum/bash_scripts_local/algo_control.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/root_kafka.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/multi_kafka.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/textrank.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/lexrank.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/lsa.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/m_textrank.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/m_lexrank.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/m_lsa.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/longbart.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/multibart.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/simcls.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/bart.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/keyword.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/clustering.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/name_entities.bash
sleep 5
# bash memsum.bash
# sleep 5
# bash primera.bash
# sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/bertext.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/single_kafka.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/app_process_summary.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/textsum_be.bash
sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/textsum_fe.bash

sleep 5
bash /home/khmt/textsum/TextSum/bash_scripts_local/textsum_db.bash
