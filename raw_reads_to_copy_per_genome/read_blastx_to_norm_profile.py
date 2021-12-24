import argparse
import os


def table_get_dictionary_between_columns(tbl_file, keycol_obi, valcol_obi, is_headered):
    dict_cols = {}
    tr = open(tbl_file)
    line = tr.readline()
    if is_headered:
        line = tr.readline()
    while line != '':
        fields = line.strip().split("\t")
        dict_cols[fields[keycol_obi - 1]] = fields[valcol_obi - 1]
        line = tr.readline()
    tr.close()
    return dict_cols


def median_from_list(list_float):
    sorted_list = sorted(list_float)
    num_elem = len(list_float)
    index_a = int(num_elem/2)
    median = sorted_list[index_a]
    if (num_elem % 2) == 0:
        median = (sorted_list[index_a] + sorted_list[index_a - 1]) / 2
    return median


def sum_list(list_of_int):
    sum_int = 0
    for int_value in list_of_int:
        sum_int += int_value
    return sum_int


def self_map_fa_titles(fasta):
    dict_self = {}
    fr = open(fasta, "r")
    for line in fr:
        if line.strip().startswith('>'):
            title = line.strip()[1:].split(' ')[0]
            dict_self[title] = title
    fr.close()
    return dict_self



parser = argparse.ArgumentParser(description = "An inferior strategy")
parser.add_argument("--sample_scg_blastx", dest="sample_scg_blastx_map_file", required=True, type=str, help="column 1 sample name, column 2 SCG blastx file(s; multiple blastx could be provided e.g. paired end each, separated by comma)")
parser.add_argument("--scg_db_fasta", dest="scg_db_fasta", required=True, type=str, help="the single-copy gene (SCG) database fasta, used in blastx step (for gene length)")
parser.add_argument("--scg_id_cut", dest="scg_id_cutoff", required=True, type=float, help="blastx HSP filtering based on this percent identity")
parser.add_argument("--scg_acc_map", dest="scg_acc_map_file", required=True, type=str, help="SCG database protein accession to SCG group (e.g. COG number) mapping; no header row, col 1 accession, col 2 group")
parser.add_argument("--sample_target_blastx", dest="sample_target_blastx_map_file", required=True, type=str, help="column 1 sample name, column 2 target gene blastx file(s; multiple blastx could be provided e.g. paired end each, separated by comma)")
parser.add_argument("--target_db_fasta", dest="target_db_fasta", required=True, type=str, help="the target gene (e.g. ARGs) database fasta, used in blastx step (for gene length)")
parser.add_argument("--target_id_cut", dest="target_id_cutoff", required=True, type=float, help="blastx HSP filtering based on this percent identity")
parser.add_argument("--target_acc_map", dest="target_acc_map_file", required=True, type=str, help="say NA if you don't have it; target database protein accession to final annotation mapping; col 1 accession, col 2 annotation")
parser.add_argument("--out", dest="output", required=True, type=str, help="")
args = parser.parse_args()
sample_scg_blastx_map_file = args.sample_scg_blastx_map_file
scg_db_fasta = args.scg_db_fasta
scg_id_cutoff = args.scg_id_cutoff
scg_acc_map_file = args.scg_acc_map_file
sample_target_blastx_map_file = args.sample_target_blastx_map_file
target_db_fasta = args.target_db_fasta
target_id_cutoff = args.target_id_cutoff
target_acc_map_file = args.target_acc_map_file
output = args.output


#
print("sample information")
sample_list = []
dict_sample_index = {}
sindex = 0
dict_sample_scg_blastx = table_get_dictionary_between_columns(sample_scg_blastx_map_file, 1, 2, False)
dict_sample_target_blastx = table_get_dictionary_between_columns(sample_target_blastx_map_file, 1, 2, False)
for keysample in dict_sample_scg_blastx:
    if keysample not in dict_sample_index:
        dict_sample_index[keysample] = sindex
        sample_list.append(keysample)
        sindex += 1
for keysample in dict_sample_target_blastx:
    if keysample not in dict_sample_index:
        dict_sample_index[keysample] = sindex
        sample_list.append(keysample)
        sindex += 1
