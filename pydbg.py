from elftools.elf.elffile import ELFFile
from elftools.common.utils import bytelist2string

import collections

class CuDict(collections.abc.Mapping):

    def __init__(self, dwarf):
        self._dwarf = dwarf
        self._data = {}
        
        for CU in self._dwarf.iter_CUs():
            # Start with the top DIE, the root for this CU's DIE tree
            top_DIE = CU.get_top_DIE()
            cu_filename = top_DIE.get_full_path()
            self._data[cu_filename] = CU

    def __getitem__(self, key): 
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
    

class Firmware:
    def __init__(self, fw):
        self._fw = open(fw, 'rb')
        self._elf = ELFFile(self._fw)

        if not self._elf.has_dwarf_info():
            print('  file has no DWARF info')
            return
                
        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        self._dwarf = self._elf.get_dwarf_info()

    @property
    def cu_dict(self):
        return CuDict(self._dwarf)
    


if __name__ == '__main__':
    fw = Firmware('C:\\Users\\jonso\\OneDrive\\Documents\\DCC\\samc21\\Debug\\dcc_encoder.elf')

    print(fw.cu_dict)