#!/bin/bash
if [ ! -d read_blastx_cpg ]; then
	mkdir read_blastx_cpg
fi

scgblast_fmap="read_blastx_cpg/scg_blastx_fmap.txt"
if [ -f ${scgblast_fmap} ]; then
	rm ${scgblast_fmap}
fi
while read sample_id
do
	scg1="read_cpg_wf/${sample_id}/${sample_id}_1.blastx.cog.l_25"
	scg2="read_cpg_wf/${sample_id}/${sample_id}_2.blastx.cog.l_25"
	echo "${sample_id}	${scg1},${scg2}" >> ${scgblast_fmap}
done < sample_name.list

carblast_fmap="read_blastx_cpg/card_blastx_fmap.txt"
if [ -f ${carblast_fmap} ]; then
	rm ${carblast_fmap}
fi
while read sample_id
do
	card1="read_cpg_wf/${sample_id}/${sample_id}_1.blastx.card.l_25_i_90"
	card2="read_cpg_wf/${sample_id}/${sample_id}_2.blastx.card.l_25_i_90"
	echo "${sample_id}	${card1},${card2}" >> ${carblast_fmap}
done < sample_name.list


python /mnt/disks/permanentDisk/installation/python_codes/read_blastx_to_norm_profile.py --sample_scg_blastx ${scgblast_fmap} --sample_target_blastx ${carblast_fmap} --scg_db_fasta /mnt/disks/permanentDisk/databases/cog/cog-20.derep_cdhit_99.fasta --scg_id_cut 1 --scg_acc_map /mnt/disks/permanentDisk/databases/cog/mende_40_scg.acc_cogno.tsv --target_db_fasta /mnt/disks/permanentDisk/databases/CARD_AMR/v_202110/protein_fasta_protein_homolog_model.acc.fasta --target_id_cut 90 --target_acc_map /mnt/disks/permanentDisk/databases/CARD_AMR/v_202110/acc_argfam.tsv --out read_blastx_cpg/card_argfam_scg_cpg.tsv


