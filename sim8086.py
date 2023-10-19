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


def main():
    # read binary file
    asm_file = sys.argv[1]
    asm_compiled = asm_file.replace('.asm', '')

    output_lines = ['bits 16']

    file = open(asm_compiled, mode='rb')

    def rm_in_effective_address_calc(rm):
        match rm:
            case '000': return '[bx + si '
            case '001': return '[bx + di '
            case '010': return '[bp + si '
            case '011': return '[bp + di '
            case '100': return '[si '
            case '101': return '[di '
            case '110': return '[bp '
            case '111': return '[bx '
            case _: raise Exception(f'rm={rm} not found')

    def mov_reg_to_reg(cur_byte, file, output_lines):
        temp = BitArray(file.read(1)).b

        [d, w] = [cur_byte[6], cur_byte[7]]
        [mod, reg, rm] = [temp[0:2], temp[2: 5], temp[5:]]

        def calc_effective(mod, rm, file):
            leading = rm_in_effective_address_calc(rm)
            if mod == '00':
                return f'{leading}]'

            snd_byte = BitArray(file.read(1)).b
            thrd_byte = BitArray(file.read(1)).b if mod == '10' else ''

            if mod == '01':
                return f'{leading} + {int(snd_byte, 2)}]'
            else:
                return f'{leading} + {int(thrd_byte + snd_byte, 2)}]'

        reg_encoded = encode_reg(reg, w)

        match mod:
            case '11': output_lines.append(f'mov {match_rm_or_reg(rm, w)}, {reg_encoded}')
            case _: output_lines.append(f'mov {reg_encoded}, {calc_effective(mod, rm, file)}')

        # output_lines.append(f'mov {rm_encoded}, {reg_encoded}')

    def mov_immediate_to_reg(cur_byte, file, output_lines):
        pass

    def mov_immediate_to_reg(cur_byte, file, output_lines):
        [w, reg] = [cur_byte[4], cur_byte[5:]]
        snd_byte = BitArray(file.read(1)).b
        thrd_byte = BitArray(file.read(1)).b if w == '1' else ''
        # decode register and what to move inside of it
        reg_encoded = encode_reg(reg, w)

        data = int(thrd_byte + snd_byte, 2)

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
