#use Script to show the PWV 1 to 10 pwv step by 1

rm -f 1_10pwv_inp.txt
rm -f 1_10pwv_inp.err
#!/bin/bash

# float sequence
for PWV in $(awk '
        BEGIN {
            for (p = 1.0; p <= 10.0; p++)
                printf("%f\n", p)

            }
    '); do

trop_h2o_scale_factor=$(awk -v n="$PWV" 'BEGIN { print n * 3.005 }')

printf "%f 0\n" $PWV >> 1_10pwv_inp.txt

am ACT_DJF_5_1_10.amc  10 GHz  200 GHz  10 MHz  30 deg  $trop_h2o_scale_factor \
    >> 1_10pwv_inp.txt 2>>1_10pwv_inp.err

done