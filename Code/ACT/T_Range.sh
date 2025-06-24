#use Script to show the diff Tbase

rm -f diff_Tbase_inp.txt
rm -f diff_Tbase_inp.err

#!/bin/bash
# float sequence
for Tchage in $(awk '
        BEGIN {
            for (p = 0.5; p <= 1.21; p += 0.1)
                printf("%+.1f\n", p)
            }
    '); do

echo "Tchage = $Tchage"

printf "%+.1f 1 0\n" $Tchage >> diff_Tbase_inp.txt

am Tmode/ACT_DJF_5_T_R1_1pwv_$Tchage.amc \
    >> diff_Tbase_inp.txt 2>>diff_Tbase_inp.err

# printf "%+.1f 10 0\n" $Tchage >> diff_Tbase_inp.txt

# am Tmode/ACT_DJF_5_T_R1_10pwv_$Tchage.amc \
#     >> diff_Tbase_inp.txt 2>>diff_Tbase_inp.err

#break

done