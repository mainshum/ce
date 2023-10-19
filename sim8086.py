from bitstring import BitArray
from bitarray import util, bitarray
import sys

opcodes = {
    '100010': 'mov'
}

if len(sys.argv) < 2:
    raise Exception('Missing binary file to check against')


def match_rm_or_reg(rm_or_reg, w):
    match [rm_or_reg, w]:
        case ['000', '0']: return 'al'
        case ['000', '1']: return 'ax'

        case ['001', '0']: return 'cl'
        case ['001', '1']: return 'cx'

        case ['010', '0']: return 'dl'
        case ['010', '1']: return 'dx'

        case ['011', '0']: return 'bl'
        case ['011', '1']: return 'bx'

        case ['100', '0']: return 'ah'
        case ['100', '1']: return 'sp'

        case ['101', '0']: return 'ch'
        case ['101', '1']: return 'bp'

        case ['110', '0']: return 'dh'
        case ['110', '1']: return 'si'

        case ['111', '0']: return 'bh'
        case ['111', '1']: return 'di'

        case _:
            raise Exception(f'(reg / rm, w) = ({rm_or_reg, w}) not found')


def encode_reg(reg, w):
    return match_rm_or_reg(reg, w)


def encode_rm(mod, rm, w):
    match mod:
        case '11': return match_rm_or_reg(rm, w)

        case _: raise Exception(f'mod = {mod} combination not found')


def main():
    # read binary file
    asm_file = sys.argv[1]
    asm_compiled = asm_file.replace('.asm', '')

    output_lines = ['bits 16']

    file = open(asm_compiled, mode='rb')

    def mov_reg_to_reg(first_byte, file, output_lines):
        [d, w] = [first_byte[6], first_byte[7]]
        temp = BitArray(file.read(1)).b
        [mod, reg, rm] = [temp[0:2], temp[2: 5], temp[5:]]

        rm_encoded = encode_rm(mod, rm, w)
        reg_encoded = encode_reg(reg, w)

        output_lines.append(f'mov {rm_encoded}, {reg_encoded}')

    def mov_immediate_to_reg(first_byte, file, output_lines):
        [w, reg] = [first_byte[4], first_byte[5:]]
        snd_byte = BitArray(file.read(1)).b
        thrd_byte = BitArray(file.read(1)).b if w == '1' else ''
        # decode register and what to move inside of it
        reg_encoded = encode_reg(reg, w)

        data = int(thrd_byte + snd_byte, 2)

        print(thrd_byte + snd_byte)
        print(data)

        output_lines.append(f'mov {reg_encoded}, {data}')

    while True:
        byte = file.read(1)
        if not byte:
            break

        first_byte = BitArray(byte).b
        byte_list = list(first_byte)

        match byte_list:
            # register-to-register
            case ['1', '0', '0', '0', '1', '0', _, _]:
                mov_reg_to_reg(first_byte, file, output_lines)
            case ['1', '0', '1', '1', _, _, _, _]:
                mov_immediate_to_reg(first_byte, file, output_lines)
            case _:
                raise Exception(f'Unkown byte sequence: {byte_list}')

    file.close()

    result = '\n'.join(output_lines)

    # 3rd arg is for folder to push output to
    if (len(sys.argv) == 3):
        output_file_name = sys.argv[2]
        output_file = open(output_file_name, mode='w')
        output_file.write(result)
        output_file.close()


if __name__ == '__main__':
    main()
