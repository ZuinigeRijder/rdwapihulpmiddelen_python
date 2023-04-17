"""rdw.py"""
import json
import os
import re
import sys
from rdw_utils import (
    arg_has,
    execute_command,
    fill_prices,
    get_variant,
    my_die,
    safe_get_key,
)

sys.stdout.flush()  # Disable output buffering

D = arg_has("debug")


def dbg(line: str) -> bool:
    """print line if debugging"""
    if D:
        print(line)
    return D  # just to make a lazy evaluation expression possible


# ===============================================================================
# get_print_line
# parameter 1: line
# format:
#           1         2         3         4         5         6         7         8         9  # noqa
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# NDHN146DH 20210917 GRIJS      55600    F5E32;E11A11;e9*2018/858*11054*01; prijs: 55600 GRIJS     73 kWh Lounge  # noqa
# return printLine
# ===============================================================================
def get_print_line(line):
    """get_print_line"""
    _ = D and dbg(f"getPrintLine({line})")
    new = line[3:19] + line[39:93] + line[97:]
    new = re.sub(r";e9\*2018\/858\*11054\*0[134];", "", new)

    new = new.replace("prijs: ", "E")

    # Kleuren:
    # GEEL  Gravity Gold (Mat)
    # ZWART Phantom Black (Mica Parelmoer)
    # GROEN Digital Teal (Mica Parelmoer), Mystic Olive (Mica)
    # BLAUW Lucid Blue (Mica Parelmoer)
    # BRUIN Mystic Olive (Mica)
    # GRIJS Shooting Star (Mat), Cyber Grey (Metal.), Galactic Gray (Metal.)
    # WIT   Atlas White (Solid) Atlas White Matte
    new = new.replace("GEEL  ", "Gravity Gold   ")
    new = new.replace("ZWART ", "Phantom Black  ")
    if "GROEN " in new and " (Olive)" in new:
        new = new.replace(" (Olive)", "")
        new = new.replace("GROEN ", "Mystic Olive   ")
    if "GROEN " in new and "Olive" not in new:
        new = new.replace("GROEN ", "Digital Teal   ")
    new = new.replace("GROEN ", "GROEN          ")
    new = new.replace("BLAUW ", "Lucid Blue     ")
    new = new.replace("BRUIN ", "Mystic Olive   ")
    if "GRIJS " in new and (" (Shooting Star)" in new or "PROJECT45" in new):
        new = new.replace(" (Shooting Star)", "")
        new = new.replace("GRIJS ", "Shooting Star  ")
    new = new.replace("GRIJS ", "Cyber/Galactic ")
    if "WIT " in new and " (Atlas White Matte)" in new:
        new = new.replace("WIT   ", "White Matte    ")
    else:
        new = new.replace("WIT   ", "Atlas White    ")

    # get rid of internal information too, not interesting for end user
    new = re.sub(r"F5E..;E11.11 ", "", new)
    _ = D and dbg(f"getPrintLine RESULT: [{new}]")

    return new


