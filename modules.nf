process MINIMAP2_ALIGN {
  cpus "${params.minimap2_threads}"
  tag "${sampleid}"
  label "xlarge2"

  container 'quay.io/biocontainers/minimap2:2.24--h7132678_1'

  input:
  tuple val(sampleid), path(fastq)
  path(reference)
  output:
  tuple val(sampleid), path(fastq), path("${sampleid}_unaligned_ids.txt"), emit: sequencing_ids

  def minimap_options = (params.minimap_options) ? " ${params.minimap_options}" : ''

  script:
  """
  minimap2 -ax ${minimap_options} -uf -k14 ${reference} ${fastq} -t ${params.minimap_threads} > ${sampleid}.sam
  awk '\$6 == "*" { print \$0 }' ${sampleid}.sam | cut -f1 | uniq >  ${sampleid}_unaligned_ids.txt
  """
}

process EXTRACT_READS {
  tag "${sampleid}"
  label "medium"

  container = 'docker://quay.io/biocontainers/seqtk:1.3--h5bf99c6_3'

  input:
  tuple val(sampleid), path(fastq), path(unaligned_ids)
  output:
  tuple val(sampleid), path("*_unaligned.fastq"), emit: unaligned_fq

  script:
  """
  seqtk subseq ${fastq} ${unaligned_ids} > ${fastq.baseName}_unaligned.fastq
  """
}

/*
process MAP_BACK_TO_ASSEMBLY {
  cpus "${params.minimap2_threads}"
  tag "${sampleid}"
  label "large"
  publishDir "$params.outdir/$sampleid",  mode: 'copy', pattern: '*.sam'

  container 'quay.io/biocontainers/minimap2:2.24--h7132678_1'

  input:
  tuple val(sampleid), path(fastq), path(assembly)
  output:
  path "${sampleid}.sam"
  tuple val(sampleid), path(fastq), path("${sampleid}_unaligned_ids.txt"), emit: unmapped_ids

  script:
  """
  minimap2 -ax splice -uf -k14 ${assembly} ${fastq} > ${sampleid}.sam
  awk '\$6 == "*" { print \$0 }' ${sampleid}.sam | cut -f1 | uniq >  ${sampleid}_unaligned_ids.txt
  """
}
*/

process FASTQ2FASTA {
  tag "${sampleid}"
  label "medium"
  //publishDir "$params.outdir/$sampleid/fasta", mode: 'copy', pattern: '*.fasta'

  container = 'docker://quay.io/biocontainers/seqtk:1.3--h7132678_4'

  input:
  tuple val(sampleid), path(fastq)
  output:
  tuple val(sampleid), path("${sampleid}.fasta"), emit: fasta

  script:
  """
  seqtk seq -A -C ${fastq} > ${sampleid}.fasta
  """
}

process NANOPLOT {
  publishDir "${params.outdir}/${sampleid}/nanoplot",  pattern: '*.html', mode: 'link', saveAs: { filename -> "${sampleid}_$filename" }
  publishDir "${params.outdir}/${sampleid}/nanoplot",  pattern: '*.NanoStats.txt', mode: 'link', saveAs: { filename -> "${sampleid}_$filename" }
  tag "${sampleid}"
  cpus 2

  container 'quay.io/biocontainers/nanoplot:1.41.0--pyhdfd78af_0'
  
  input:
    tuple val(sampleid), path(sample)
  output:
    path("*.html")
    path("*NanoStats.txt")
  
  script:
  if (sample.endsWith("quality_trimmed.fastq.gz")) {
    """
    NanoPlot -t 2 --fastq ${sample} --prefix filtered_ --plots dot --N50
    """
  }
  else {
    """
    NanoPlot -t 2 --fastq ${sample} --prefix raw_ --plots dot --N50
    """
  }
}