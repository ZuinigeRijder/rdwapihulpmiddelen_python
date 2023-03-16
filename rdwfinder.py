"""rdwfinder.py"""
import sys
import time
from datetime import datetime

from rdw_utils import arg_has, execute_command, my_die

sys.stdout.flush()  # Disable output buffering

D = arg_has("debug")


def dbg(line: str) -> bool:
    """print line if debugging"""
    if D:
        print(line)
    return D  # just to make a lazy evaluation expression possible


def main():
    """main"""
    if len(sys.argv) != 6:
        my_die(
            "Usage: rdwfinder BEGINLETTER ENDLETTERS FROM TO INCREMENT, e.g. rdwfinder R LF 510 560 1"  # noqa
        )

    toggle = True

    arg_beginletter = sys.argv[1]
    arg_letters = sys.argv[2]
    arg_from = int(sys.argv[3])
    arg_to = int(sys.argv[4])

    if arg_to < arg_from:
        arg_to, arg_from = arg_from, arg_to

    arg_increment = int(sys.argv[5])
    arg_beginletter = arg_beginletter.upper()
    arg_letters = arg_letters.upper()

    results = []
    current = arg_from
    count = 0
    start_time = time.time()
    begin_time = time.time()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

    while current <= arg_to and current <= 1000 and current >= 0:
        current_number = f"{current:03d}"
        kenteken = f"{arg_beginletter}{current_number}{arg_letters}"
        current += arg_increment
        _ = D and dbg(f"Getting details of kenteken: {kenteken}")
        if (
            execute_command(
                'curl -X POST -d "__VIEWSTATE=%2FwEPDwUKMTE1NDI3MDEyOQ9kFgJmD2QWAgIDD2QWBAIBD2QWAgIJDxYCHgdWaXNpYmxlaGQCAw9kFgICAw9kFghmD2QWAmYPZBYMZg9kFgICAQ9kFgJmDxQrAAIPFgIeC18hSXRlbUNvdW50AgxkZGQCAQ9kFgICAQ9kFgJmDxQrAAIPFgIfAQIFZGRkAgIPZBYCAgEPZBYCZg8UKwACDxYCHwECB2RkZAIDD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgNkZGQCBA9kFgICAQ9kFgJmDxQrAAIPFgIfAQIFZGRkAgUPZBYCAgEPZBYCZg8UKwACDxYCHwECAWRkZAIBD2QWAmYPZBYGZg9kFgICAQ9kFgJmDxQrAAIPFgIfAQIEZGRkAgEPZBYCAgEPZBYCZg8UKwACDxYCHwECDmRkZAICD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgtkZGQCAg9kFgJmD2QWBGYPZBYCAgEPZBYCZg8UKwACDxYCHwECBmRkZAIBD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgdkZGQCAw9kFgJmD2QWAmYPZBYCAgEPZBYCZg8UKwACDxYCHwECA2RkZBgMBRdjdGwwMCRNYWluQ29udGVudCRjdGwyNg8UKwAOZGRkZGRkZDwrAAYAAgZkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMTQPFCsADmRkZGRkZGQUKwABZAIBZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDIwDxQrAA5kZGRkZGRkPCsADgACDmRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwwNg8UKwAOZGRkZGRkZDwrAAUAAgVkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMjIPFCsADmRkZGRkZGQ8KwALAAILZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDEwDxQrAA5kZGRkZGRkFCsAA2RkZAIDZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDMyDxQrAA5kZGRkZGRkFCsAA2RkZAIDZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDEyDxQrAA5kZGRkZGRkPCsABQACBWRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwwOA8UKwAOZGRkZGRkZDwrAAcAAgdkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMTgPFCsADmRkZGRkZGQ8KwAEAAIEZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDA0DxQrAA5kZGRkZGRkPCsADAACDGRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwyOA8UKwAOZGRkZGRkZDwrAAcAAgdkZGRmAv%2F%2F%2F%2F8PZNmHhgdEC2dk11hzIudYxHwUwGfK4eXG%2Fo9Cu8qdtlVL&__VIEWSTATEGENERATOR=CA0B0334&__EVENTVALIDATION=%2FwEdAALw6Ljfck63rzOJzJwmCORy851Fq81QBiZgFEttEk2eePY91dYtbp8ZA%2BHq0kU34KFnAvRU3Nv8x3coJguc2YKX&ctl00%24TopContent%24txtKenteken='  # noqa pylint:disable=line-too-long
                + f"{kenteken}"
                + '" https://ovi.rdw.nl/default.aspx > x.rdwfind.html',
                D,
                retry=True,
                die_on_error=False,
            )
            == 0
        ):
            print(f"{count}: Checking {kenteken}")
            with open("x.rdwfind.html", encoding="latin-1") as kentekenfile:
                for line in kentekenfile:
                    line = line.strip()
                    if "IONIQ5" in line:
                        print(f"MATCH IONIQ5: {kenteken}")
                        results.append(kenteken)
                        count += 1
                        break
                    elif (
                        "Het maximaal aantal opvragingen per dag" in line
                        or "dienst ontzegd" in line
                    ):
                        print(line)
                        time.sleep(30)
                        current -= arg_increment
                    elif (
                        "Er zijn geen gegevens gevonden voor het ingevulde kenteken"
                        in line
                    ):
                        print(f"GEEN GEGEVENS: {kenteken}")

            stop_time = time.time()
            diff_time = stop_time - start_time
            toggle = not toggle
            wait_time = 3 - diff_time if toggle else 2 - diff_time
            if wait_time > 0:
                time.sleep(wait_time)
            start_time = time.time()

    print("\n\nAlle detail resultaten:\n\n")
    for result in sorted(results):
        print(result)
    print(f"Totaal aantal IONIQ5: {count}")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_time = time.time()
    elapsed_time = end_time - begin_time
    print(f"Elapsed: {elapsed_time}")


main()
