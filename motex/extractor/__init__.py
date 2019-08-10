import sys
from pathlib import Path
from logzero import logger
from motex.extractor.elf_extractor import ELFExtractor


class MotexExtractor:
    supported_arch = []
    supported_binary_format = {'elf': ELFExtractor}

    def __init__(self, motex_config, storage):
        if not all(map(lambda x: x is not None, [motex_config, storage])):
            logger.error('motex_config, storage cannot be None')
            sys.exit(1)

        binary_format = motex_config.get('binary_format').lower()
        format_extractor = self.supported_binary_format.get(binary_format)
        if format_extractor is None:
            logger.error(f'Binary format `{binary_format}` is not supported')
            sys.exit(1) 

        binary_path = motex_config.get('binary_path')
        if binary_path is None or not Path(binary_path).is_file():
            logger.error("Invalid binary path")
            sys.exit(1)

        self.extractor = format_extractor(binary_path)
        self.storage = storage

    def extract(self, extract_config):
        self.extractor.extract(extract_config, self.storage)


__all__ = ['MotexExtractor',]
