#!/bin/bash

rm -f total.txt
rm -f total.err

printf "0 1.0 0\n" >> total.txt

am ACT_DJF_5_T_R.amc \
>> total.txt 2>>total.err

printf "1 1.0 0\n" >> total.txt

am ACT_DJF_5_T_R_total.amc \
>> total.txt 2>>total.err
