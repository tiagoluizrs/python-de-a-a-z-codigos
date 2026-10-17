"""Gabarito do exercício 3."""
import sys
import traceback


class UserError(Exception):
    pass


def run(main, argv=None, stderr=None, debug=False):
    stderr = stderr or sys.stderr
    argv = sys.argv[1:] if argv is None else argv
    try:
        code = main(argv)
        return 0 if code is None else int(code)
    except UserError as error:
        print(f"erro: {error}", file=stderr)
        return 1
    except KeyboardInterrupt:
        print(file=stderr)
        return 130
    except BrokenPipeError:
        return 0
    except SystemExit as exit_:
        if exit_.code is None:
            return 0
        if isinstance(exit_.code, int):
            return exit_.code
        print(exit_.code, file=stderr)
        return 1
    except Exception as error:
        if debug:
            print(traceback.format_exc(), file=stderr)
        print(f"erro interno: {type(error).__name__}: {error}", file=stderr)
        return 70
