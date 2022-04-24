from shutil import which


def _exists(name: str) -> str:
    """
    Check for the existence of a program
    INPUT: Name, string.
    OUTPUT: exists, bool.
    """
    return which(name) is not None


def checkTools() -> list[str]:
    """
    Check for all needed programs.
    INPUT: None
    OUTPUT: Missing packages, List of str.
    """
    missing_programs = []
    programs_to_check = ["rg"]
    for program in programs_to_check:
        if not _exists(program):
            missing_programs.append(program)
    return missing_programs
