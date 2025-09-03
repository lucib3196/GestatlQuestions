# Helpers
def logs_contain(logs, *substrs) -> bool:
    """True if any single log line contains all given substrings."""
    logs = logs or []
    for line in logs:
        if all(s in line for s in substrs):
            return True
    return False