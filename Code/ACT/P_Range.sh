#use Script to show the diff Tbase

rm -f diff_Pbase.txt
rm -f diff_Pbase.err

#!/bin/bash
# float sequence
for Pchage in $(awk '
        BEGIN {
            for (p = 0.8; p <= 1.3; p += 0.2)
                printf("%.1f\n", p)
            }
    '); do

echo "Pchage = $Pchage"

printf "%.1f 1.0 0\n" $Pchage >> diff_Pbase.txt

am Pmode/ACT_DJF_5_1.0pwv_P$Pchage.amc \
    >> diff_Pbase.txt 2>>diff_Pbase.err

printf "%.1f 5.5 0\n" $Pchage >> diff_Pbase.txt

am Pmode/ACT_DJF_5_5.5pwv_P$Pchage.amc \
    >> diff_Pbase.txt 2>>diff_Pbase.err


printf "%.1f 10.0 0\n" $Pchage >> diff_Pbase.txt

am Pmode/ACT_DJF_5_10.0pwv_P$Pchage.amc \
    >> diff_Pbase.txt 2>>diff_Pbase.err

#break

done