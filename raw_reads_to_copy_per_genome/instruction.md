# Workflow: From raw metagenome sequencing reads to normalized abundance profiles of target reference proteins

## 1. Workflow description

### 1.1 Scenario

### 1.2 What sequencing reads

### 1.3 What database you will use

### 1.4 What profile you will get

### 1.5 What is normalized abundance



## 2. Installations 

### 2.1 diamond

Go to: https://github.com/bbuchfink/diamond

### 2.2. some java classes used in the workflow

```
javac ArgumentBean.java
javac BlastTabularReaderLkh.java
javac BlastResultFilterLkh.java
```

## 3. Database downloads

### 3.1 target database (example = CARD)

### 3.2 COG database

### 3.3 Database preprocessing


## 4. Prepare working directory file structure

### 4.1 Recommended structure (the one used in the example commands)


## 5. Run the analysis

For each sample, there are two read fastq files.\
There are two reference databases to blastx against.\
Hence we'll run the following four commands per each sample

```
blastx_cog1="read_cpg_wf/${sample_name}/${sample_name}_1.blastx.cog"
blastx_cog2="read_cpg_wf/${sample_name}/${sample_name}_2.blastx.cog"
blastx_card1="read_cpg_wf/${sample_name}/${sample_name}_1.blastx.card"
blastx_card2="read_cpg_wf/${sample_name}/${sample_name}_2.blastx.card"

diamond2 blastx -p 3 -f 6 --fast -d PATH_TO_COG/cog-20.derep_cdhit_99.dmnd2.dmnd --unfmt fastq -q raw_read/${sample_name}_1.fastq -e 1e-10 -k 1 --query-cover 80 -o ${blastx_cog1}
diamond2 blastx -p 3 -f 6 --fast -d PATH_TO_COG/cog-20.derep_cdhit_99.dmnd2.dmnd --unfmt fastq -q raw_read/${sample_name}_2.fastq -e 1e-10 -k 1 --query-cover 80 -o ${blastx_cog2}
diamond2 blastx -p 3 -f 6 -d PATH_TO_CARD/protein_fasta_protein_homolog_model.acc.diamond2.dmnd --unfmt fastq -q raw_read/${sample_name}_1.fastq -e 1e-10 -k 1 --query-cover 80 -o ${blastx_card1}
diamond2 blastx -p 3 -f 6 -d PATH_TO_CARD/protein_fasta_protein_homolog_model.acc.diamond2.dmnd --unfmt fastq -q raw_read/${sample_name}_2.fastq -e 1e-10 -k 1 --query-cover 80 -o ${blastx_card2}
```

The blastx tab outputs can be post-processed, i.e., filtering the alignments by alignment length and identity.\
For each sample, the following commands could be applied for example: 

```
java -cp PATH_TO_JAVA_CLASS_DIR BlastResultFilterLkh -in read_cpg_wf/${sample_id}/${sample_id}_1.blastx.cog -lengthCut 25 -out read_cpg_wf/${sample_id}/${sample_id}_1.blastx.cog.l_25
java -cp PATH_TO_JAVA_CLASS_DIR BlastResultFilterLkh -in read_cpg_wf/${sample_id}/${sample_id}_2.blastx.cog -lengthCut 25 -out read_cpg_wf/${sample_id}/${sample_id}_2.blastx.cog.l_25
java -cp PATH_TO_JAVA_CLASS_DIR BlastResultFilterLkh -in read_cpg_wf/${sample_id}/${sample_id}_1.blastx.card -lengthCut 25 -idcut 90 -out read_cpg_wf/${sample_id}/${sample_id}_1.blastx.card.l_25_i_90
java -cp PATH_TO_JAVA_CLASS_DIR BlastResultFilterLkh -in read_cpg_wf/${sample_id}/${sample_id}_2.blastx.card -lengthCut 25 -idcut 90 -out read_cpg_wf/${sample_id}/${sample_id}_2.blastx.card.l_25_i_90

python table_translate_single_column.py -i read_cpg_wf/${sample_id}/${sample_id}_1.blastx.cog.l_25 -c 2 -d mende_40_scg.acc_cogno.tsv --dk 1 --dt 2 --ex_untranslated -o read_cpg_wf/${sample_id}/${sample_id}_1.blastx.cog.l_25.scg
python table_translate_single_column.py -i read_cpg_wf/${sample_id}/${sample_id}_2.blastx.cog.l_25 -c 2 -d mende_40_scg.acc_cogno.tsv --dk 1 --dt 2 --ex_untranslated -o read_cpg_wf/${sample_id}/${sample_id}_2.blastx.cog.l_25.scg
python table_translate_single_column.py -i read_cpg_wf/${sample_id}/${sample_id}_1.blastx.card.l_25_i_90 -d PATH_TO_CARD/aro_index.tsv -c 2 --dk 7 --dt 9 -o read_cpg_wf/${sample_id}/${sample_id}_1.blastx.card.l_25_i_90.argfam
python table_translate_single_column.py -i read_cpg_wf/${sample_id}/${sample_id}_2.blastx.card.l_25_i_90 -d PATH_TO_CARD/aro_index.tsv -c 2 --dk 7 --dt 9 -o read_cpg_wf/${sample_id}/${sample_id}_2.blastx.card.l_25_i_90.argfam

```


Blastx results can be combined into cpg profiles.
```
```
