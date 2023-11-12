# Python imports

# Lib imports

# Application imports



# Break into a Python console upon SIGUSR1 (Linux) or SIGBREAK (Windows:
# CTRL+Pause/Break).  To be included in all production code, just in case.
def debug_signal_handler(signal, frame):
    del signal
    del frame

    try:
        import rpdb2
        logger.debug("\n\nStarting embedded RPDB2 debugger. Password is 'foobar'\n\n")
        rpdb2.start_embedded_debugger("foobar", True, True)
        rpdb2.setbreak(depth=1)
        return
    except StandardError:
        ...

    try:
        from rfoo.utils import rconsole
        logger.debug("\n\nStarting embedded rconsole debugger...\n\n")
        rconsole.spawn_server()
        return
    except StandardError as ex:
        ...

    try:
        from pudb import set_trace
        logger.debug("\n\nStarting PuDB debugger...\n\n")
        set_trace(paused = True)
        return
    except StandardError as ex:
        ...

    try:
        import pdb
        logger.debug("\n\nStarting embedded PDB debugger...\n\n")
        pdb.Pdb(skip=['gi.*']).set_trace()
        return
    except StandardError as ex:
        ...

    try:
        import code
        code.interact()
    except StandardError as ex:
        logger.debug(f"{ex}, returning to normal program flow...")
