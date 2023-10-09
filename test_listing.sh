echo Testing listing $1...

sim_output_bin=_test\/sim_output
correct_output_bin=_test\/listing_output
sim_output_asm=_test\/sim_output.asm

mkdir _test
python3 sim8086.py $1 $sim_output_asm

nasm $sim_output_asm -o $sim_output_bin
nasm $1 -o $correct_output_bin

cmp --quiet $correct_output_bin $sim_output_bin

if [ $? -eq 0 ]
then 
    echo Success!
fi

rm -rf _test