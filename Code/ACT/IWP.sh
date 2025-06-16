#use Script to show the diff Tbase
#!/bin/bash

rm -f IWP.txt
rm -f IWP.err


printf "139 1.0 0\n" >> IWP.txt

am ACT_DJF_5_1.0pwv_iwp.amc \
>> IWP.txt 2>>IWP.err

printf "139 10.0 0\n" $Pchage >> IWP.txt

am ACT_DJF_5_10.0pwv_iwp.amc \
>> IWP.txt 2>>IWP.err