def main():
    """main"""

    # this contains the pricelist per date and kWh battery and AWD
    pricelists_dates = ["20230101", "20220901", "20220501", "20220301", "20210501"]
    pricelists = fill_prices(D)

    variantscount = {}
    variantscountnognietopnaam = {}

    counttaxi = 0
    taxi = "Nee"

    countexport = 0
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

    # totals kleuren en andere statistieken
    count = 0
    colors = {}
    dates = {}

    # statistics
    longrangebattery = 0
    rwd = 0
    v2l = 0
    warmtepomp = 0
    panoramadak = 0
    solardak = 0

    project45 = 0
    lounge = 0
    connectplus = 0
    connect = 0
    style = 0

    model2022 = 0
    model2022_5 = 0
    model2023 = 0

    months = {
        "01": "januari",
        "02": "februari",
        "03": "maart",
        "04": "april",
        "05": "mei",
        "06": "juni",
        "07": "juli",
        "08": "augustus",
        "09": "september",
        "10": "oktober",
        "11": "november",
        "12": "december",
    }

    summary = arg_has("summary")
    overview = arg_has("overview")

    filename = "x.kentekens"
    cmd = ""

    opkentekenzonderexport = 0

    nognietopnaam_dict = {}
    with open("nognietopnaam.txt", "r", encoding="utf8") as nognietopnaamfile:
        for line in nognietopnaamfile:
            mstr = line.rstrip("\n")
            k = mstr[:6].rstrip("\n")
            if k == "":
                continue
            _ = D and dbg(f"Adding nognietopnaam: [{k}]")
            nognietopnaam_dict[k] = mstr

    opnaam_dict = {}
    with open("opnaam.txt", "r", encoding="utf8") as opnaamfile:
        for line in opnaamfile:
            mstr = line.rstrip("\n")
            k = mstr[:6].rstrip("\n")
            if k == "":
                continue
            _ = D and dbg(f"Adding opnaam: [{k}]")
            opnaam_dict[k] = mstr

    types = {}
    kentekensexported = {}
    special_kentekens = []
    gekend_op_naam_list = []
    nieuw_op_naam_list = []
    nieuw_nog_niet_op_naam_list = []
    geimporteerd = 0

    count_nog_niet_op_naam = 0
    nognietopnaam = []
    opnaam = []

    print("Getting IONIQ5 kentekens")
    if os.path.exists(filename):
        os.remove(filename)
    cmd = 'wget --quiet --output-document=x.kentekens "https://opendata.rdw.nl/api/id/m9d7-ebf2.json?$select=*&$order=`:id`+ASC&$limit=8000&$offset=0&$where=(%60handelsbenaming%60%20%3D%20%27IONIQ5%27)&$$read_from_nbe=true&$$version=2.1"'  # noqa
    execute_command(cmd, D, retry=False, die_on_error=True)
    print("Processing IONIQ5 kentekens")
    with open(filename, encoding="utf8") as json_file:
        json_data = json.load(json_file)

    aantal_kentekens = len(json_data)
    print(f"Aantal kentekens: {aantal_kentekens}")
    for hash_ in json_data:
        k = hash_["kenteken"]
        _ = D and dbg(f"kenteken = [{k}]")

        gekend_op_naam = False
        nieuw_op_naam = False

        gekend_niet_op_naam = False
        nieuw_niet_op_naam = False

        taxi = hash_["taxi_indicator"]
        if taxi == "Ja":
            counttaxi += 1

        export = hash_["export_indicator"]
        if export == "Ja":
            countexport += 1
        else:
            opkentekenzonderexport += 1

        kenteken = safe_get_key(hash_, "kenteken")
        if len(kenteken) != 6:
            os.rename(filename, filename + ".fout")
            my_die(f"Kenteken lengte fout: [{filename}],[{kenteken}] {hash_}")
        date = safe_get_key(
            hash_, "datum_eerste_afgifte_nederland"
        )  # niet gevuld wanneer kenteken nog niet op naam
        if date == "":
            date = safe_get_key(
                hash_, "datum_eerste_tenaamstelling_in_nederland"
            )  # changed 31 maart 2022, niet gevuld wanneer kenteken nog niet op naam
        date_bpm = safe_get_key(
            hash_, "registratie_datum_goedkeuring_afschrijvingsmoment_bpm_dt"
        )  # gevuld wanneer kenteken nog niet op naam
        if date_bpm != "":
            if len(date_bpm) == 23 and date_bpm[:2] == "20":
                date_bpm = date_bpm[:4] + date_bpm[5:7] + date_bpm[8:10]
                if date == date_bpm:
                    date_bpm = ""
                else:
                    _ = D and dbg(f"{k} dateBPM: [{date_bpm}]")
            else:
                print(f"WARNING: {k} dateBPM: [{date_bpm}]")
        if date == "" and date_bpm != "":
            date = date_bpm
            if k not in nognietopnaam_dict:
                nieuw_niet_op_naam = True
                print(
                    f"{k} Nieuw kenteken nog niet op naam {date_bpm}: [{filename}],[{date}]"  # noqa
                )
            else:
                gekend_niet_op_naam = True
                print(
                    f"{k} Gekend kenteken nog niet op naam {date_bpm}: [{filename}],[{date}]"  # noqa
                )
            nognietopnaam_dict[k] = k
        else:
            if k not in nognietopnaam_dict and k not in opnaam_dict:
                nieuw_op_naam = True
                print(
                    f"{k} Nieuw kenteken op naam {date_bpm}: [{filename}],[{date}]"  # noqa
                )
            else:
                gekend_op_naam = True
                if k in nognietopnaam_dict:
                    del nognietopnaam_dict[k]
                _ = D and dbg(
                    f"{k} Gekend kenteken op naam {date_bpm}: [{filename}],[{date}]"  # noqa
                )
        if len(date) != 8:
            my_die(f"Date lengte fout: [{filename}],[{date}]")
        date_toelating = safe_get_key(hash_, "datum_eerste_toelating")
        if date_toelating == "":
            date_toelating = date
            print(
                f"datetoelating overruled with {date}: [{filename}],[{date}]"
            )  # niet gevuld wanneer kenteken nog niet op naam
        if len(date_toelating) != 8:
            my_die(f"Date lengte fout: [{filename}],[{date_toelating}] {hash_}")
        if date != date_toelating:
            _ = D and dbg(f"Import {kenteken}: [{date_toelating}] [{date}]")
            geimporteerd += 1

        kleur = safe_get_key(hash_, "eerste_kleur")
        if kleur == "":
            my_die(f"Kleur leeg: [{filename}], [{kleur}]")
        if kleur not in ["GROEN", "WIT", "ZWART", "GEEL", "GRIJS", "BLAUW", "BRUIN"]:
            my_die(f"Kleur onbekend: [{filename}], [{kleur}]")
        kleur = kleur.ljust(10)

        prijs = safe_get_key(hash_, "catalogusprijs")
        if not prijs and kenteken != "R296FL":
            my_die(f"Prijs leeg: [{filename}], [{prijs}]")
        if len(prijs) != 5 and kenteken not in ["N770TS", "R296FL", "R303XF"]:
            my_die(f"Prijs verkeerd: [{filename}], [{prijs}]")

        variant = safe_get_key(hash_, "variant")
        uitvoering = safe_get_key(hash_, "uitvoering")
        typegoedkeuring = safe_get_key(hash_, "typegoedkeuringsnummer")
        if kenteken == "N331SH":
            variant = "F5E14"
            uitvoering = "E11B11"
            typegoedkeuring = "e9*2018/858*11054*01"
        elif kenteken == "P085GJ":
            variant = "F5E14"
            uitvoering = "E11B11"
            typegoedkeuring = "e9*2018/858*11054*01"
        elif kenteken == "N688DR":
            variant = "F5E32"
            uitvoering = "E11B11"
            typegoedkeuring = "e9*2018/858*11054*01"
        elif kenteken == "P380DR":
            variant = "F5E14"
        elif kenteken == "N770TS":
            prijs = 72300
        elif kenteken == "R296FL":
            variant = "F5E32"
            uitvoering = "E11B11"
            typegoedkeuring = "e9*2018/858*11054*01"
            prijs = 55600
        elif kenteken == "R303XF":
            variant = "F5E42"
            uitvoering = "E11A11"
            typegoedkeuring = "e9*2018/858*11054*01"
            prijs = 52426
        elif kenteken == "R818ZL":
            variant = "F5E42"
            uitvoering = "E11A11"
            typegoedkeuring = "e9*2018/858*11054*01"
        elif kenteken == "R494RB":
            variant = "F5E42"
            uitvoering = "E11A11"
            typegoedkeuring = "e9*2018/858*11054*04"

        if variant == "":
            my_die(f"{k} Variant leeg: [{filename}],[{variant}] {hash_}")
        if variant not in [
            "F5E14",
            "F5E32",
            "F5P41",
            "F5E42",
            "F5E54",
            "F5E62",
            "F5E24",
        ]:
            my_die(f"Variant verkeerd {kenteken}: [{filename}],[{variant}] {hash_}")

        if uitvoering == "":
            my_die(f"Uitvoering leeg: [{filename}],[{uitvoering}] {hash_}")
        if uitvoering not in ["E11A11", "E11B11"]:
            my_die(f"Uitvoering onbekend: [{filename}],[{uitvoering}] {hash_}")

        if typegoedkeuring == "":
            my_die(f"Typegoedkeuring leeg: [{filename}],[{typegoedkeuring}] {hash_}")
        if typegoedkeuring not in [
            "e9*2018/858*11054*01",
            "e9*2018/858*11054*03",
            "e9*2018/858*11054*04",
        ]:
            my_die(
                f"Typegoedkeuring verkeerd: [{filename}],[{typegoedkeuring}] {hash_}"
            )

        cartype = f"{variant};{uitvoering};{typegoedkeuring}; prijs: {prijs} {kleur}"
        date20 = date_toelating.replace(
            "??", "20"
        )  # nog niet op naam date can start with ??
        if date_bpm and int(date_bpm) < int(date_toelating):
            date20 = date_bpm
            if D:
                print(
                    f"Overruled {kenteken} met dateBPM: dateToelating: {date_toelating} with dateBPM {date_bpm}"  # noqa
                )
        date20 = date20.replace("??", "20")  # nog niet op naam date can start with ??
        if date20[:3] != "202":
            print(f"Invalid toelating date: {date20}")
            date20 = date20[6:10] + date20[3:5] + date20[0:2]
            print(f"Corrected toelating date: {date20}")
        if D and kenteken == "R059VH":
            print(
                f"{kenteken}, date: {date}, datetoelating: {date_toelating}, date20: {date20}, dateBPM: {date_bpm}"  # noqa
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
            pricelists, pricelists_dates, D, tuple_parameter, cartype, True, k, date20
        )

        if value == "ERROR":
            if os.path.exists(filename):
                os.remove(filename)
            continue
        cartype += value
        if date != date_toelating:
            cartype += f" ({date_toelating} geimporteerd {date})"
        elif date_bpm != "":
            cartype += f" (aanvraag kenteken {date_bpm})"
        types[cartype] = 1
        special_kenteken = f"{kenteken[0]}{kenteken[4:6]}{kenteken} {date} {kleur} {prijs}    {cartype}"  # noqa
        _ = D and print(special_kenteken)
        tmp = get_print_line(special_kenteken)
        if export == "Ja":
            kentekensexported[k] = tmp
        if gekend_niet_op_naam:
            print(f"Gekend kenteken niet op naam: {k} {tmp}")
            nognietopnaam.append(tmp)
            count_nog_niet_op_naam += 1
        if nieuw_niet_op_naam:
            print(f"Nieuw kenteken niet op naam: {k} {tmp}")
            nognietopnaam.append(tmp)
            nieuw_nog_niet_op_naam_list.append(tmp)
            count_nog_niet_op_naam += 1

        if gekend_op_naam:
            _ = D and dbg(f"Gekend kenteken op naam gezet: {k} {tmp}")
            opnaam.append(tmp)
            # tmp = specialKenteken[2:18] + specialKenteken[38:]
            # tmp = re.sub(r';e9\*2018\/858\*11054\*0[134]; prijs: ', ' Euro', tmp)
            # print(tmp)
            if k in nognietopnaam_dict:
                gekend_op_naam_list.append(f"{tmp}")
        if nieuw_op_naam:
            opnaam.append(tmp)
            # tmp = specialKenteken[2:18] + specialKenteken[38:]
            # tmp = re.sub(r';e9\*2018\/858\*11054\*0[134]; prijs: ', ' Euro', tmp)
            # print(tmp)
            print(f"Nieuw kenteken op naam gezet: {k} {tmp}")
            nieuw_op_naam_list.append(f"{tmp}")
        special_kentekens.append(special_kenteken)

    with open("exported.txt", "w", encoding="utf8") as exportedtxtfile:
        for values in sorted(
            kentekensexported.values(), key=lambda s: s[7:], reverse=True
        ):
            exportedtxtfile.write(f"{values}\n")

    importnietopnaam = 0
    with open("nognietopnaam.txt", "w", encoding="utf8") as nognietopnaamtxtfile:
        sorted_nog_niet_op_naam = sorted(nognietopnaam, key=lambda s: s[23:])
        for string in sorted_nog_niet_op_naam:
            if "geimporteerd" in string:
                importnietopnaam += 1
            nognietopnaamtxtfile.write(f"{string}\n")

    with open("opnaam.txt", "w", encoding="utf8") as opnaamtxtfile:
        sorted_op_naam = sorted(opnaam, key=lambda s: s[7:], reverse=True)
        for string in sorted_op_naam:
            opnaamtxtfile.write(f"{string}\n")

    if not overview and not summary:
        print(
            "\n\n"
            + "[h1]Kentekens gesorteerd met tenaamstelling datum, prijs, kleur, uitvoering[/h1]"  # noqa
        )
        print("[code]")

    for k in sorted(special_kentekens):
        count += 1
        print_line = get_print_line(k)
        if not overview and not summary:
            print(f"{print_line}")
        if not re.search(r"AWD", print_line, re.IGNORECASE) and not re.search(
            r"PROJECT45", print_line, re.IGNORECASE
        ):
            rwd += 1
        if re.search(r"Model 2023", print_line, re.IGNORECASE):
            model2023 += 1
        elif re.search(r"Model 2022\.5", print_line, re.IGNORECASE):
            model2022_5 += 1
        else:
            model2022 += 1
        if not re.search(r"58 kWh", print_line, re.IGNORECASE):
            longrangebattery += 1
        if re.search(r"V2L|PROJECT45|Lounge|Connect", print_line, re.IGNORECASE):
            v2l += 1
        if re.search(r"WP|PROJECT45|Lounge|Connect\+", print_line, re.IGNORECASE):
            warmtepomp += 1
        if re.search(r"Panoramadak", print_line, re.IGNORECASE) and not re.search(
            r"Olive", print_line
        ):
            panoramadak += 1
        if re.search(r"Zonnepanelen", print_line, re.IGNORECASE):
            solardak += 1
        if re.search(r"PROJECT45", print_line, re.IGNORECASE):
            solardak += 1
            project45 += 1
        elif re.search(r"LOUNGE", print_line, re.IGNORECASE):
            lounge += 1
        elif re.search(r"CONNECT\+", print_line, re.IGNORECASE):
            connectplus += 1
        elif re.search(r"CONNECT", print_line, re.IGNORECASE):
            connect += 1
        elif re.search(r"STYLE", print_line, re.IGNORECASE):
            style += 1
        else:
            print(f"ERROR: Model niet gevonden: [{print_line}]")

        date = k[10:16]
        if date.startswith("2"):
            if date in dates:
                dates[date] += 1
            else:
                dates[date] = 1

        color = k[19:29].rstrip()
        _ = D and dbg(f"KLEUR=[{color}]")
        if color in colors:
            colors[color] += 1
        else:
            colors[color] = 1

    if not overview and not summary:
        print("[/code]\n")

    if overview:
        print("\n\n[h1]Kentekens gesorteerd op kleur/uitvoering/datum[/h1]\n[code]")
        op_all = []
        for k in sorted(special_kentekens):
            print_line = get_print_line(k)
            op_all.append(print_line)
        sorted_all = sorted(op_all, key=lambda x: (x[23:], x[7:], x[0], x[4:6], x[1:]))
        for string in sorted_all:
            print(string)

        print("[/code]\n")
        print("\n\n[h1]Taxi's gesorteerd op kleur/uitvoering/datum[/h1]\n[code]")
        op_taxi = []
        for k in sorted(special_kentekens):
            print_line = get_print_line(k)
            if "(Taxi)" in print_line:
                op_taxi.append(print_line)
        sorted_taxi = sorted(
            op_taxi, key=lambda x: (x[23:], x[7:9], x[0], x[4:6], x[1:])
        )
        for string in sorted_taxi:
            print(string)

        print("[/code]\n")

        print("\n\n[h1]geexporteerd gesorteerd op kleur/uitvoering/datum[/h1]")
        print("[code]")
        op_export = []
        for k in sorted(special_kentekens):
            print_line = get_print_line(k)
            if "(geexporteerd)" in print_line:
                op_export.append(print_line)
        sorted_export = sorted(
            op_export, key=lambda a: (a[23:], a[7:10], a[0], a[4:6], a[1:])
        )
        for string in sorted_export:
            print(string)
        print("[/code]\n")

    # overview of kentekens per month
    for key in sorted(dates.keys()):
        jaar = key[:4]
        maand = key[4:6]
        if overview:
            continue
        if not summary:
            print(f"Skipping maand: {maand} in mode without parameters")
            continue
        # if jaar <= 2021 or maand <= 1: # do not give overviews after this month
        #     print(f"Skipping maand: {maand}")
        #     continue
        maandstring = months[maand]
        print(
            f"\n\n[h1]Kentekens op naam in {maandstring} {jaar}, kleur/uitvoering[/h1]"  # noqa
        )
        print("[code]")
        op_naam = []
        for k in sorted(special_kentekens):
            kenteken = k[3:9]
            _ = D and dbg(f"kenteken={kenteken} k=[{k}]")
            if kenteken not in nognietopnaam_dict:
                print_line = get_print_line(k)
                date = k[10:16]
                if date == key:
                    _ = D and dbg(print_line)
                    op_naam.append(print_line)
        sorted_opnaam = sorted(op_naam, key=lambda a: a[23:])
        for string in sorted_opnaam:
            print(string)
        print("[/code]\n")
    print()

    if not overview and not summary:
        sorted_nog_niet_op_naam = sorted(nognietopnaam, key=lambda s: s[23:])
        print(
            "\n\n"
            + "[h1]Kentekens nog niet op naam gesorteerd op kleur/uitvoering (datum is registratiedatum)[/h1]"  # noqa
        )
        print("[code]")
        for string in sorted_nog_niet_op_naam:
            print(string)
        print("[/code]" + "\n")

    if len(gekend_op_naam_list) > 0:
        print("Eerder gevonden kenteken op naam gezet:\n[code]")
        sorted_gekend_op_naam = sorted(
            gekend_op_naam_list, key=lambda x: (x[23:], x[7:10], x[0], x[4:6], x[1:])
        )
        for string in sorted_gekend_op_naam:
            print(string)
        print("[/code]\n")

    if len(nieuw_op_naam_list) > 0:
        print("Nieuw kenteken op naam gezet:\n[code]")
        sorted_nieuw_op_naam = sorted(
            nieuw_op_naam_list, key=lambda x: (x[23:], x[7:10], x[0], x[4:6], x[1:])
        )
        for string in sorted_nieuw_op_naam:
            print(string)
        print("[/code]\n")

    if len(nieuw_nog_niet_op_naam_list) > 0:
        print("Nieuw kenteken nog niet op naam:\n[code]")
        sorted_nieuw_nog_niet_op_naam_list = sorted(
            nieuw_nog_niet_op_naam_list,
            key=lambda x: (x[23:], x[7:10], x[0], x[4:6], x[1:]),
        )
        for string in sorted_nieuw_nog_niet_op_naam_list:
            print(string)
        print("[/code]\n")

    print(f"Totaal aantal IONIQ5 op (ooit) gekend kenteken: {count}")

    if count_nog_niet_op_naam > 0:
        print(
            f"Kenteken op naam RDW API: {aantal_kentekens}, zonder geexporteerd: {opkentekenzonderexport}, {geimporteerd} geimporteerd en {countexport} geexporteerd"  # noqa
        )
        print(
            f"[url=https://gathering.tweakers.net/forum/list_message/69802884#69802884]Kenteken nog niet op naam: {count_nog_niet_op_naam}[/url], waarvan {importnietopnaam} geimporteerd\n"  # noqa
        )

    pmodel2022 = model2022 / count * 100
    pmodel2022_5 = model2022_5 / count * 100
    pmodel2023 = model2023 / count * 100
    print(f"{pmodel2022:4.1f} % model 2022   ({model2022} maal)")
    print(f"{pmodel2023:4.1f} % model 2023   ({model2023} maal)")
    print(f"{pmodel2022_5:4.1f} % model 2022.5 ({model2022_5} maal)")
    print()

    if overview or summary:
        print("Kentekens op naam gezet per maand:")
        href = {
            "juni 2021": "https://gathering.tweakers.net/forum/list_message/69800422#69800422",  # noqa
            "juli 2021": "https://gathering.tweakers.net/forum/list_message/69800430#69800430",  # noqa
            "augustus 2021": "https://gathering.tweakers.net/forum/list_message/69800436#69800436",  # noqa
            "september 2021": "https://gathering.tweakers.net/forum/list_message/69800444#69800444",  # noqa
            "oktober 2021": "https://gathering.tweakers.net/forum/list_message/69800446#69800446",  # noqa
            "november 2021": "https://gathering.tweakers.net/forum/list_message/69800456#69800456",  # noqa
            "december 2021": "https://gathering.tweakers.net/forum/list_message/69800460#69800460",  # noqa
            "januari 2022": "https://gathering.tweakers.net/forum/list_message/70090920#70090920",  # noqa
            "februari 2022": "https://gathering.tweakers.net/forum/list_message/70788736#70788736",  # noqa
            "maart 2022": "https://gathering.tweakers.net/forum/list_message/71123634#71123634",  # noqa
            "april 2022": "https://gathering.tweakers.net/forum/list_message/71393214#71393214",  # noqa
            "mei 2022": "https://gathering.tweakers.net/forum/list_message/71723406#71723406",  # noqa
            "juni 2022": "https://gathering.tweakers.net/forum/list_message/72031366#72031366",  # noqa
            "juli 2022": "https://gathering.tweakers.net/forum/list_message/72300528#72300528",  # noqa
            "augustus 2022": "https://gathering.tweakers.net/forum/list_message/72624024#72624024",  # noqa
            "september 2022": "https://gathering.tweakers.net/forum/list_message/72989402#72989402",  # noqa
            "oktober 2022": "https://gathering.tweakers.net/forum/list_message/73324494#73324494",  # noqa
            "november 2022": "https://gathering.tweakers.net/forum/list_message/73660348#73660348",  # noqa
            "december 2022": "https://gathering.tweakers.net/forum/list_message/73984554#73984554",  # noqa
            "januari 2023": "https://gathering.tweakers.net/forum/list_message/74335278#74335278",  # noqa
            "februari 2023": "https://gathering.tweakers.net/forum/list_message/74650990#74650990",  # noqa
            "maart 2023": "https://gathering.tweakers.net/forum/list_message/74966656#74966656",  # noqa
        }

        # jaren
        years = {}

        for key in sorted(dates.keys()):
            count_date = dates[key]
            countstring = f"{count_date:3d}"
            jaar = key[:4]
            if jaar in years:
                years[jaar] = count_date + years[jaar]
            else:
                years[jaar] = count_date
            maand = key[4:6]
            maandjaarstring = f"{months[maand]} {jaar}"
            if maandjaarstring in href:
                print(
                    f"[url={href[maandjaarstring]}]{countstring} op naam gezet in {maandjaarstring}[/url]"  # noqa
                )
            else:
                print(f"{countstring} op naam gezet in {maandjaarstring}")
        print()

        for key in sorted(years.keys()):
            count_year = years[key]
            print(f"{count_year} op naam gezet in {key}")
        print()

        print(f"Statistieken van totaal {count} maal IONIQ 5:")

        plongrangebattery = longrangebattery / count * 100
        prwd = rwd / count * 100
        pv2l = v2l / count * 100
        pwp = warmtepomp / count * 100
        ppanoramadak = panoramadak / count * 100
        psolardak = solardak / count * 100

        pproject45 = project45 / count * 100
        plounge = lounge / count * 100
        pconnectplus = connectplus / count * 100
        pconnect = connect / count * 100
        pstyle = style / count * 100

        print(f"{pwp:4.1f} % warmtepomp (standaard vanaf Connect+, {warmtepomp} maal)")
        print(f"{plongrangebattery:4.1f} % grote batterij ({longrangebattery} maal)")
        print(f"{pv2l:4.1f} % vehicle to load (standaard vanaf Connect, {v2l} maal)")
        print(f"{prwd:4.1f} % achterwielaandrijving ({rwd} maal)")
        print(f"{ppanoramadak:4.1f} % panoramadak ({panoramadak} maal)")
        print(
            f"{psolardak:4.1f} % zonnepanelendak (alleen op PROJECT45, {solardak} maal)\n"  # noqa
        )

        print(f"{plounge:4.1f} % Lounge ({lounge} maal)")
        print(f"{pstyle:4.1f} % Style ({style} maal)")
        print(f"{pconnectplus:4.1f} % Connect+ ({connectplus} maal)")
        print(f"{pconnect:4.1f} % Connect ({connect} maal)")
        print(f"{pproject45:4.1f} % Project45 ({project45} maal)\n")

        pexport = countexport / count * 100
        print(f"{pexport:4.1f} % geexporteerd ({countexport} maal)")
        print()

        ptaxi = counttaxi / count * 100
        print(f"{ptaxi:4.1f} % Taxi ({counttaxi} maal)")
        print()

        p19 = count19inch / count * 100
        p20 = count20inch / count * 100
        lounge_count = countlounge19inch + countlounge20inch
        plounge19 = countlounge19inch / lounge_count * 100
        plounge20 = countlounge20inch / lounge_count * 100
        print(f"{p19:4.1f} % 19 inch banden ({count19inch} maal)")
        print(f"{p20:4.1f} % 20 inch banden ({count20inch} maal)")
        print(f"{plounge20:4.1f} % Lounge 20 inch banden ({countlounge20inch} maal)")
        print(f"{plounge19:4.1f} % Lounge 19 inch banden ({countlounge19inch} maal)")
        print()

        leganda = {
            "WIT": "Atlas White (Solid), Atlas White (Mat)",
            "GRIJS": "Shooting Star (Mat), Cyber Grey (Metal.), Galactic Gray (Metal.)",
            "GROEN": "Digital Teal (Mica Parelmoer), Mystic Olive (Mica)",
            "ZWART": "Phantom Black (Mica Parelmoer), Abyss Black (Mica Parelmoer)",
            "BLAUW": "Lucid Blue (Mica Parelmoer)",
            "GEEL": "Gravity Gold (Mat)",
            "BRUIN": "Mystic Olive (Mica)",
        }

        colorsoutput = []
        for key in sorted(colors.keys()):
            number = colors[key]
            perc = int((number / count * 100) + 0.5)
            legenda = leganda[key]
            percstr = f"{perc:2d}"
            cstr = f"{key:>6s}"
            cnt = f"{number:3d}"
            colorsoutput.append(f"{percstr}% {cstr} ({cnt} maal) {legenda}\n")

        print("[code]")
        sorted_output = sorted(colorsoutput, reverse=True)
        print("".join(sorted_output))

        pcolormatte = colormatte / count * 100
        pcolormetallic = colormetallic / count * 100
        pcolormica = colormica / count * 100
        pcolorsolid = colorsolid / count * 100
        pcolormicapearl = colormicapearl / count * 100

        print(f"{pcolormicapearl:4.1f} % Mica Parelmoer kleur ({colormicapearl} maal)")
        print(f"{pcolormatte:4.1f} % Mat kleur ({colormatte} maal)")
        print(f"{pcolormetallic:4.1f} % Metallic kleur ({colormetallic} maal)")
        print(f"{pcolormica:4.1f} % Mica Kleur ({colormica} maal)")
        print(f"{pcolorsolid:4.1f} % Solid kleur ({colorsolid} maal)")

        print("[/code]\n")

        for k, count in sorted(
            variantscount.items(),
            key=lambda x: (
                x[1],
                format(-int(x[0].split(" ")[0]), "05d")
                if x[0].split(" ")[0].isdigit()
                else x[0],
            ),
            reverse=True,
        ):
            _ = D and dbg(f"key: [{k}]")
            # count = variantscount[k]
            print(f"{count} maal op gekend kenteken variant: {k}")
            if k in variantscountnognietopnaam:
                count_nog_niet_op_naam = variantscountnognietopnaam[k]
                if count_nog_niet_op_naam > 0:
                    print(
                        f"waarvan {count_nog_niet_op_naam} maal kenteken nog niet op naam"  # noqa
                    )
            print()


main()