#
num_sample = len(sample_list)
print(str(num_sample) + " samples")


# 
print("scg reference average length")
dict_scg_acc_scgid = table_get_dictionary_between_columns(scg_acc_map_file, 1, 2, False)     # DB property; Irrelevant to sample property
dict_scgid_num_acc = {}     # DB property; Irrelevant to sample property
dict_scgid_avg_length = {}  # DB property; Irrelevant to sample property
dict_scgid_read_count = {}  # {scgid : [sample index]}
for arbkey in dict_scg_acc_scgid:
    arbscgid = dict_scg_acc_scgid[arbkey]
    dict_scgid_num_acc[arbscgid] = 0
    dict_scgid_avg_length[arbscgid] = 0
    dict_scgid_read_count[arbscgid] = [0]*num_sample
#
fr = open(scg_db_fasta, "r")
line = fr.readline()
while line != '':
    if line.strip().startswith('>'):
        seqid = line.strip()[1:].split(' ')[0]
        length = 0
        line = fr.readline()
        while line != '':
            length += len(line.strip())
            line = fr.readline()
            if line.strip().startswith('>'):
                break
        if seqid in dict_scg_acc_scgid:
            scgid = dict_scg_acc_scgid[seqid]
            prev_num_acc = dict_scgid_num_acc[scgid]
            prev_avg_len = dict_scgid_avg_length[scgid]
            updated_num_acc = prev_num_acc + 1
            updated_avg_len = (float(prev_num_acc)*prev_avg_len + length)/float(updated_num_acc)
            dict_scgid_num_acc[scgid] = updated_num_acc
            dict_scgid_avg_length[scgid] = updated_avg_len
    else:
        line = fr.readline()
fr.close()
#
#
print("scg read count in the samples")
for sample in sample_list:
    sample_scg_blastx_str = dict_sample_scg_blastx[sample]
    sample_scg_blastx_split = []
    if sample_scg_blastx_str.find(',') == -1:
        sample_scg_blastx_split.append(sample_scg_blastx_str)
    else:
        sample_scg_blastx_split = sample_scg_blastx_str.split(',')
    #
    sample_index = dict_sample_index[sample]
    #
    for sample_scg_blastx in sample_scg_blastx_split:
        fr = open(sample_scg_blastx, "r")
        prev_qread = 'x'
        for line in fr:
            fields = line.strip().split("\t")
            qread = fields[0]
            ident = float(fields[2])
            hit_acc = fields[1]
            #
            if qread == prev_qread:
                continue
            prev_qread = qread
            #
            if ident < scg_id_cutoff:
                continue
            #
            if hit_acc not in dict_scg_acc_scgid:
                continue
            #
            hit_scgid = dict_scg_acc_scgid[hit_acc]
            read_count = dict_scgid_read_count[hit_scgid]
            read_count[sample_index] += 1
            dict_scgid_read_count[hit_scgid] = read_count
        fr.close()
    #
#
num_scgid = len(dict_scgid_num_acc)


# 
print("scg RPK median per sample")
dict_sample_scg_median = {}
for sample_index in range(num_sample):
    sample_list_scg_rpk = []
    for scgid in dict_scgid_read_count:
        sample_read_count = dict_scgid_read_count[scgid][sample_index]
        scg_avg_length = dict_scgid_avg_length[scgid]
        rpk = float(sample_read_count)*1000/float(scg_avg_length)
        sample_list_scg_rpk.append(rpk)
    median_rpk = median_from_list(sample_list_scg_rpk)
    dict_sample_scg_median[sample_list[sample_index]] = median_rpk
    print("  ---  " + sample_list[sample_index] + " median " + str(median_rpk))


#
print("target database reference prot lengths")
dict_target_acc_targetid = {}   # DB property; Irrelevant to sample property
if target_acc_map_file != 'NA':
    dict_target_acc_targetid = table_get_dictionary_between_columns(target_acc_map_file, 1, 2, False)
else:
    dict_target_acc_targetid = self_map_fa_titles(target_db_fasta)
