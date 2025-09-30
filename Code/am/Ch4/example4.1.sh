# Example 4.1 - Shell script to compute mass absorption coefficient
#               spectra in m^2 kg-1 for liquid water and ice in the
#               Rayleigh limit.
#!/bin/bash

for T in -60 -30 0; do
rm -f am_iwp_${T}C.out am_iwp_${T}C.err
am - <<- end > am_iwp_${T}C.out 2> am_iwp_${T}C.err
    f 0 GHz 1000 GHz 1 GHz
    output f GHz tau
    layer
    P 1 atm
    T ${T} C
    column iwp_abs_Rayleigh 1 kg*m^-2
end
done

for T in -30 0 30; do
rm -f am_lwp_${T}C.out am_lwp_${T}C.err
am - <<- end > am_lwp_${T}C.out 2> am_lwp_${T}C.err
    f 0 GHz 1000 GHz 1 GHz
    output f GHz tau
    layer
    P 1 atm
    T ${T} C
    column lwp_abs_Rayleigh 1 kg*m^-2
end
done
