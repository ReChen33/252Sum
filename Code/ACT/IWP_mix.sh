#use Script to show the diff PWV with diff mixing ratio of IWP

rm -f diff_IWP10test.txt
rm -f diff_IWP10test.err

#!/bin/bash
# float sequence
for Percent in $(awk '
        BEGIN {
            for (p = 0.3; p <= 0.91; p += 0.3)
                printf("%.1f\n", p)
            
            }
    '); do

#for (p = 1.0; p < 1.1; p += 0.1)
#                printf("%.1f\n", p)

echo "Percent of IWP = $Percent"

# printf "%.1f 0.1 0\n" $Percent >> diff_IWP_0.1-1_full.txt

# am IWP/ACT_DJF_5_0.1pwv_iwpmix$Percent.amc \
#     >> diff_IWP_0.1-1_full.txt 2>>diff_IWP_0.1-1_full.err

printf "%.1f 10 0\n" $Percent >> diff_IWP10test.txt

am IWP/ACT_DJF_5_10pwv_iwpmix$Percent.amc \
    >> diff_IWP10test.txt 2>>diff_IWP10test.err


#break

done