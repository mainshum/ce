from bitstring import BitArray
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
    asm_compiled = sys.argv[1]
    # asm_compiled = asm_file.replace('.asm', '')

    output_lines = ['bits 16']

    file = open(asm_compiled, mode='rb')

    while True:
        byte = file.read(1)
        if not byte:
            break

        first_byte = BitArray(byte).b
        [opcode, d, w] = [opcodes[first_byte[0:6]], first_byte[6], first_byte[7]]

        # opcode tells us how many more bytes to fetch to figure out the instruction

        match opcode:
            case 'mov':  # 3 more bytes
                temp = BitArray(file.read(1)).b
                # [mod0, mod1, reg2, reg3, reg4, rm5, rm6, rm7]
                [mod, reg, rm] = [temp[0:2], temp[2: 5], temp[5:]]

                rm_encoded = encode_rm(mod, rm, w)
                reg_encoded = encode_reg(reg, w)

                output_lines.append(f'{opcode} {rm_encoded}, {reg_encoded}')

            case _:
                raise Exception(f'opcode ${opcode} not found')
        # check what this specific byte represents

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
