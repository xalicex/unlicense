from typing import Optional

import lief  # type: ignore

THEMIDA2_IMPORTED_MODS = ["kernel32.dll", "comctl32.dll"]
THEMIDA2_IMPORTED_FUNCS = ["lstrcpy", "InitCommonControls"]


def detect_winlicense_version(pe_file_path: str) -> Optional[int]:
    binary = lief.parse(pe_file_path)

    # Version 3.x
    try:
        _boot_section = binary.get_section(".boot")
        _themida_section = binary.get_section(".themida")
        return 3
    except lief.not_found:
        # Not Themida 3.x
        pass

    try:
        _boot_section = binary.get_section(".boot")
        _winlice_section = binary.get_section(".winlice")
        return 3
    except lief.not_found:
        # Not Winlicense 3.x
        pass

    # Version 2.x
    if len(binary.imports) == 2 and len(binary.imported_functions) == 2:
        if binary.imports[0].name in THEMIDA2_IMPORTED_MODS and \
           binary.imports[1].name in THEMIDA2_IMPORTED_MODS and \
           binary.imported_functions[0].name in THEMIDA2_IMPORTED_FUNCS and \
           binary.imported_functions[1].name in THEMIDA2_IMPORTED_FUNCS:
            return 2

    # These x86 instructions are always present at the beginning of a section
    # in Themida/WinLicense 2.x
    instr_pattern = [
        0x56, 0x50, 0x53, 0xE8, 0x01, 0x00, 0x00, 0x00, 0xCC, 0x58
    ]
    for section in binary.sections:
        if instr_pattern == section.content[:len(instr_pattern)]:
            return 2

    # Failed to automatically detect version
    return None
