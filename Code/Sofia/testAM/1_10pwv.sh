
rm -f 0.1_1pwv_inp_SP.txt
rm -f 0.1_1pwv_inp_SP.err
#!/bin/bash

# float sequence
for PWV in $(awk '
        BEGIN {
            for (p = 0.1; p <= 1.1; p += 0.912)
                printf("%f\n", p)

            }
    '); do

trop_h2o_scale_factor=$(awk -v n="$PWV" 'BEGIN { print n * 2.33 }')

echo "PWV: $PWV, scale factor: $trop_h2o_scale_factor"

printf "%f 0 0\n" $PWV >> 0.1_1pwv_inp_SP.txt

am SPole_annual_50.amc  10 GHz  500 GHz  100 MHz  30 deg  $trop_h2o_scale_factor \
    >> 0.1_1pwv_inp_SP.txt 2>>0.1_1pwv_inp_SP.err

done