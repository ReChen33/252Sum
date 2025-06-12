#use Script to show the diff Tbase

rm -f diff_Tbase_inp.txt
rm -f diff_Tbase_inp.err

#!/bin/bash
# float sequence
for Tchage in $(awk '
        BEGIN {
            for (p = -20.0; p <= +20.1; p += +10.0)
                printf("%+.1f\n", p)
            }
    '); do

echo "Tchage = $Tchage"

printf "%+.1f 0\n" $Tchage >> diff_Tbase_inp.txt

am ACT_DJF_5_T_R_$Tchage.amc \
    >> diff_Tbase_inp.txt 2>>diff_Tbase_inp.err

done