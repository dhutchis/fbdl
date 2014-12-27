#!/bin/bash 
myid=
target=
output_base=
# 86400 duration one day
duration=
start=
end=

let duration=duration-1
cur=$start
echo "-t $myid " > tmpAll.tmp
while [ $cur -lt $end ]; do
    echo Starting timestamp: $cur = `date --date="@$cur"`
    let next=cur+duration
    cp tmpAll.tmp tmp_$cur.tmp
    echo "-o $output_base$cur.json -e &since=$cur&until=$next $target" >> tmp_$cur.tmp
    python fbdl.py -i tmp_$cur.tmp 0 
    if [ $? -ne 0 ]; then
	rm tmp_$cur.tmp
	break
    fi
    rm tmp_$cur.tmp
    let cur=next+1
    #break  # Put a break here for testing one execution.
done
rm tmpAll.tmp

#date --date="23 December 2014 15:18:07" +%s
#date --date="@1419365887"
#date --date="Tue Dec 23 15:18:07 EST 2014" +%s
