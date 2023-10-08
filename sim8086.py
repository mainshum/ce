from bitstring import BitArray

opcodes = {
    '100010': 'mov'
}

mods = {
    '00': 'no di'
}


def interpret(bits):
    [opcode, d, w] = [opcodes[bits[0:6]], bits[6], bits[7]]

    # if (opcode in opcodes == False):
    #     raise Exception(f'{opcode} not recognized')

    print(opcode)
    pass


def encode_reg(reg, w):
    print(reg, w)
    match [reg, w]:
        case ['011', '1']: return 'bx'
        case _:
            raise Exception(f'(reg, w) = (${reg, w}) not found')


def encode_rm(mod, rm, w):
    match mod:
        case '11':
            match [rm, w]:
                case ['000', '0']: return 'al'
                case ['001', '1']: return 'cx'
                case ['011', '1']: return 'bx'
                case _: raise Exception(f'rm, w ${rm, w} combination not found')

        case _:
            raise Exception(f'mod ${mod} combination not found')


def main():
    # read binary file
    file = open('listing37', mode='rb')

    print('bits 16')

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

                print(f'{opcode} {rm_encoded}, {reg_encoded}')

            case _:
                raise Exception(f'opcode ${opcode} not found')
        # check what this specific byte represents

    file.close()


if __name__ == '__main__':
    main()
