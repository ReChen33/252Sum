#use Script to show the diff Tbase

rm -f IWPLWP.txt
rm -f IWPLWP.err

#!/bin/bash
printf "1 1.0 0\n" >> IWPLWP.txt

am IWPLWP/ACT_DJF_5_1.0pwv_iwp.amc \
>> IWPLWP.txt 2>>IWPLWP.err

printf "1 10.0 0\n" $Pchage >> IWPLWP.txt

am IWPLWP/ACT_DJF_5_10.0pwv_iwp.amc \
>> IWPLWP.txt 2>>IWPLWP.err
