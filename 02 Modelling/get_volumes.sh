
# arg: input directory of images, job name, gender 

# make input directory under "data/jobname", should have
# input and output folder
jobname=$1
gender=$2
lookup_table_location=$3

for img in $jobname/results/results/*
do
    echo "JOB RUNNING: $img/"

    python smplify-x-sil/smplifyx/pose_model_for_simulation.py --pkl $img/000.pkl \
        --posed_mesh $img/posed.obj \
        --skeleton_out $img/posed.json  \
        --config smplify-x-sil/cfg_files/fit_smplx.yaml \
        --gender $gender \
        --data_folder NaN \
        --output_folder NaN \
        --visualize="True" \
        --model_folder models \
        --vposer_ckpt vposer_v1_0 \
        --part_segm_fn smplify-x-sil/smplx_parts_segm.pkl \
        --use_cuda="False"

done

python get_volume_from_mesh.py --results_file  $jobname/results/results \
--csv_output_file $jobname/results/overall_results.csv \
--lookup_table_location $lookup_table_location \

echo "JOB COMPLETED"