dict_targetid_num_acc = {}      # DB property; Irrelevant to sample property
dict_targetid_avg_length = {}   # DB property; Irrelevant to sample property
dict_targetid_read_count = {}   #   {scgid : [sample index]}
for arbkey in dict_target_acc_targetid:
    arbtargetid = dict_target_acc_targetid[arbkey]
    dict_targetid_num_acc[arbtargetid] = 0
    dict_targetid_avg_length[arbtargetid] = 0
    dict_targetid_read_count[arbtargetid] = [0]*num_sample
#
fr = open(target_db_fasta, "r")
line = fr.readline()
while line != '':
    if line.strip().startswith('>'):
        seqid = line.strip()[1:].split(' ')[0]
        length = 0
        line = fr.readline()
        while line != '':
            length += len(line.strip())
            line = fr.readline()
            if line.strip().startswith('>'):
                break
        if seqid in dict_target_acc_targetid:
            targetid = dict_target_acc_targetid[seqid]
            prev_num_acc = dict_targetid_num_acc[targetid]
            prev_avg_len = dict_targetid_avg_length[targetid]
            updated_num_acc = prev_num_acc + 1
            updated_avg_len = (float(prev_num_acc)*prev_avg_len + length)/float(updated_num_acc)
            dict_targetid_num_acc[targetid] = updated_num_acc
            dict_targetid_avg_length[targetid] = updated_avg_len
    else:
        line = fr.readline()
fr.close()


print("target database read counts in the samples")
for sample in sample_list:
    sample_target_blastx_str = dict_sample_target_blastx[sample]
    sample_index = dict_sample_index[sample]
    #
    sample_target_blastx_split = []
    if sample_target_blastx_str.find(',') == -1:
        sample_target_blastx_split.append(sample_target_blastx_str)
    else:
        sample_target_blastx_split = sample_target_blastx_str.split(',')    
    #
    for sample_target_blastx in sample_target_blastx_split:
        fr = open(sample_target_blastx, "r")
        prev_qread = 'x'
        for line in fr:
            fields = line.strip().split("\t")
            qread = fields[0]
            ident = float(fields[2])
            hit_acc = fields[1]
            #
            if qread == prev_qread:
                continue
            prev_qread = qread
            #
            if ident < target_id_cutoff:
                continue
            #
            if hit_acc not in dict_target_acc_targetid:
                continue
            #
            hit_targetid = dict_target_acc_targetid[hit_acc]
            read_count = dict_targetid_read_count[hit_targetid]
            read_count[sample_index] += 1
            dict_targetid_read_count[hit_targetid] = read_count
        fr.close()
    #
num_targetid = len(dict_targetid_num_acc)


# filter for nonzero target
dict_targetid_nonzero = {}
num_nonzero_target = 0
num_zero_target = 0
for targetid in dict_targetid_avg_length:
    is_nonzero = False
    if dict_targetid_avg_length[targetid] > 0: 
        sample_read_count_sum = sum_list(dict_targetid_read_count[targetid])
        if sample_read_count_sum > 0:
            is_nonzero = True
    dict_targetid_nonzero[targetid] = is_nonzero
    if is_nonzero:
        num_nonzero_target += 1
    else:
        num_zero_target += 1
print("  non-zero target ref = " + str(num_nonzero_target))
print("  zero target ref = " + str(num_zero_target))


# normalized matrix
print("normalize and write output")
fw = open(output, "w")
fw.write("gene")
for sample_index in range(num_sample):
    fw.write("\t" + sample_list[sample_index])
fw.write("\n")
#
for targetid in dict_targetid_avg_length:
    #
    if dict_targetid_nonzero[targetid] == False:
        continue
    #
    avg_length = dict_targetid_avg_length[targetid]
    read_count_list = dict_targetid_read_count[targetid]
    #
    fw.write(targetid)
    for sample_index in range(num_sample):
        sample = sample_list[sample_index]
        sample_scg_median_rpk = dict_sample_scg_median[sample]
        sample_read_count = read_count_list[sample_index]
        sample_targetid_rpk = float(sample_read_count)*1000/float(avg_length)
        normalized_rpk = sample_targetid_rpk/sample_scg_median_rpk
        #
        fw.write("\t" + str(normalized_rpk))
    fw.write("\n")
    #
fw.close()


