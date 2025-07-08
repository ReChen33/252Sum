#use Script to show the PWV 1 to 10 pwv step by 1

rm -f 0.1_1pwv_inp.txt
rm -f 0.1_1pwv_inp.err
#!/bin/bash

# float sequence
for PWV in $(awk '
        BEGIN {
            for (p = 0.1; p <= 1; p += 0.1)
                printf("%f\n", p)

            }
    '); do

trop_h2o_scale_factor=$(awk -v n="$PWV" 'BEGIN { print n * 3.005 }')

echo "PWV: $PWV, scale factor: $trop_h2o_scale_factor"

printf "%f 0 0\n" $PWV >> 0.1_1pwv_inp.txt

am ACT_DJF_5_1_10.amc  10 GHz  1000 GHz  1000 MHz  30 deg  $trop_h2o_scale_factor \
    >> 0.1_1pwv_inp.txt 2>>0.1_1pwv_inp.err

done