"""missing.py"""
import os
import re
import sys
import time
from rdw_utils import arg_has, execute_command, fill_prices, get_variant

sys.stdout.flush()  # Disable output buffering

D = arg_has("debug")


def dbg(line: str) -> bool:
    """print line if debugging"""
    if D:
        print(line)
    return D  # just to make a lazy evaluation expression possible


def main():
    """main"""
    variantscount = {}
    variantscountnognietopnaam = {}

    taxi = "Nee"
    export = "Nee"

    count19inch = 0
    count20inch = 0
    countlounge19inch = 0
    countlounge20inch = 0

    colormatte = 0
    colormetallic = 0
    colormica = 0
    colorsolid = 0
    colormicapearl = 0

    # this contains the pricelist per date and kWh battery and AWD
    pricelists_dates = ["20230101", "20220901", "20220501", "20220301", "20210501"]
    pricelists = fill_prices(D)

    filename = "missing.txt"

    print(f"Processing {filename}")
    kentekens = []
    with open(filename, encoding="utf8") as missing_infile:
        for line in missing_infile.readlines():
            current_line = line.strip()
            if current_line == "":
                continue
            _ = D and dbg(f"currentLine=[{current_line}]")
            kentekens.append(current_line)

    errors = []
    new_missing_list = []
    with open("missing.outfile.txt", "w", encoding="utf8") as outfile:
        start_time = time.time()
        for k in kentekens:
            filename = f"kentekens/x.missing.{k}.html"
            exists = os.path.exists(filename)
            if exists:
                _ = D and dbg(f"Skipping: {k}")
                # skip already asked missing kentekens

            if not exists:
                filename = "x.missing"
                print(f"Getting details of missing kenteken: {k}")
                cmd = f'curl -s -X POST -d "__VIEWSTATE=%2FwEPDwUKMTE1NDI3MDEyOQ9kFgJmD2QWAgIDD2QWBAIBD2QWAgIJDxYCHgdWaXNpYmxlaGQCAw9kFgICAw9kFghmD2QWAmYPZBYMZg9kFgICAQ9kFgJmDxQrAAIPFgIeC18hSXRlbUNvdW50AgxkZGQCAQ9kFgICAQ9kFgJmDxQrAAIPFgIfAQIFZGRkAgIPZBYCAgEPZBYCZg8UKwACDxYCHwECB2RkZAIDD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgNkZGQCBA9kFgICAQ9kFgJmDxQrAAIPFgIfAQIFZGRkAgUPZBYCAgEPZBYCZg8UKwACDxYCHwECAWRkZAIBD2QWAmYPZBYGZg9kFgICAQ9kFgJmDxQrAAIPFgIfAQIEZGRkAgEPZBYCAgEPZBYCZg8UKwACDxYCHwECDmRkZAICD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgtkZGQCAg9kFgJmD2QWBGYPZBYCAgEPZBYCZg8UKwACDxYCHwECBmRkZAIBD2QWAgIBD2QWAmYPFCsAAg8WAh8BAgdkZGQCAw9kFgJmD2QWAmYPZBYCAgEPZBYCZg8UKwACDxYCHwECA2RkZBgMBRdjdGwwMCRNYWluQ29udGVudCRjdGwyNg8UKwAOZGRkZGRkZDwrAAYAAgZkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMTQPFCsADmRkZGRkZGQUKwABZAIBZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDIwDxQrAA5kZGRkZGRkPCsADgACDmRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwwNg8UKwAOZGRkZGRkZDwrAAUAAgVkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMjIPFCsADmRkZGRkZGQ8KwALAAILZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDEwDxQrAA5kZGRkZGRkFCsAA2RkZAIDZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDMyDxQrAA5kZGRkZGRkFCsAA2RkZAIDZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDEyDxQrAA5kZGRkZGRkPCsABQACBWRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwwOA8UKwAOZGRkZGRkZDwrAAcAAgdkZGRmAv%2F%2F%2F%2F8PZAUXY3RsMDAkTWFpbkNvbnRlbnQkY3RsMTgPFCsADmRkZGRkZGQ8KwAEAAIEZGRkZgL%2F%2F%2F%2F%2FD2QFF2N0bDAwJE1haW5Db250ZW50JGN0bDA0DxQrAA5kZGRkZGRkPCsADAACDGRkZGYC%2F%2F%2F%2F%2Fw9kBRdjdGwwMCRNYWluQ29udGVudCRjdGwyOA8UKwAOZGRkZGRkZDwrAAcAAgdkZGRmAv%2F%2F%2F%2F8PZNmHhgdEC2dk11hzIudYxHwUwGfK4eXG%2Fo9Cu8qdtlVL&__VIEWSTATEGENERATOR=CA0B0334&__EVENTVALIDATION=%2FwEdAALw6Ljfck63rzOJzJwmCORy851Fq81QBiZgFEttEk2eePY91dYtbp8ZA%2BHq0kU34KFnAvRU3Nv8x3coJguc2YKX&ctl00%24TopContent%24txtKenteken={k}" https://ovi.rdw.nl/default.aspx > x.missing'  # noqa pylint:disable=line-too-long
                execute_command(cmd, D, retry=False, die_on_error=True)
                stop_time = time.time()
                diff_time = stop_time - start_time
                wait_time = 3 - diff_time  # at least wait some seconds
                _ = D and dbg(f"Diff: [{diff_time}], Wait: [{wait_time}]")
                if wait_time > 0:
                    time.sleep(wait_time)
                start_time = time.time()

            prijs = None
            kleur = None
            uitvoering = None
            variant = None
            typegoedkeuring = None
            afg_dat_kent = None
            datum_gdk = "????????"
            eerstetoelatingsdatum = None
            _ = D and dbg(f"reading={filename}")
            with open(filename, encoding="utf8") as kentekenfile:
                op_naam = "????????"
                for line in kentekenfile:
                    line = line.strip()
                    if (
                        "Het maximaal aantal opvragingen per dag" in line
                        or "dienst ontzegd" in line
                    ):
                        print(line)
                        continue

                    if 'id="CatalogusPrijs"' in line:
                        tmp = line
                        tmp = re.sub('.*id="CatalogusPrijs"', "", tmp)
                        tmp = re.sub("</div>.*", "", tmp)
                        tmp = re.sub(">.+ ", "", tmp)
                        _ = D and dbg(f"CatalogusPrijs: {tmp}")
                        prijs = tmp
                    if 'id="Kleur"' in line:
                        tmp = line
                        tmp = re.sub('.*id="Kleur"', "", tmp)
                        tmp = re.sub("</div>.*", "", tmp)
                        tmp = re.sub(">", "", tmp)
                        _ = D and dbg(f"Kleur: {tmp}")
                        kleur = tmp.upper()
                        kleur = kleur.ljust(10)
                    if 'id="Uitvoering"' in line:
                        tmp = line
                        tmp = re.sub('.*id="Uitvoering"', "", tmp)
                        tmp = re.sub("</div>.*", "", tmp)
                        tmp = re.sub(">", "", tmp)
                        _ = D and dbg(f"Uitvoering: {tmp}")
                        uitvoering = tmp
                    if 'id="Variant"' in line:
                        tmp = line
                        tmp = re.sub('.*id="Variant"', "", tmp)
                        tmp = re.sub("</div>.*", "", tmp)
                        tmp = re.sub(">", "", tmp)
                        _ = D and dbg(f"Variant: {tmp}")
                        variant = tmp

                    if 'id="Typegoedkeuring"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="Typegoedkeuring"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        _ = D and dbg(f"Typegoedkeuring: {tmp}")
                        typegoedkeuring = tmp

                    if 'id="EersteToelatingsdatum"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="EersteToelatingsdatum"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        _ = D and dbg(f"{filename} EersteToelatingsdatum: {tmp}")
                        eerstetoelatingsdatum = tmp

                    if 'id="AfgDatKent"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="AfgDatKent"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        _ = D and dbg(f"{filename} AfgDatKent: {tmp}")
                        afg_dat_kent = tmp

                    if 'id="EersteAfgifteNederland"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="EersteAfgifteNederland"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        afg_dat_kent = tmp
                        _ = D and dbg(f"{filename} EersteAfgifteNederland: {tmp}")

                    if 'id="DatumAanvangTenaamstelling"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="DatumAanvangTenaamstelling"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        _ = D and dbg(f"{filename} DatumAanvangTenaamstelling: {tmp}")
                        if re.search(r"Niet geregistreerd", tmp, re.IGNORECASE):
                            op_naam = "????????"
                        else:
                            op_naam = tmp[6:10] + tmp[3:5] + tmp[0:2]

                    if 'id="DatumGdk"' in line:
                        tmp = line
                        tmp = re.sub(r'.*id="DatumGdk"', "", tmp)
                        tmp = re.sub(r"</div>.*", "", tmp)
                        tmp = re.sub(r">", "", tmp)
                        datum_gdk = "??" + tmp[8:10] + tmp[3:5] + tmp[0:2]
                        _ = D and dbg(f"{filename} DatumGdk: {datum_gdk}")

                if op_naam == "????????":
                    op_naam = datum_gdk
                _ = D and dbg(f"OpNaam: {op_naam}")
                kentekenfile.close()
                cartype = f"{variant};{uitvoering};{typegoedkeuring}; prijs: {prijs} {kleur}"  # noqa
                date20 = eerstetoelatingsdatum
                if date20 == "Niet geregistreerd":
                    date20 = afg_dat_kent
                if date20 == "Niet geregistreerd":
                    date20 = datum_gdk
                date20 = date20.replace("??", "20")
                if date20[:3] != "202":
                    _ = D and dbg(
                        f"Invalid date: {date20} {eerstetoelatingsdatum}, {afg_dat_kent}, {datum_gdk}"  # noqa
                    )
                    date20 = date20[6:10] + date20[3:5] + date20[0:2]
                    _ = D and dbg(f"Corrected date: {date20}")

                _ = D and dbg(
                    f"date20={date20}      {eerstetoelatingsdatum}, {afg_dat_kent}, {datum_gdk}"  # noqa
                )
                tuple_parameter = (
                    taxi,
                    export,
                    count20inch,
                    countlounge20inch,
                    count19inch,
                    countlounge19inch,
                    colormatte,
                    colormica,
                    colorsolid,
                    colormicapearl,
                    colormetallic,
                    variantscount,
                    variantscountnognietopnaam,
                )
                (
                    value,
                    taxi,
                    export,
                    count20inch,
                    countlounge20inch,
                    count19inch,
                    countlounge19inch,
                    colormatte,
                    colormica,
                    colorsolid,
                    colormicapearl,
                    colormetallic,
                    variantscount,
                    variantscountnognietopnaam,
                ) = get_variant(
                    pricelists,
                    pricelists_dates,
                    D,
                    tuple_parameter,
                    cartype,
                    False,
                    k,
                    date20,
                )
                if value == "ERROR":
                    msg = f"ERROR: kenteken {k} [{cartype}]\n"
                    errors.append(msg)
                    print(msg)
                    continue
                if not exists:
                    filename = f"kentekens/x.missing.{k}.html"
                    os.rename("x.missing", filename)
                cartype = cartype.rstrip()  # get rid of spaces at the end
                cartype = re.sub(
                    r";e9\*2018\/858\*11054\*0[134]; prijs: ", " Euro", cartype
                )
                new = f"{cartype} {value}"

                # Kleuren:
                # GEEL  Gravity Gold (Mat)
                # ZWART Phantom Black (Mica Parelmoer)
                # GROEN Digital Teal (Mica Parelmoer), Mystic Olive (Mica)
                # BLAUW Lucid Blue (Mica Parelmoer)
                # GRIJS Shooting Star (Mat), Cyber Grey (Metal.), Galactic Gray (Metal.) # noqa
                # WIT   Atlas White (Solid)
                new = re.sub(r"GEEL ", "Gravity Gold   ", new)
                new = re.sub(r"ZWART ", "Phantom Black  ", new)
                if "GROEN " in new and " (Olive)" in new:
                    new = new.replace(" (Olive)", "")
                    new = re.sub(r"GROEN ", "Mystic Olive   ", new)
                if "GROEN " in new and "Olive" not in new:
                    new = re.sub(r"GROEN ", "Digital Teal   ", new)
                new = re.sub(r"GROEN ", "GROEN          ", new)
                new = re.sub(r"BLAUW ", "Lucid Blue     ", new)
                if "GRIJS " in new and " (Shooting Star)" in new:
                    new = new.replace(" (Shooting Star)", "")
                    new = re.sub(r"GRIJS ", "Shooting Star  ", new)
                new = re.sub(r"GRIJS ", "Cyber/Galactic ", new)
                new = re.sub(r"WIT ", "Atlas White    ", new)

                new = re.sub(r"F5E..;E11.11 ", "", new)

                import_text = ""
                if (
                    eerstetoelatingsdatum != "Niet geregistreerd"
                    and eerstetoelatingsdatum != afg_dat_kent
                ):
                    _ = D and dbg(
                        f"EersteToelatingsdatum = {eerstetoelatingsdatum}, AfgDatKent = {afg_dat_kent}"  # noqa
                    )
                    yymmdd = (
                        eerstetoelatingsdatum[6:10]
                        + eerstetoelatingsdatum[3:5]
                        + eerstetoelatingsdatum[0:2]
                    )
                    yymmdd_import = (
                        afg_dat_kent[6:10] + afg_dat_kent[3:5] + afg_dat_kent[0:2]
                    )
                    import_text = f" ({yymmdd} geimporteerd {yymmdd_import})"
                    new = new + import_text

                new_missing = f"{k} {op_naam} {new}"
                print(new_missing)
                if not exists:
                    new_missing_list.append(new_missing)

                outfile.write(
                    f"{k} {op_naam} {kleur} {prijs}    {variant};{uitvoering};{typegoedkeuring}; prijs: {prijs} #{import_text}\n"  # noqa
                )

    print("\n\nNieuw gevonden gescande kentekens:\n[code]")
    sorted_list = sorted(
        new_missing_list, key=lambda x: (x[23:], x[7:], x[0], x[4:6], x[1:])
    )
    for entry in sorted_list:
        print(entry)
    print("[/code]\n")
    print("ERRORS")
    print("\n".join(errors))


main()
