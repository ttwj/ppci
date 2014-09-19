
"""
    Target independent code generator part. The target is provided when
    the generator is created.
"""

from .. import ir, irdag, irmach
from ..irutils import Verifier, split_block, Writer
from ..target import Target
from .registerallocator import RegisterAllocator
from ..binutils.outstream import MasterOutputStream, FunctionOutputStream
from ..binutils.outstream import TextOutputStream
import logging


class CodeGenerator:
    """ Generic code generator """
    def __init__(self, target):
        # TODO: schedule traces in better order.
        # This is optional!
        assert isinstance(target, Target), target
        self.logger = logging.getLogger('codegen')
        self.target = target
        self.dagger = irdag.Dagger()
        self.ins_sel = target.ins_sel
        self.register_allocator = RegisterAllocator()
        self.verifier = Verifier()

    def dump_dag(self, dags, f):
        print("Selection dag:", file=f)
        for dag in dags:
            print('Dag:', file=f)
            for root in dag:
                print("- {}".format(root), file=f)

    def dump_frame(self, frame, f):
        print("Frame:", file=f)
        print(frame, file=f)
        for ins in frame.instructions:
            print('$ {}'.format(ins.long_repr), file=f)

    def generate_function(self, irfunc, outs):
        """ Generate code for one function into a frame """
        self.logger.info('Generating {} code for {}'
                         .format(self.target, irfunc.name))

        log_file = 'log_{}.txt'.format(irfunc.name)
        with open(log_file, 'w') as f:
            print("Log for {}".format(irfunc), file=f)
            print("Target: {}".format(self.target), file=f)
            Writer().write_function(irfunc, f)

        instruction_list = []
        outs = MasterOutputStream([
            FunctionOutputStream(instruction_list.append),
            outs])

        # Create a frame for this function:
        frame = self.target.FrameClass(ir.label_name(irfunc))

        # Split too large basic blocks in smaller chunks (for literal pools):
        # TODO: fix arbitrary number of 500. This works for arm and thumb..
        for block in irfunc:
            while len(block) > 500:
                self.logger.debug('{} too large, splitting up'.format(block))
                _, block = split_block(block, pos=500)

        # Create selection dag (directed acyclic graph):
        dag = self.dagger.make_dag(irfunc, frame)
        self.logger.debug('DAG created')

        with open(log_file, 'a') as f:
            self.dump_dag(dag, f)

        # Select instructions:
        self.ins_sel.munch_dag(dag, frame)
        self.logger.debug('Selected instructions')

        # Define arguments live at first instruction:
        ins0 = frame.instructions[0]
        in0def = []
        for idx, arg in enumerate(irfunc.arguments):
            arg_loc = frame.argLoc(idx)
            if isinstance(arg_loc, irmach.VirtualRegister):
                in0def.append(arg_loc)
        ins0.dst = tuple(in0def)

        # Dump current state to file:
        with open(log_file, 'a') as f:
            print('Selected instructions', file=f)
            self.dump_frame(frame, f)

        # Do register allocation:
        self.register_allocator.allocFrame(frame)
        self.logger.debug('Registers allocated, now adding final glue')
        # TODO: Peep-hole here?

        with open(log_file, 'a') as f:
            self.dump_frame(frame, f)

        # Add label and return and stack adjustment:
        frame.EntryExitGlue3()

        # Materialize the register allocated instructions into a stream of
        # real instructions.
        self.target.lower_frame_to_stream(frame, outs)
        self.logger.debug('Instructions materialized')

        with open(log_file, 'a') as f:
            for ins in instruction_list:
                print(ins, file=f)

    def generate(self, ircode, outs):
        """ Generate code into output stream """
        assert isinstance(ircode, ir.Module)

        # Generate code for global variables:
        outs.select_section('data')
        for global_variable in ircode.Variables:
            self.target.emit_global(outs, ir.label_name(global_variable))

        # Generate code for functions:
        # Munch program into a bunch of frames. One frame per function.
        # Each frame has a flat list of abstract instructions.
        outs.select_section('code')
        for function in ircode.Functions:
            self.generate_function(function, outs)
