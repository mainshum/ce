if [ -z $1 ] 
then 
    echo Test listing needs to be provided as param!
    exit 1
fi

echo Testing listing $1...

# $1 = listing_x.asm
# 1 listing_x.asm -> $correct_output_bin (nasm)
# 2 $correct_output_bin -> $sim_output_asm (python)
# 3 $sim_output_asm -> $sim_output_bin (nasm)
# 4 cmp $correct_output_bin vs $sim_output_bin

# sim
sim_output_bin=sim_output
correct_output_bin=listing_output
sim_output_asm=sim_output.asm

# 1. create proper output 
nasm $1 -o $correct_output_bin

# 2. create our own output
python3 sim8086.py $correct_output_bin $sim_output_asm
# 3. compile python's asm 
nasm $sim_output_asm -o $sim_output_bin

cmp --quiet $correct_output_bin $sim_output_bin

if [ $? -eq 0 ]
then 
    echo Success!
fi

# cleanup
rm sim_output
rm listing_output
rm $sim_output_asm