from ... import same_dir
from ppci import pyburg
from ..instructionselector import InstructionSelector

# Import BURG spec for arm:
spec_file = same_dir(__file__, 'arm.brg')
arm_matcher = pyburg.load_as_module(spec_file)


class ArmMatcher(arm_matcher.Matcher):
    """ Matcher that derives from a burg spec generated matcher """
    def __init__(self, selector):
        super().__init__()
        self.selector = selector
        self.newTmp = selector.newTmp
        self.emit = selector.emit


class ArmInstructionSelector(InstructionSelector):
    """ Instruction selector for the arm architecture """
    def __init__(self):
        super().__init__()
        self.matcher = ArmMatcher(self)
