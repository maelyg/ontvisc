#!/usr/bin/env python
import argparse
import pandas as pd
import numpy as np
import glob
import time

def main():
    ################################################################################
    parser = argparse.ArgumentParser(description="Load VirReport pipeline results")
    # All the required arguments #
    parser.add_argument("--threshold", type=float)
    
    args = parser.parse_args()
    threshold = args.threshold
    
    timestr = time.strftime("%Y%m%d-%H%M%S")

    run_data = pd.DataFrame()
    
    for fl in glob.glob("*_top_blast_with_cov_stats.txt"):
        sample_data = pd.read_csv(fl, header=0, sep="\t",index_col=None)
        run_data = pd.concat([run_data, sample_data], axis = 0)
    print(run_data)
    
    if len(run_data) == 0:
        print("DataFrame is empty!")
        dummy = open(("detection_summary_" + timestr + ".txt"), "w")
        dummy.write("sample\tspecies\treference_title\treference_accession\treference_length\tquery_id\tquery_length\tpc_ident\torientation\tevalue\tbitscore\tquery_coverage\tread_count\tmean_cov\tRPKM\tRPM\tPCT_5X\tPCT_10X\tPCT_20X\tcontamination_flag")
        dummy.close()
    else:
        run_data = run_data[["sample","species","reference_title","reference_accession","reference_length","query_id","query_length","pc_ident","orientation","evalue","bitscore","query_coverage","read_count","mean_cov","RPKM", "RPM", "PCT_5X","PCT_10X","PCT_20X"]]
        contamination_flag(run_data,threshold)
        run_data = run_data.sort_values(["sample", "species"], ascending = (True, True))
        run_data.drop(["reference_title", "RPKM_max", "threshold_value"], axis=1, inplace=True)
        run_data.fillna(0, inplace=True)
        run_data.to_csv("detection_summary_" + timestr + ".txt", index=None, sep="\t")


def contamination_flag(df, threshold):
    df["RPKM"] = df["RPKM"].astype(float)
    df["RPKM_max"] = df.groupby(["species"])["RPKM"].transform(max)
    df["RPKM_max"] =  df["RPKM_max"].round(1)
    df["threshold_value"]=df["RPKM_max"]*threshold
    df["threshold_value"] = df["threshold_value"].round(1)
    df["contamination_flag"] = np.where(df["RPKM"] < df["threshold_value"], True, False)
    df["contamination_flag"] = np.where(df["RPKM_max"] <= 10, "NA", df["contamination_flag"])

if __name__ == "__main__":
    main()