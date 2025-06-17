#use Script to show the diff Tbase
#!/bin/bash

rm -f LWP.txt
rm -f LWP.err

# float sequence
for Tchage in $(awk '
        BEGIN {
            for (p = -20.0; p <= +20.1; p += +10.0)
                printf("%+.1f\n", p)
            }
    '); do

echo "Tchage = $Tchage"

printf "739 1.0 0\n" >> LWP.txt

am LWP/ACT_DJF_5_T_R_1pwv_lwp_$Tchage.amc \
>> LWP.txt 2>>LWP.err

# printf "739 10.0 0\n" $Pchage >> LWP.txt

# am ACT_DJF_5_10.0pwv_iwp.amc \
# >> LWP.txt 2>>LWP.err
done