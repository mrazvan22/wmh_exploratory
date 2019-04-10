config_file=$(shell pwd)/gasros.cfg
WMHP_folder=WMHP

register:
	cd ${WMHP_folder}; python3 setup.py ${config_file} ; ./run_pipeline.sh ${config_file}

cerebro:
	cd ${WMHP_folder}; Packages/nCerebro/bin/segment_WMH_affine.sh ${config_file}

cerebro_one_subj:
	cd ${WMHP_folder}; python3 segment_WMH_subject.py ${config_file} sub-000000856

freeview:
	 cd /data/vision/polina/projects/wmh/razvan/03/data/nifti/sub-000000023/images; freeview sub-000000023_affine_leuk_seg.nii.gz sub-000000023_flair_img_brainmask.nii.gz sub-000000023_flair_img_brain_matchwm.nii.gz sub-000000023_flair_img_brain_matchwm_upsample.nii.gz sub-000000023_flair_img_brain.nii.gz sub-000000023_flair_img_in_atlas_affine.nii.gz sub-000000023_leuk_seg_bin.nii.gz  /data/vision/polina/projects/wmh/incoming/2018_05_15/gasros_files/derivatives/sub-000000023/lesionmask/flair/manual/sub-000000023_flair_ax_01_seg_01.nii.gz
