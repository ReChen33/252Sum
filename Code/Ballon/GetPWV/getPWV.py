import os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob


def PWV_array(rho, g, m_mix_kgkg, p_pa):
    PWV_arr = np.zeros(len(p_pa) - 1)
    PWV_sum = 0.0
    for i in range(len(p_pa) - 1):
        sum_m_P_rho = 0.5 * (m_mix_kgkg[i+1] + m_mix_kgkg[i]) * np.abs(p_pa[i+1] - p_pa[i])
        PWV_meter = sum_m_P_rho / (g * rho)      # m
        PWV_arr[i] = PWV_meter * 1000.0          # mm
        PWV_sum += PWV_arr[i]
    return PWV_arr, PWV_sum

def PWVCumuSum(PWV_arr):
    out = np.zeros(len(PWV_arr))
    out[0] = PWV_arr[0]
    for i in range(1, len(PWV_arr)):
        out[i] = out[i-1] + PWV_arr[i]
    return out


def _norm(s: str) -> str:
    # Uppercase and keep only letters/numbers, replace runs with single underscore
    s = re.sub(r'[^A-Za-z0-9]+', '_', s.upper()).strip('_')
    return s

def get_required_columns(df: pd.DataFrame):
    cols = {_norm(c): c for c in df.columns}
    # try common variants
    pres_key = None
    mixr_key = None
    for k in ("PRES", "PRESSURE_HPA", "PRESSURE", "P_HPA"):
        if k in cols:
            pres_key = cols[k]; break
    for k in ("MIXR", "MIXING_RATIO_G_KG", "MIXING_RATIO", "MIXINGRATIO_G_KG"):
        if k in cols:
            mixr_key = cols[k]; break
    if pres_key is None or mixr_key is None:
        missing = []
        if pres_key is None: missing.append("pressure (e.g., PRES or PRESSURE_HPA)")
        if mixr_key is None: missing.append("mixing ratio (e.g., MIXR or MIXING RATIO_G/KG)")
        raise KeyError(f"Missing columns: {', '.join(missing)}")
    return pres_key, mixr_key


g = 9.8
rho_w_liq = 1000.0
folder = os.getcwd()  
csv_files = sorted(glob(os.path.join(folder, "data", "*.csv")))

summary = []  # collect totals

for csv_path in csv_files:
    try:
        df = pd.read_csv(csv_path, comment="#", skip_blank_lines=True)
        # normalize duplicate spacing in headers
        df.columns = [c.strip() for c in df.columns]
        pres_col, mixr_col = get_required_columns(df)

        # clean and keep rows with required numeric values
        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[pres_col, mixr_col])

        # sort so x-axis goes high Pa -> low Pa (left -> right). No x inversion later.
        df = df.sort_values(pres_col, ascending=False).reset_index(drop=True)

        # arrays + units
        p_hpa = df[pres_col].to_numpy(dtype=float)
        p_pa  = p_hpa * 100.0               # hPa -> Pa
        m_mix_gkg = df[mixr_col].to_numpy(dtype=float)
        m_mix_kgkg = m_mix_gkg * 1e-3       # g/kg -> kg/kg

        if len(p_pa) < 2:
            print(f"[skip] {os.path.basename(csv_path)}: not enough rows.")
            continue

        # midpoints and widths
        pa_mid = 0.5 * (p_pa[:-1] + p_pa[1:])
        dp = np.abs(np.diff(p_pa))

        # PWV
        PWV_arr, PWV_sum = PWV_array(rho_w_liq, g, m_mix_kgkg, p_pa)
        PWV_cumu = PWVCumuSum(PWV_arr)

       
        fig, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)

        gap = 0.95  # 95% width -> 5% gap
        axes[0].bar(pa_mid, PWV_arr, width=dp*gap, alpha=0.8, edgecolor="k", color='b')
        axes[0].set_ylabel("PWV per layer (mm)")
        axes[0].set_title(f"{os.path.basename(csv_path)}  •  Total PWV = {PWV_sum:.2f} mm")

        axes[1].bar(pa_mid, PWV_cumu, width=dp*gap, alpha=0.8, edgecolor="k", color='b')
        axes[1].set_ylabel("Cumulative PWV (mm)")
        axes[1].set_xlabel("Pressure (Pa)")
        axes[1].grid(True, ls=":")
        axes[0].legend(["PWV per layer"], fontsize=10)
        axes[1].legend(["Cumulative PWV"], fontsize=10, loc='lower left')

        plt.tight_layout()

        # save figure next to file
        out_png = os.path.splitext(csv_path)[0] + "_pwv.png"
        plt.savefig(out_png, dpi=200)
        plt.close(fig)

        # record summary
        summary.append({
            "file": os.path.basename(csv_path),
            "rows_used": len(df),
            "total_pwv_mm": round(PWV_sum, 3)
        })
        print(f"[ok] {os.path.basename(csv_path)} -> {out_png}  (PWV={PWV_sum:.2f} mm)")

    except Exception as e:
        print(f"[error] {os.path.basename(csv_path)}: {e}")

# write a summary CSV
if summary:
    summary_df = pd.DataFrame(summary)
    summary_csv = os.path.join(folder, "pwv_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"\nSummary written to: {summary_csv}")
else:
    print("\nNo valid CSVs processed.")
