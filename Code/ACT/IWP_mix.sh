#use Script to show the diff PWV with diff mixing ratio of IWP

rm -f diff_IWP.txt
rm -f diff_IWP.err

#!/bin/bash
# float sequence
for Percent in $(awk '
        BEGIN {
            for (p = 0.1; p <= 0.6; p += 0.4)
                printf("%.1f\n", p)
            for (p = 1.0; p < 1.1; p += 0.1)
                printf("%.1f\n", p)
            }
    '); do

echo "Percent of IWP = $Percent"

printf "%.1f 1 0\n" $Percent >> diff_IWP.txt

am IWP/ACT_DJF_5_1pwv_iwpmix$Percent.amc \
    >> diff_IWP.txt 2>>diff_IWP.err

printf "%.1f 10 0\n" $Percent >> diff_IWP.txt

am IWP/ACT_DJF_5_10pwv_iwpmix$Percent.amc \
    >> diff_IWP.txt 2>>diff_IWP.err

#break

done