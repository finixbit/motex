import sys
from pathlib import Path

import toml

from logzero import logger

from motex.storage import MotexStorage
from motex.core.instruction import MotexInstruction, MotexInstructionHelper
from motex.core.callsite import MotexCallsite, MotexCallsiteHelper
from motex.core.function import MotexFunction, MotexFunctionHelper
from motex.core.relocation import MotexRelocation, MotexRelocationHelper
from motex.core.segment import MotexSegment, MotexSegmentHelper
from motex.core.section import MotexSection, MotexSectionHelper
from motex.core.symbol import MotexSymbol, MotexSymbolHelper


class MotexConfig:
    _parsed_config = None

    def __init__(self, config_path):
        if not isinstance(config_path, str):
            logger.exception("config_path must be string")

        if not Path(config_path).is_file():
            logger.error("Invalid config path")
            sys.exit(1)

        try:
            with open(Path(config_path)) as fd:
                config_toml_string = fd.read()

            self._parsed_config = toml.loads(config_toml_string)
        except Exception as e:
            logger.exception(e)

    @property
    def motex_config(self):
        return self._parsed_config.get('motex')

    @property
    def storage_config(self):
        return self._parsed_config.get('storage')

    @property
    def extract_config(self):
        return self._parsed_config.get('extract')

    @property
    def config(self):
        return self._parsed_config


class Motex(MotexConfig):
    def __init__(self, config_path, **kwargs):
        super().__init__(config_path)
        self._storage = MotexStorage(self.storage_config['backend'],
                                     self.storage_config['format'], **self.storage_config['args'])

    @property
    def storage(self):
        return self._storage


class MotexHelpers:

    def __init__(self, storage):
        self._functions = MotexFunctionHelper(storage)
        self._callsites = MotexCallsiteHelper(storage)
        self._instructions = MotexInstructionHelper(storage)
        self._relocations = MotexRelocationHelper(storage)
        self._segments = MotexSegmentHelper(storage)
        self._symbols = MotexSymbolHelper(storage)
        self._sections = MotexSectionHelper(storage)
        self._basicblocks = None

    @property
    def instructions(self):
        return self._instructions
    
    @property
    def segments(self):
        return self._segments

    @property
    def symbols(self):
        return self._symbols

    @property
    def relocations(self):
        return self._relocations

    @property
    def segments(self):
        return self._segments

    @property
    def functions(self):
        return self._functions

    @property
    def sections(self):
        return self._sections

    @property
    def basicblocks(self):
        return self._basicblocks

    @property
    def callsites(self):
        return self._callsites


__all__ = ['MotexSection',
           'MotexSymbol',
           'MotexSegment',
           'MotexRelocation',
           'MotexInstruction',
           'MotexFunction',
           'MotexBasicblock',
           'MotexCallsite',
           'Motex',
           'MotexHelpers']
