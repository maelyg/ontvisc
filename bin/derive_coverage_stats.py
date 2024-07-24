#!/usr/bin/env python
import argparse
import pandas as pd
from functools import reduce
from glob import glob
from subprocess import PIPE

def main():
    ################################################################################
    parser = argparse.ArgumentParser(description="Load blast and coverage stats summary")
    parser.add_argument("--sample", type=str, required=True, help='provide sample name')
    args = parser.parse_args()
    sample_name = args.sample
    
    coverm_all = pd.DataFrame()
    blast_df = pd.DataFrame()
    PCTs_all = pd.DataFrame()
    for blast_results in glob("*_blastn_top_viral_spp_hits.txt"):
        blastn_results = pd.read_csv(blast_results, sep="\t", index_col=False)
        blast_df = blastn_results[["species", "stitle", "qseqid", "sacc", "length", "pident", "sstrand", "evalue", "bitscore", "qcovs"]]
        blast_df.columns = ["species", "reference_title", "query_id", "reference_accession", "query_length", "pc_ident", "orientation", "evalue", "bitscore", "query_coverage"]
        sacc_list = blast_df["reference_accession"].tolist()
        for sacc in sacc_list:
            for coverm_results in glob("*_coverm_summary.txt"):
                if sacc in str(coverm_results):
                    coverm_results = pd.read_csv(coverm_results, sep="\t", index_col=False)
                    coverm_results.columns = ["genome", "read_count", "mean_cov", "variance", "RPKM", "%_bases_cov", "reference_length"]
                    coverm_results["reference_title"] = sacc
                    coverm_df=coverm_results[["reference_title", "read_count", "mean_cov", "RPKM", "reference_length"]]
                    coverm_df["RPKM"] = coverm_df["RPKM"].round(1)
                    coverm_df["mean_cov"] = coverm_df["mean_cov"].round(1)
    
                    coverm_all = pd.concat([coverm_all, coverm_df], axis = 0)
                    print(coverm_all)

            for mosdepth_results in glob("*mosdepth.global.dist.txt"):
                if sacc in str(mosdepth_results):
                    mosdepth_results = pd.read_csv(mosdepth_results, sep="\t", index_col=False)
                    mosdepth_results.columns = ["genome", "pc_coverage", "depth"]
                    PCT_5X = mosdepth_results.loc[(mosdepth_results['pc_coverage']==5) & (mosdepth_results['genome'].str.contains(sacc)), ['depth']].rename(columns={"depth": "PCT_5X"})
                    PCT_5X["PCT_5X"] = PCT_5X["PCT_5X"].round(2)
                    PCT_5X['reference_title'] = sacc
                    
                    PCT_10X = mosdepth_results.loc[(mosdepth_results['pc_coverage']==10) & (mosdepth_results['genome'].str.contains(sacc)), ['depth']].rename(columns={"depth": "PCT_10X"})
                    PCT_10X['reference_title'] = sacc
                    PCT_10X["PCT_10X"] = PCT_10X["PCT_10X"].round(2)
                    PCT_20X = mosdepth_results.loc[(mosdepth_results['pc_coverage']==20) & (mosdepth_results['genome'].str.contains(sacc)), ['depth']].rename(columns={"depth": "PCT_20X"})
                    PCT_20X['reference_title'] = sacc
                    PCT_20X["PCT_20X"] = PCT_20X["PCT_20X"].round(2)
                    dfs = (PCT_5X, PCT_10X, PCT_20X)

                    PCTs = reduce(lambda left,right: pd.merge(left,right,on=["reference_title"],how='outer'), dfs)
                    PCTs_all = pd.concat([PCTs_all, PCTs], axis = 0)
                    print(PCTs_all)

        summary_dfs = (blast_df, coverm_all, PCTs_all)
        blast_df = reduce(lambda left,right: pd.merge(left,right,on=["reference_title"],how='outer').fillna("NA"), summary_dfs)
        blast_df = blast_df[["species", "reference_title", "reference_accession", "reference_length", "query_id", "query_length", "pc_ident", "orientation", "evalue", "bitscore", "query_coverage", "read_count", "mean_cov", "RPKM", "PCT_5X", "PCT_10X", "PCT_20X"]]
        blast_df.insert(0, "sample", sample_name)

        print(blast_df)
        blast_df.to_csv(str(sample_name) + "_top_blast_with_cov_stats.txt", index=None, sep="\t")
        
if __name__ == "__main__":
    main()