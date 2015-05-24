
from ..isa import Register, Syntax


class ArmRegister(Register):
    def __init__(self, name, num=None):
        super().__init__(name)
        self._num = num

    def __repr__(self):
        if self.is_colored:
            return '{}={}'.format(self.name, self.color)
        else:
            return self.name

    syntaxi = 'reg', [
        Syntax(['r0'], new_func=lambda: R0),
        Syntax(['r1'], new_func=lambda: R1),
        Syntax(['r2'], new_func=lambda: R2),
        Syntax(['r3'], new_func=lambda: R3),
        Syntax(['r4'], new_func=lambda: R4),
        Syntax(['r5'], new_func=lambda: R5),
        Syntax(['r6'], new_func=lambda: R6),
        Syntax(['r7'], new_func=lambda: R7),
        Syntax(['r8'], new_func=lambda: R8),
        Syntax(['r9'], new_func=lambda: R9),
        Syntax(['r10'], new_func=lambda: R10),
        Syntax(['r11'], new_func=lambda: R11),
        Syntax(['r12'], new_func=lambda: R12),
        Syntax(['sp'], new_func=lambda: SP),
        Syntax(['lr'], new_func=lambda: LR),
        Syntax(['pc'], new_func=lambda: PC)
        ]


class Reg8Op(ArmRegister):
    pass


def get_register(n):
    """ Based on a number, get the corresponding register """
    return num2regmap[n]


def register_range(a, b):
    """ Return set of registers from a to b """
    assert a.num < b.num
    return {get_register(n) for n in range(a.num, b.num + 1)}


R0 = Reg8Op('r0', num=0)
R1 = Reg8Op('r1', num=1)
R2 = Reg8Op('r2', num=2)
R3 = Reg8Op('r3', num=3)
R4 = Reg8Op('r4', num=4)
R5 = Reg8Op('r5', num=5)
R6 = Reg8Op('r6', num=6)
R7 = Reg8Op('r7', num=7)
R8 = ArmRegister('r8', num=8)
R9 = ArmRegister('r9', num=9)
R10 = ArmRegister('r10', num=10)
R11 = ArmRegister('r11', num=11)
R12 = ArmRegister('r12', num=12)

# Other registers:
# TODO
SP = ArmRegister('sp', num=13)
LR = ArmRegister('lr', num=14)
PC = ArmRegister('pc', num=15)

registers = [R0, R1, R2, R3, R4, R5, R6, R7, SP, LR, PC]
num2regmap = {r.num: r for r in registers}

