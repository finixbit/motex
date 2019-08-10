from collections import OrderedDict 

import lief
from lief import ELF
import capstone as capstone
from elftools.elf.elffile import ELFFile
import motex.common.hextools as hextools

from motex.core import (
    MotexSymbol,
    MotexSegment,
    MotexSection,
    MotexRelocation,
    MotexInstruction,
    MotexCallsite,
    MotexFunction,
)

from motex.core.section import MotexSectionStorageHelper
from motex.core.symbol import MotexSymbolStorageHelper
from motex.core.segment import MotexSegmentStorageHelper
from motex.core.relocation import MotexRelocationStorageHelper
from motex.core.instruction import MotexInstructionStorageHelper
from motex.core.callsite import MotexCallsiteStorageHelper
from motex.core.function import MotexFunctionStorageHelper


class ELFExtractor:
    def __init__(self, binary_path):
        super().__init__()
        self.binary_path = binary_path

        self.binary = lief.parse(binary_path)
        self.symbols = self._get_symbols()
        self.sections = self._get_sections()
        self.relocations = self._get_relocations()
        self.segments = self._get_segments()
        self.callsites = OrderedDict()
        self.functions = OrderedDict()

        self.function_symbols = {v.symbol_value: v for k, v in self.symbols.items() \
                                 if v.symbol_type == 'FUNC' and self.relocations.get(k) is None and v.symbol_value != 0}
        
    def _get_symbols(self):
        syms = OrderedDict()
        functions = OrderedDict()
        for index, symbol in enumerate(self.binary.symbols):
            symbol_name = None
            try:
                symbol_name = symbol.demangled_name
            except:
                symbol_name = symbol.name

            import_export = ""
            if symbol.imported:
                import_export = "I"

            if symbol.exported:
                import_export = "E"

            symbol_version = symbol.symbol_version if symbol.has_version else ""

            symbol_dict = {'symbol_num': index,
                           'symbol_index': str(symbol.shndx),
                           'symbol_value': hextools.int_to_hex(symbol.value),
                           'symbol_size': symbol.size,
                           'symbol_type': str(symbol.type).split(".")[-1],
                           'symbol_bind': str(symbol.binding).split(".")[-1],
                           'symbol_visibility': str(symbol.visibility).split(".")[-1],
                           'symbol_name': symbol_name,
                           'symbol_import_export': import_export,
                           'symbol_version': str(symbol_version)}

            syms[str(index)] = (MotexSymbol(**symbol_dict))
        return syms

    def _get_sections(self):
        secs = OrderedDict()
        for index, section in enumerate(self.binary.sections):
            segments_str = " - ".join([str(s.type).split(".")[-1] for s in section.segments])

            section_dict = {'section_index': index,
                            'section_name': section.name,
                            'section_type': str(section.type).split(".")[-1],
                            'section_offset': hextools.int_to_hex(section.file_offset),
                            'section_virtual_address': hextools.int_to_hex(section.virtual_address),
                            'section_size': section.size,
                            'section_entry_size': section.entry_size,
                            'section_entropy': abs(section.entropy),
                            'section_segments': segments_str}

            secs[str(index)] = (MotexSection(**section_dict))
        return secs

    def _get_segments(self):
        segs = OrderedDict()
        for index, segment in enumerate(self.binary.segments):
            flags_str = ["-"] * 3
            if ELF.SEGMENT_FLAGS.R in segment:
                flags_str[0] = "r"

            if ELF.SEGMENT_FLAGS.W in segment:
                flags_str[1] = "w"

            if ELF.SEGMENT_FLAGS.X in segment:
                flags_str[2] = "x"
            flags_str = "".join(flags_str)

            segments_dict = {'segment_type': str(segment.type).split(".")[1],
                             'segment_offset': hextools.int_to_hex(segment.file_offset),
                             'segment_virtual_address': hextools.int_to_hex(segment.virtual_address),
                             'segment_virtual_size': segment.virtual_size,
                             'segment_physical_address': hextools.int_to_hex(segment.physical_address),
                             'segment_physical_size': segment.physical_size,
                             'segment_flags': flags_str,
                             'segment_sections': [section.name for section in segment.sections],
                             'segment_section_addrs': [hextools.int_to_hex(section.file_offset)
                                                       for section in segment.sections]}

            segs[str(index)] = (MotexSegment(**segments_dict))
        return segs

    def _get_relocations(self):
        plt_section = next(filter(lambda sec: sec[1].section_name == '.plt', self.sections.items()))[1]
        plt_vma_address = hextools.hex_to_int(plt_section.section_virtual_address)
        plt_entry_size = plt_section.section_entry_size

        relocs = OrderedDict()
        for index, relocation in enumerate(self.binary.relocations):
            reloc_type = str(relocation.type)
            if self.binary.header.machine_type == ELF.ARCH.x86_64:
                reloc_type = str(ELF.RELOCATION_X86_64(relocation.type))
            elif self.binary.header.machine_type == ELF.ARCH.i386:
                reloc_type = str(ELF.RELOCATION_i386(relocation.type))
            elif self.binary.header.machine_type == ELF.ARCH.ARM:
                reloc_type = str(ELF.RELOCATION_ARM(relocation.type))
            elif self.binary.header.machine_type == ELF.ARCH.AARCH64:
                reloc_type = str(ELF.RELOCATION_AARCH64(relocation.type))

            symbol_name = str(relocation.symbol.name) if relocation.has_symbol else ""
            symbol_value = hextools.int_to_hex(relocation.symbol.value) if relocation.has_symbol else "0"*16

            def reloc_compute(rel_type, rel_addr):
                pass

            relocation_plt_address = plt_vma_address + (index + 1) * plt_entry_size;

            relocation_dict = {'relocation_address': hextools.int_to_hex(relocation.address),
                               'relocation_type': reloc_type,
                               'relocation_symbol_value': symbol_value,
                               'relocation_symbol_name': symbol_name,
                               'relocation_computed_plt_address': hextools.int_to_hex(relocation_plt_address)}

            relocs[relocation_dict['relocation_computed_plt_address']] = (MotexRelocation(**relocation_dict))
        return relocs

    def _extract_sections(self, storage):
        prev = None
        MotexSectionStorageHelper.prepare(storage)

        for index, current in enumerate(self.sections.items()):
            MotexSectionStorageHelper.save(index, current[1], prev, storage)
            prev = current[1]

        MotexSectionStorageHelper.complete(storage)
    
    def _extract_symbols(self, storage):
        prev = None
        MotexSymbolStorageHelper.prepare(storage)

        for index, current in enumerate(self.symbols.items()):
            MotexSymbolStorageHelper.save(index, current[1], prev, storage)
            prev = current[1]

        MotexSymbolStorageHelper.complete(storage)

    def _extract_relocations(self, storage):
        prev = None
        MotexRelocationStorageHelper.prepare(storage)

        for index, current in enumerate(self.relocations.items()):
            MotexRelocationStorageHelper.save(index, current[1], prev, storage)
            prev = current[1]

        MotexRelocationStorageHelper.complete(storage)

    def _extract_segments(self, storage):
        prev = None
        MotexSegmentStorageHelper.prepare(storage)

        for index, current in enumerate(self.segments.items()):
            MotexSegmentStorageHelper.save(index, current[1], prev, storage)
            prev = current[1]

        MotexSegmentStorageHelper.complete(storage)

    def _extract_callsites(self, storage):
        prev = None
        MotexCallsiteStorageHelper.prepare(storage)

        for index, current in enumerate(self.callsites.items()):
            MotexCallsiteStorageHelper.save(current[1].address, current[1], prev, storage)
            prev = current[1]

        MotexCallsiteStorageHelper.complete(storage)

    def _extract_functions(self, storage):
        prev = None
        MotexFunctionStorageHelper.prepare(storage)

        for index, current in enumerate(self.functions.items()):
            MotexFunctionStorageHelper.save(current[1].address, current[1], prev, storage)
            prev = current[1]

        MotexFunctionStorageHelper.complete(storage)

    def _extract_instructions(self, storage):
        with open(self.binary_path, 'rb') as bin_file:
            elf = ELFFile(bin_file)
            text_code_section = elf.get_section_by_name('.text')
            text_code_content = text_code_section.data()
            text_code_entry = text_code_section['sh_addr']

            # function Tracker
            current_function = None
            current_function_ret = False
            function_dict = dict()

            # Callsite Tracker
            current_callsite_open = False
            callsite_dict = dict()

            prev_insn = None
            MotexInstructionStorageHelper.prepare(storage)
            md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

            for (index, instruction) in enumerate(md.disasm(text_code_content, text_code_entry)):
                insn_address = hextools.int_to_hex(instruction.address)

                if self.function_symbols.get(insn_address):
                    if current_function:
                        fn = MotexFunction(**function_dict)
                        self.functions[function_dict.get('address')] = fn

                    current_function = insn_address
                    fn_sym = self.function_symbols.get(insn_address)
                    if fn_sym:
                        function_dict = {'basicblock_leaders': [],
                                         'address': fn_sym.symbol_value,
                                         'name': fn_sym.symbol_name,
                                         'callsites_list': [],
                                         'function_edges': [],
                                         'basicblock_edges': [],
                                         'instructions_list': []}

                if current_callsite_open:
                    callsite_dict['return_address'] = insn_address
                    cs = MotexCallsite(**callsite_dict)
                    self.callsites[callsite_dict.get('address')] = cs

                    current_callsite_open = False
                    callsite_dict = dict()

                if 'call' in instruction.mnemonic:
                    current_callsite_open = True
                    callsite_dict = {'address': insn_address,
                                     'target_resolved': False,
                                     'target_name': instruction.op_str,
                                     'target_address': None,
                                     'target_type': None,
                                     'function_address': current_function,
                                     'basicblock_leader': None,}
                    try:
                        target_address = hextools.hex_to_int(instruction.op_str)
                        callsite_dict['target_resolved'] = True
                        callsite_dict['target_address'] = hextools.int_to_hex(target_address)

                        sym = self.function_symbols.get(callsite_dict['target_address'])
                        if sym:
                            callsite_dict['target_type'] = 'symbol'
                            callsite_dict['target_name'] = sym.symbol_name
                            function_dict['function_edges'].append(sym.symbol_value)

                        if hextools.int_to_hex(target_address) in self.relocations.keys():
                            rel_sym = self.relocations[hextools.int_to_hex(target_address)]
                            callsite_dict['target_type'] = 'reloc'
                            callsite_dict['target_name'] = rel_sym.relocation_symbol_name
                    except Exception as e:
                        pass

                    if current_function and not current_function_ret:
                        function_dict['callsites_list'].append(insn_address)

                instruction_dict = {'address': insn_address,
                                    'function_address': current_function,
                                    'basicblock_address': None,
                                    'content': instruction.bytes.hex(),
                                    'content_str': [instruction.mnemonic, instruction.op_str]}

                if current_function:
                    function_dict['instructions_list'].append(insn_address)

                insn = MotexInstruction(**instruction_dict)
                MotexInstructionStorageHelper.save(insn_address, insn, prev_insn, storage)
                prev_insn = insn

            MotexInstructionStorageHelper.complete(storage)

    def _extract_basicblocks(self, storage):
        pass
        
    def extract(self, extract_config, storage):
        if extract_config.get('sections') is True:
            self._extract_sections(storage)

        if extract_config.get('symbols') is True:
            self._extract_symbols(storage)

        if extract_config.get('segments') is True:
            self._extract_segments(storage)

        if extract_config.get('relocations') is True:
            self._extract_relocations(storage)
        
        if extract_config.get('instructions') is True:
            self._extract_instructions(storage)

        if extract_config.get('callsites') is True:
            self._extract_callsites(storage)

        if extract_config.get('functions') is True:
            self._extract_functions(storage)

        if extract_config.get('basicblocks') is True:
            self._extract_basicblocks(storage) 
