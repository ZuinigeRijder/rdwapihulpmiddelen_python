"""rdwfinder.py"""
# pylint:disable=too-many-lines
import re
import subprocess
import sys
import traceback


# ===============================================================================
# my_die
# parameter 1: die string
# ===============================================================================
def my_die(txt):
    """my_die"""
    # Note that Python doesn't have a direct equivalent to Perl's croak
    # function, so I've replaced it with sys.exit(1) which will terminate
    # the program with an exit code of 1 (indicating an error).
    print("\n" + "?" * 80 + "\n")
    print(f"Error: {txt}\n\n")
    traceback.print_stack()
    sys.exit(1)


# ===============================================================================
# execute_command
# parameter 1: command
# return errorlevel
# ===============================================================================
def execute_command(command, debug, retry, die_on_error):
    """execute_command"""
    # Note that the Python code uses the subprocess module to execute the
    # command instead of the system function used in Perl.
    # The subprocess.call function is used with the shell=True argument to
    # execute the command in a shell.
    # The output is redirected to stderr with 2>&1 as in the original
    # Perl code.
    # The function returns the error code, which is obtained by masking the
    # returned value with 0xffff.
    if retry:
        try_count = 5
    else:
        try_count = 1
    while try_count > 0:
        if retry and try_count < 5:
            print(f"Retry: {try_count}")
        try_count -= 1
        if debug:
            print(f"Before: {command} 2>&1")
        return_code = subprocess.call(f"{command} 2>&1", shell=True)
        if return_code == 0:
            # everything Ok
            return 0
        elif return_code == 0xFF00:
            print(f"ERROR: Command [{command}] failed: {return_code}")
        elif return_code > 0x80:
            return_code >>= 8
            print(
                f"ERROR: Command [{command}] exited with non-zero exit status: {return_code}"  # noqa
            )
        else:
            print(
                f"ERROR: Command [{command}] exited with signal {return_code}"
            )  # noqa
    if die_on_error:
        my_die(f"execute_command failed with {return_code}: [$command]")
    return return_code & 0xFFFF


# ===============================================================================
# arg_has
# parameter 1: string argument to match
# ===============================================================================
def arg_has(string: str) -> bool:
    """arguments has string"""
    for i in range(1, len(sys.argv)):
        if string in sys.argv[i].lower():
            return True
    return False


# ===============================================================================
# round5
# parameter 1: integer number
# ===============================================================================
def round5(number):
    """round5"""
    remainder = number % 5
    if remainder < 3:
        return number - remainder
    else:
        return number - remainder + 5


# ===============================================================================
# fill_price
# parameter 1: hash reference
# parameter 2: variant
# parameter 3: prijscheck
# parameter 4: batterijgrootte
# parameter 5: AWD
# parameter 6: model2023
# parameter 7: prijslijst
# return variant
#
#  795 V2L (alleen op Style i.c.m. warmtepomp)
# 1200 WP (alleen beschikbaar op Style en Connect)
#  895 Panoramadak (alleen op Lounge)
# 1200 Zonnedak (alleen op Lounge)
# -750 geen FCA-JX en HDA2 (alleen op Connect, Connect+ en Lounge)
#  400 digitale binnenspiegel (2023 model)
# 1400 digitale buitenspiegels (2023 model)
#    0 19 inch wielen i.p.v. 20 inch (alleen Lounge)
#
def fill_price(
    debug, prices, variant, prijscheck, batterijgrootte, arg_awd, model2023, prijslijst
):
    """fill_price"""
    if debug:
        print(
            f"{variant}, {prijscheck}, {batterijgrootte}, {arg_awd:d}, {model2023:d}, {prijslijst}"  # noqa
        )
    zonder_fca_hda2 = prijslijst != "mei 2021"
    prijslijst = " (prijslijst " + prijslijst + ")"
    duurder1500 = False
    batterijgrootte = str(batterijgrootte) + " kWh "
    if arg_awd:
        batterijgrootte += "AWD "

    prices[prijscheck] = batterijgrootte + variant + prijslijst
    if duurder1500:
        prices[prijscheck + 1500] = (
            batterijgrootte + variant + prijslijst + " (1500 euro duurder)"
        )

    if variant == "Style":
        prices[prijscheck + 1200] = batterijgrootte + variant + " met WP" + prijslijst
        prices[prijscheck + 1200 + 795] = (
            batterijgrootte + variant + " met WP en V2L" + prijslijst
        )

        if duurder1500:
            prices[prijscheck + 1200 + 1500] = (
                batterijgrootte
                + variant
                + " met WP"
                + prijslijst
                + " (1500 euro duurder)"
            )
            prices[prijscheck + 1200 + 795 + 1500] = (
                batterijgrootte
                + variant
                + " met WP en V2L"
                + prijslijst
                + " (1500 euro duurder)"
            )
    elif variant == "Lounge":
        prices[prijscheck + 895] = (
            batterijgrootte + variant + " met Panoramadak" + prijslijst
        )
        prices[prijscheck + 1200] = (
            batterijgrootte + variant + " met Zonnepanelendak" + prijslijst
        )

        if duurder1500:
            prices[prijscheck + 895 + 1500] = (
                batterijgrootte
                + variant
                + " met Panoramadak"
                + prijslijst
                + " (1500 euro duurder)"
            )
            prices[prijscheck + 1200 + 1500] = (
                batterijgrootte
                + variant
                + " met Zonnepanelendak"
                + prijslijst
                + " (1500 euro duurder)"
            )

        if zonder_fca_hda2:
            prices[prijscheck - 750] = (
                batterijgrootte + variant + " zonder FCA-JX/HDA2" + prijslijst
            )
            prices[prijscheck + 895 - 750] = (
                batterijgrootte
                + variant
                + " met Panoramadak zonder FCA-JX/HDA2"
                + prijslijst
            )
            prices[prijscheck + 1200 - 750] = (
                batterijgrootte
                + variant
                + " met Zonnepanelendak zonder FCA-JX/HDA2"
                + prijslijst
            )

            if duurder1500:
                prices[prijscheck - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )
                prices[prijscheck + 895 - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " met Panoramadak zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )
                prices[prijscheck + 1200 - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " met Zonnepanelendak zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )

        if model2023:
            prices[prijscheck + 1400] = (
                batterijgrootte + variant + " met digitale buitenspiegels" + prijslijst
            )
            prices[prijscheck + 895 + 1400] = (
                batterijgrootte
                + variant
                + " met Panoramadak en digitale buitenspiegels"
                + prijslijst
            )
            prices[prijscheck + 1200 + 1400] = (
                batterijgrootte
                + variant
                + " met Zonnepanelendak en digitale buitenspiegels"
                + prijslijst
            )

            if zonder_fca_hda2:
                prices[prijscheck + 1400 - 750] = (
                    batterijgrootte
                    + variant
                    + " met digitale buitenspiegels zonder FCA-JX/HDA2"
                    + prijslijst
                )
                prices[prijscheck + 895 + 1400 - 750] = (
                    batterijgrootte
                    + variant
                    + " met Panoramadak en digitale buitenspiegels zonder FCA-JX/HDA2"
                    + prijslijst
                )
                prices[prijscheck + 1200 + 1400 - 750] = (
                    batterijgrootte
                    + variant
                    + " met Zonnepanelendak en digitale buitenspiegels zonder FCA-JX/HDA2"  # noqa
                    + prijslijst
                )
    elif variant == "Connect":
        prices[prijscheck + 1200] = batterijgrootte + variant + " met WP" + prijslijst

        if duurder1500:
            prices[prijscheck + 1200 + 1500] = (
                batterijgrootte
                + variant
                + " met WP"
                + prijslijst
                + " (1500 euro duurder)"
            )

        if zonder_fca_hda2:
            prices[prijscheck - 750] = (
                batterijgrootte + variant + " zonder FCA-JX/HDA2" + prijslijst
            )
            prices[prijscheck + 1200 - 750] = (
                batterijgrootte + variant + " met WP zonder FCA-JX/HDA2" + prijslijst
            )

            if duurder1500:
                prices[prijscheck - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )
                prices[prijscheck + 1200 - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " met WP zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )
    elif variant == "Connect+":
        if zonder_fca_hda2:
            prices[prijscheck - 750] = (
                batterijgrootte + variant + " zonder FCA-JX/HDA2" + prijslijst
            )
            if duurder1500:
                prices[prijscheck - 750 + 1500] = (
                    batterijgrootte
                    + variant
                    + " zonder FCA-JX/HDA2"
                    + prijslijst
                    + " (1500 euro duurder)"
                )
    else:
        my_die("PROGRAMERROR: variant niet bekend: " + variant)


def safe_get_key(hash_, key):
    """safe_get_key"""
    if key in hash_:
        return hash_[key]
    return ""


def safe_get_pricelists_key(pricelists, key):
    """safe_get_pricelists_key"""
    if key in pricelists:
        return pricelists[key]
    return {}


def get_prijs(pricelists, key, prijs):
    """get_prijs"""
    result = ""
    if key in pricelists:
        item = pricelists[key]
        if prijs in item:
            result = item[prijs]
    return result


# ===============================================================================
# find_variant_exact
# parameter 1: kenteken
# parameter 2: prijs
# parameter 3: variant
# parameter 4: model2023
# parameter 5: date
# return variant
def find_variant_exact(
    pricelists, pricelists_dates, debug, kenteken, prijs, variant, model2023, date
):
    """findVariantExact"""
    awd = variant == "F5E14" or variant == "F5E54"
    smallbattery = variant == "F5E42"
    result = ""
    for pricelist_date in pricelists_dates:
        if date < pricelist_date:
            if debug:
                print(f"Skipping pricelist {pricelist_date} for {date}")
            continue  # skip registration dates before prijslist date

        if debug:
            print(f"Checking {kenteken} pricelist {pricelist_date} for {date}")

        if smallbattery:
            if model2023:
                result = get_prijs(pricelists, f"{pricelist_date}_58_2023", prijs)
            else:
                result = get_prijs(pricelists, f"{pricelist_date}_58", prijs)
        elif awd:
            if model2023:
                result = get_prijs(pricelists, f"{pricelist_date}_77AWD", prijs)
            else:
                result = get_prijs(pricelists, f"{pricelist_date}_73AWD", prijs)
        else:
            if model2023:
                result = get_prijs(pricelists, f"{pricelist_date}_77", prijs)
            else:
                result = get_prijs(pricelists, f"{pricelist_date}_73", prijs)

        if result != "":
            break  # found result....

    if debug:
        small_str = ""
        if smallbattery:
            small_str = "1"
        awd_str = ""
        if awd:
            awd_str = "1"
        print(
            f"findVariantExact {kenteken} result {prijs}, {awd_str}, {small_str}: [{result}]"  # noqa
        )

    return result


# ===============================================================================
# find_helper
# parameter 1: prices hash
# parameter 2: prijs
# return variant
def find_helper(debug, prices, prijs):
    """find_helper"""
    found_delta = 9999999
    found_price = 0
    for price in prices:
        delta = abs(prijs - price)
        if delta < found_delta:
            found_delta = delta
            found_price = price
    result = safe_get_key(prices, found_price)
    if result != "" and found_delta != 0:
        delta = prijs - found_price
        abs_delta = abs(delta)
        if abs_delta == delta:
            result += f" $(E{abs_delta} duurder dan prijslijst)"
        else:
            result += f" $(E{abs_delta} goedkoper dan prijslijst)"
    if debug:
        print(f"findHelper result {prijs}: {result}")
    return result


# ===============================================================================
# find_variant_nearest
# parameter 1: kenteken
# parameter 2: prijs
# parameter 3: variant
# parameter 4: model2023
# parameter 5: date
# return variant
def find_variant_nearest(
    pricelists, pricelists_dates, debug, kenteken, prijs, variant, model2023, date
):
    """find_variant_nearest"""
    awd = variant in ("F5E14", "F5E54")
    smallbattery = variant == "F5E42"
    result = ""
    for pricelist_date in pricelists_dates:
        if int(date) < int(pricelist_date):
            if debug:
                print(f"Skipping nearest pricelist {pricelist_date} for {date}")
            continue  # skip registration dates before pricelist date
        if debug:
            print(
                f"Checking nearest pricelist {kenteken} pricelist {pricelist_date} for {date}"  # noqa
            )
        if smallbattery:
            if model2023:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_58_2023"),
                    prijs,
                )
            else:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_58"),
                    prijs,
                )
        elif awd:
            if model2023:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_77AWD"),
                    prijs,
                )
            else:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_73AWD"),
                    prijs,
                )
        else:
            if model2023:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_77"),
                    prijs,
                )
            else:
                result = find_helper(
                    debug,
                    safe_get_pricelists_key(pricelists, pricelist_date + "_73"),
                    prijs,
                )
        if result != "":
            break
    if debug:
        small_str = ""
        if smallbattery:
            small_str = "1"
        awd_str = ""
        if awd:
            awd_str = "1"
        print(
            f"findVariantNearest {kenteken} result {prijs}, {awd_str}, {small_str}: [{result}]"  # noqa
        )
    return result


def clean_variant(value, debug):
    """clean_variant"""
    stripped = value
    if debug:
        print(f"clean variant before: [{stripped}]")
    stripped = re.sub(
        r"\$\(E[0-9]+ [a-z]+ dan prijslijst\)", "", stripped
    )  # exclude dollar and goedkoper/duurder
    stripped = stripped.replace("$", "")  # exclude dollar in counting
    stripped = re.sub(
        r" \(model 202[^)]+\)", "", stripped, flags=re.IGNORECASE
    )  # exclude model in counting
    stripped = re.sub(
        r" \(Taxi\)", "", stripped, flags=re.IGNORECASE
    )  # exclude taxi in counting
    stripped = re.sub(
        r" \(geexporteerd\)", "", stripped, flags=re.IGNORECASE
    )  # exclude geexporteerd in counting
    stripped = re.sub(
        r" \(prijslijst [^)]+\)", "", stripped, flags=re.IGNORECASE
    )  # exclude prijslijst in counting
    stripped = re.sub(
        r" \(1500 euro duurder\)", "", stripped, flags=re.IGNORECASE
    )  # exclude prijsinfo in counting
    stripped = re.sub(
        r" \(1495 euro duurder\)", "", stripped, flags=re.IGNORECASE
    )  # exclude prijsinfo in counting
    stripped = re.sub(
        r" zonder FCA-JX/HDA2", "", stripped, flags=re.IGNORECASE
    )  # exclude prijsinfo in counting
    stripped = re.sub(
        r" \(19 inch banden\)", "", stripped, flags=re.IGNORECASE
    )  # exclude bandeninfo in counting
    stripped = re.sub(
        r" \(20 inch banden\)", "", stripped, flags=re.IGNORECASE
    )  # exclude bandeninfo in counting
    stripped = re.sub(
        r" \(Digital Teal, Mystic Olive met Panoramadak\)",
        "",
        stripped,
        flags=re.IGNORECASE,
    )  # exclude colorinfo in counting
    stripped = re.sub(r" \(Olive\)", "", stripped)  # exclude colorinfo in counting
    stripped = re.sub(
        r" \(Shooting Star\)", "", stripped
    )  # exclude colorinfo in counting
    stripped = re.sub(
        r" \(Atlas White Matte\)", "", stripped
    )  # exclude colorinfo in counting
    stripped = stripped.rstrip()  # remove trailing spaces
    if debug:
        print(f"clean variant after: [{stripped}]")
    return stripped


# ===============================================================================
# getVariant and count variants at the same time
# parameter 1: type
# parameter 2: opNaam
# parameter 3: kenteken
# parameter 4: date
# return type
#
# Legenda:
#
# Typegoedkeuring:
# e9*2018/858*11054*01 since 20210405 (model 2022)
# e9*2018/858*11054*03 since 20220210 (model 2022.5)
# e9*2018/858*11054*04 since 20220708 (model 2023)
#
# Variant:
# F5E14=72 kWh AWD (model 2022)
# F5E32=72 kWh RWD (model 2022)
# F5E42=58 kWh RWD (model 2022/2023)
# F5E54=77 kWh AWD (model 2023)
# F5E62=77 kWh RWD (model 2023)
#
# Uitvoering:
# E11A11=19 inch
# E11B11=20 inch
#
# Kleuren:
# GEEL  Gravity Gold (Mat)
# ZWART Phantom Black (Mica Parelmoer)
# GROEN Digital Teal (Mica Parelmoer), Mystic Olive (Mica)
# BLAUW Lucid Blue (Mica Parelmoer)
# GRIJS Shooting Star (Mat), Cyber Grey (Metal.), Galactic Gray (Metal.)
# WIT   Atlas White (Solid)
# BRUIN Mystic Olive (Mica)
#
#  795 V2L (alleen op Style i.c.m. warmtepomp)
# 1200 WP (alleen beschikbaar op Style en Connect)
#  895 Panoramadak (alleen op Lounge)
# 1200 Zonnedak (alleen op Lounge)
# -750 geen FCA-JX en HDA2 (alleen op Connect, Connect+ en Lounge)
#  400 digitale binnenspiegel (2023 model)
# 1400 digitale buitenspiegels (2023 model)
#    0 19 inch wielen i.p.v. 20 inch (alleen Lounge)
#
# Extra prijzen kleuren
#  695 Wit
#  895 Mica/Metallic
# 1095 Matte
#
# ===============================================================================
def get_variant(
    pricelists,
    pricelists_dates,
    debug,
    par,
    fulltype,
    op_naam,
    kenteken,
    date,
):
    """get_variant"""
    value = "ERROR"

    (
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
    ) = par

    if debug:
        print(f"#kenteken: {kenteken}")
        print(f"#fulltype: {fulltype}")
        print(f"#opNaam  : {op_naam:d}")
        print(f"#date    : {date}")

    if int(date) < 20210401 or int(date) > 20240101:
        my_die(f"Unexpected date: {date} for {kenteken} {fulltype}\n")

    kleur = "GRIJS"
    inch20 = True

    # F5E14;E11B11;e9*2018/858*11054*01; prijs: 59600 GRIJS
    # $variant;$uitvoering;$typegoedkeuring; prijs: $prijs $kleur";
    #           1         2         3         4         5         6         7         8
    # 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
    variant, uitvoering, typegoedkeuring, prijskleur = fulltype.split(";")
    prijskleur = re.sub(" +", " ", prijskleur)  # multiple spaces replaced by one
    prijskleur = prijskleur.strip()  # remove leading/trailing space

    if not prijskleur.startswith("prijs: "):
        my_die(f"Geen prijs in fulltype: {fulltype}")

    if variant == "F5E14":
        value = "73 kWh AWD"
    elif variant == "F5E32":
        value = "73 kWh"
    elif variant == "F5E42":
        value = "58 kWh"
    elif variant == "F5E54":
        value = "77 kWh"
    elif variant == "F5E62":
        value = "77 kWh"
    elif variant == "F5E24":  # error??
        value = "58 kWh"
    else:
        my_die(f"ERROR: variant {variant} fout voor {kenteken}: {fulltype}")

    if uitvoering != "E11A11" and uitvoering != "E11B11":
        my_die(f"ERROR: uitvoering {uitvoering} fout voor {kenteken}: {fulltype}")

    inch20 = uitvoering == "E11B11"

    if inch20 and variant == "F5E42":
        my_die("58 kWh and 20 inch not possible")

    if (
        typegoedkeuring != "e9*2018/858*11054*01"
        and typegoedkeuring != "e9*2018/858*11054*03"
        and typegoedkeuring != "e9*2018/858*11054*04"
    ):
        my_die(
            f"ERROR: typegoedkeuring {typegoedkeuring} fout voor {kenteken}: {fulltype}"
        )

    model2023 = typegoedkeuring == "e9*2018/858*11054*04"

    prijskleur = prijskleur.replace("prijs: ", "")
    prijsstr, tempkleur = prijskleur.split()
    prijs = int(prijsstr)
    kleur = tempkleur
    if kleur not in ["WIT", "GRIJS", "GROEN", "ZWART", "BLAUW", "GEEL", "BRUIN"]:
        my_die(f"ERROR: kleur {kleur} fout voor {kenteken}: {fulltype}")

    if (prijs < 4200 or prijs > 71000) and prijs not in [
        42000,
        72300,
        33589,
        37831,
        5242655,
        78650,
    ]:
        my_die(f"ERROR: prijs {prijs} fout voor {kenteken}: {fulltype}")
    if debug:
        print(f"#prijs   : {prijs}")
    # round prijs to multiple of 5 euro
    prijs = round5(prijs)
    if debug:
        print(f"#prijs5  : {prijs}")
        print(f"#kleur   : {kleur}")

    prijs2 = prijs
    if variant == "F5E14":
        if prijs == 58000:
            value = "PROJECT45"
        elif kenteken in ["L162KD", "L430TK", "L431TK", "L432TK", "N309TK", "P229NR"]:
            value = "PROJECT45$"

    if value != "PROJECT45" and value != "PROJECT45$":
        if kleur == "WIT":
            if model2023:
                prijs -= 695
                prijs2 -= 1095
            else:
                prijs -= 695
                prijs2 = 0
        elif kleur == "ZWART":
            prijs -= 895
            prijs2 = 0
        elif kleur == "BLAUW":
            if date > "20220801":
                prijs2 -= 895
            else:
                prijs -= 895
                prijs2 = 0
        elif kleur == "GEEL":
            prijs -= 1095
            prijs2 = 0
        elif kleur == "GRIJS":
            prijs -= 895
            prijs2 -= 1095
        elif kleur == "GROEN":
            prijs2 -= 895
        elif kleur == "BRUIN":
            prijs2 = 0
        else:
            my_die(f"PROGRAMERROR: kleur {kleur} fout voor {kenteken}: {fulltype}")

        found_variant = find_variant_exact(
            pricelists,
            pricelists_dates,
            debug,
            kenteken,
            prijs,
            variant,
            model2023,
            date,
        )
        found_variant2 = ""
        if prijs != prijs2 and prijs2 != 0:
            found_variant2 = find_variant_exact(
                pricelists,
                pricelists_dates,
                debug,
                kenteken,
                prijs2,
                variant,
                model2023,
                date,
            )

        if found_variant == "" and found_variant2 == "":
            found_variant = find_variant_nearest(
                pricelists,
                pricelists_dates,
                debug,
                kenteken,
                prijs,
                variant,
                model2023,
                date,
            )
            found_variant2 = ""
            if prijs != prijs2 and prijs2 != 0:
                found_variant2 = find_variant_nearest(
                    pricelists,
                    pricelists_dates,
                    debug,
                    kenteken,
                    prijs2,
                    variant,
                    model2023,
                    date,
                )
                delta1 = 9999999
                delta2 = 9999999
                if re.search(r"dan prijslijst\)", found_variant):
                    string = re.sub(r".*\$\(E", "", found_variant)
                    string = re.sub(r" [a-z]+ dan prijslijst\).*", "", string)
                    delta1 = int(string)
                if re.search(r"dan prijslijst\)", found_variant2):
                    string = re.sub(r".*\$\(E", "", found_variant2)
                    string = re.sub(r" [a-z]+ dan prijslijst\).*", "", string)
                    delta2 = int(string)
                if abs(delta2) < abs(delta1):
                    found_variant = ""
                else:
                    found_variant2 = ""

        if found_variant != "" and found_variant2 != "":
            if kleur != "GROEN":
                if debug:
                    print(
                        f"WARNING: 2 variants found for {kenteken} {kleur}: [{found_variant}] and [{found_variant2}]"  # noqa
                    )

        if kleur == "GRIJS":
            if found_variant2 != "":
                found_variant2 += " (Shooting Star)"
                if found_variant != "":
                    if debug:
                        print(
                            f"Found DUBBEL GRIJS {kenteken}: {fulltype} -> [{found_variant}],[{found_variant2}]"  # noqa
                        )
                    found_variant2 = ""
                    if debug:
                        print(f"{kenteken} Genomen: {fulltype} -> {found_variant}")
        elif kleur == "WIT":
            if found_variant2 != "":
                found_variant2 += " (Atlas White Matte)"
                if found_variant != "":
                    if debug:
                        print(
                            f"Found DUBBEL WHITE {kenteken}: {fulltype} -> [{found_variant}],[{found_variant2}]"  # noqa
                        )
                    if model2023:
                        found_variant = ""
                        if debug:
                            print(f"{kenteken} Genomen: {fulltype} -> {found_variant2}")
                    else:
                        found_variant2 = ""
                        if debug:
                            print(f"{kenteken} Genomen: {fulltype} -> {found_variant}")
        elif kleur == "GROEN":
            if found_variant != "":
                found_variant += " (Olive)"
                if debug:
                    print(
                        f"Found OLIVE GROEN {kenteken}: {fulltype} -> {found_variant}"  # noqa
                    )
            if found_variant != "" and found_variant2 != "":
                if re.search("Panoramadak", found_variant, re.IGNORECASE):
                    found_variant2 += " (Digital Teal, Mystic Olive met Panoramadak)"
                    if debug:
                        print(
                            f"Found DUBBEL GROEN {kenteken}: {fulltype} -> [{found_variant}],[{found_variant2}]"  # noqa
                        )
                    found_variant = ""
                else:
                    if debug:
                        print(
                            f"Found UNEXPECTED DUBBEL GROEN {kenteken}: {fulltype} -> [{found_variant}],[{found_variant2}]"  # noqa
                        )
                    found_variant = ""  # assume digital teal
                    if debug:
                        print(f"{kenteken} Genomen: {fulltype} -> {found_variant2}")

        if found_variant == "":
            found_variant = found_variant2
        value = found_variant
        if debug:
            print(f"#value={value}")

    if inch20:
        if "Lounge" not in value and "PROJECT45" not in value:
            value += " (20 inch banden)"
    else:
        if "Lounge" in value or "PROJECT45" in value:
            value += " (19 inch banden)"

    if inch20:
        count20inch += 1
        if "Lounge" in value:
            countlounge20inch += 1
    else:
        count19inch += 1
        if "Lounge" in value:
            countlounge19inch += 1

    if taxi == "Ja":
        value += " (Taxi)"
        if debug:
            print(f"VALUE: {value}")

    if export == "Ja":
        value += " (geexporteerd)"
        if debug:
            print(f"VALUE: {value}")

    if debug:
        value += f" ({typegoedkeuring})"
    if typegoedkeuring == "e9*2018/858*11054*01":
        value += " (model 2022)"
    elif typegoedkeuring == "e9*2018/858*11054*03":
        value += " (model 2022.5)"
    elif typegoedkeuring == "e9*2018/858*11054*04":
        value += " (model 2023)"

    if kleur == "WIT":
        if re.search(r"\(Atlas White Matte\)", value, re.IGNORECASE):
            colormatte += 1
        else:
            colorsolid += 1
    elif kleur == "ZWART":
        colormicapearl += 1
    elif kleur == "BLAUW":
        colormicapearl += 1
    elif kleur == "GEEL":
        colormatte += 1
    elif kleur == "GRIJS":
        if re.search(r"\(Shooting Star\)", value, re.IGNORECASE):
            colormatte += 1
        else:
            colormetallic += 1
    elif kleur == "GROEN":
        if re.search(r"\(Olive\)", value, re.IGNORECASE):
            colormica += 1
        else:
            colormicapearl += 1
    elif kleur == "BRUIN":
        colormica += 1
    else:
        my_die(f"PROGRAMERROR: kleur {kleur} fout voor {kenteken}: {fulltype}")

    stripped = clean_variant(value, debug)
    if stripped in variantscount:
        variantscount[stripped] += 1
    else:
        variantscount[stripped] = 1
    if not op_naam:
        if stripped in variantscountnognietopnaam:
            variantscountnognietopnaam[stripped] += 1
        else:
            variantscountnognietopnaam[stripped] = 1
    if debug:
        print(f"#RETURN: [{value}]")

    return_value = (
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
    )

    return return_value


def fill_prices(d):  # pylint:disable=invalid-name
    """fill_prices"""
    pricelists = {}

    # ========== model2022 ============================================================
    # model 2022 prijslijst mei 2021 (prijslijst mei 2022 1500 euro duurder)
    p_mei2021_small = {}
    p_mei2021_big = {}
    p_mei2021_awd = {}
    par = "mei 2021"
    fill_price(d, p_mei2021_small, "Style", 42505, 58, False, False, par)
    fill_price(d, p_mei2021_small, "Connect", 46505, 58, False, False, par)
    fill_price(d, p_mei2021_small, "Connect+", 49505, 58, False, False, par)
    fill_price(d, p_mei2021_small, "Lounge", 51705, 58, False, False, par)

    fill_price(d, p_mei2021_big, "Style", 45505, 73, False, False, par)
    fill_price(d, p_mei2021_big, "Connect", 49505, 73, False, False, par)
    fill_price(d, p_mei2021_big, "Connect+", 52505, 73, False, False, par)
    fill_price(d, p_mei2021_big, "Lounge", 54705, 73, False, False, par)

    fill_price(d, p_mei2021_awd, "Connect", 53505, 73, True, False, par)
    fill_price(d, p_mei2021_awd, "Connect+", 56505, 73, True, False, par)
    fill_price(d, p_mei2021_awd, "Lounge", 58705, 73, True, False, par)

    pricelists["20210501_58"] = p_mei2021_small
    pricelists["20210501_73"] = p_mei2021_big
    pricelists["20210501_73AWD"] = p_mei2021_awd

    # model 2022 prijslijst maart 2022:
    p_mrt22_small = {}
    p_mrt22_big = {}
    p_mrt22_awd = {}
    par = "maart 2022"
    fill_price(d, p_mrt22_small, "Style", 42805, 58, False, False, par)
    fill_price(d, p_mrt22_small, "Connect", 46905, 58, False, False, par)
    fill_price(d, p_mrt22_small, "Connect+", 49905, 58, False, False, par)
    fill_price(d, p_mrt22_small, "Lounge", 52305, 58, False, False, par)

    fill_price(d, p_mrt22_big, "Style", 46405, 73, False, False, par)
    fill_price(d, p_mrt22_big, "Connect", 50505, 73, False, False, par)
    fill_price(d, p_mrt22_big, "Connect+", 53505, 73, False, False, par)
    fill_price(d, p_mrt22_big, "Lounge", 55905, 73, False, False, par)

    fill_price(d, p_mrt22_awd, "Connect", 54505, 73, True, False, par)
    fill_price(d, p_mrt22_awd, "Connect+", 57505, 73, True, False, par)
    fill_price(d, p_mrt22_awd, "Lounge", 59905, 73, True, False, par)

    # also take into account korting
    e300 = "maart 2022 E300 korting"
    e400 = "maart 2022 E400 korting"
    e600 = "maart 2022 E600 korting"
    e900 = "maart 2022 E900 korting"
    e1000 = "maart 2022 E1000 korting"
    e1200 = "maart 2022 E1200 korting"
    fill_price(d, p_mrt22_small, "Style", 42805 - 300, 58, False, False, e300)
    fill_price(d, p_mrt22_small, "Connect", 46905 - 400, 58, False, False, e400)
    fill_price(d, p_mrt22_small, "Connect+", 49905 - 400, 58, False, False, e400)
    fill_price(d, p_mrt22_small, "Lounge", 52305 - 600, 58, False, False, e600)

    fill_price(d, p_mrt22_big, "Style", 46405 - 900, 73, False, False, e900)
    fill_price(d, p_mrt22_big, "Connect", 50505 - 1000, 73, False, False, e1000)
    fill_price(d, p_mrt22_big, "Connect+", 53505 - 1000, 73, False, False, e1000)
    fill_price(d, p_mrt22_big, "Lounge", 55905 - 1200, 73, False, False, e1200)

    fill_price(d, p_mrt22_awd, "Connect", 54505 - 1000, 73, True, False, e1000)
    fill_price(d, p_mrt22_awd, "Connect+", 57505 - 1000, 73, True, False, e1000)
    fill_price(d, p_mrt22_awd, "Lounge", 59905 - 1200, 73, True, False, e1200)

    pricelists["20220301_58"] = p_mrt22_small
    pricelists["20220301_73"] = p_mrt22_big
    pricelists["20220301_73AWD"] = p_mrt22_awd

    # model 2022 prijslijst mei 2022: 1500 euro duurder dan jan 2022
    p_mei22_small = {}
    p_mei22_big = {}
    p_mei22_awd = {}
    par = "mei 2022"
    fill_price(d, p_mei22_small, "Style", 44305, 58, False, False, par)
    fill_price(d, p_mei22_small, "Connect", 48405, 58, False, False, par)
    fill_price(d, p_mei22_small, "Connect+", 51405, 58, False, False, par)
    fill_price(d, p_mei22_small, "Lounge", 53805, 58, False, False, par)

    fill_price(d, p_mei22_big, "Style", 47905, 73, False, False, par)
    fill_price(d, p_mei22_big, "Connect", 52005, 73, False, False, par)
    fill_price(d, p_mei22_big, "Connect+", 55005, 73, False, False, par)
    fill_price(d, p_mei22_big, "Lounge", 57405, 73, False, False, par)

    fill_price(d, p_mei22_awd, "Connect", 56005, 73, True, False, par)
    fill_price(d, p_mei22_awd, "Connect+", 59005, 73, True, False, par)
    fill_price(d, p_mei22_awd, "Lounge", 61405, 73, True, False, par)

    # also take into account korting
    e300 = "mei 2022 E300 korting"
    e400 = "mei 2022 E400 korting"
    e600 = "mei 2022 E600 korting"
    e900 = "mei 2022 E900 korting"
    e1000 = "mei 2022 E1000 korting"
    e1200 = "mei 2022 E1200 korting"
    fill_price(d, p_mei22_small, "Style", 44305 - 300, 58, False, False, e300)
    fill_price(d, p_mei22_small, "Connect", 48405 - 400, 58, False, False, e400)
    fill_price(d, p_mei22_small, "Connect+", 51405 - 400, 58, False, False, e400)
    fill_price(d, p_mei22_small, "Lounge", 53805 - 600, 58, False, False, e600)

    fill_price(d, p_mei22_big, "Style", 47005, 73, False, False, e900)
    fill_price(d, p_mei22_big, "Connect", 51005, 73, False, False, e1000)
    fill_price(d, p_mei22_big, "Connect+", 54005, 73, False, False, e1000)
    fill_price(d, p_mei22_big, "Lounge", 56205, 73, False, False, e1200)

    fill_price(d, p_mei22_awd, "Connect", 55005, 73, True, False, e1000)
    fill_price(d, p_mei22_awd, "Connect+", 58005, 73, True, False, e1000)
    fill_price(d, p_mei22_awd, "Lounge", 60205, 73, True, False, e1200)

    pricelists["20220501_58"] = p_mei22_small
    pricelists["20220501_73"] = p_mei22_big
    pricelists["20220501_73AWD"] = p_mei22_awd

    # model 2022 prijslijst september: 1495 euro duurder dan mei 2022
    p_sep22_small = {}
    p_sep22_big = {}
    p_sep22_awd = {}
    par = "sept 2022"
    fill_price(d, p_sep22_small, "Style", 45800, 58, False, False, par)
    fill_price(d, p_sep22_small, "Connect", 49900, 58, False, False, par)
    fill_price(d, p_sep22_small, "Connect+", 52900, 58, False, False, par)
    fill_price(d, p_sep22_small, "Lounge", 55300, 58, False, False, par)

    fill_price(d, p_sep22_big, "Style", 49400, 73, False, False, par)
    fill_price(d, p_sep22_big, "Connect", 53500, 73, False, False, par)
    fill_price(d, p_sep22_big, "Connect+", 56500, 73, False, False, par)
    fill_price(d, p_sep22_big, "Lounge", 58900, 73, False, False, par)

    fill_price(d, p_sep22_awd, "Connect", 57500, 73, True, False, par)
    fill_price(d, p_sep22_awd, "Connect+", 60500, 73, True, False, par)
    fill_price(d, p_sep22_awd, "Lounge", 62900, 73, True, False, par)

    # also take into account korting
    e300 = "sept 2022 E300 korting"
    e400 = "sept 2022 E400 korting"
    e600 = "sept 2022 E600 korting"
    e900 = "sept 2022 E900 korting"
    e1000 = "sept 2022 E1000 korting"
    e1200 = "sept 2022 E1200 korting"
    fill_price(d, p_sep22_small, "Style", 45800 - 300, 58, False, False, e300)
    fill_price(d, p_sep22_small, "Connect", 49900 - 400, 58, False, False, e400)
    fill_price(d, p_sep22_small, "Connect+", 52900 - 400, 58, False, False, e400)
    fill_price(d, p_sep22_small, "Lounge", 55300 - 600, 58, False, False, e600)

    fill_price(d, p_sep22_big, "Style", 48500, 73, False, False, e900)
    fill_price(d, p_sep22_big, "Connect", 52500, 73, False, False, e1000)
    fill_price(d, p_sep22_big, "Connect+", 55500, 73, False, False, e1000)
    fill_price(d, p_sep22_big, "Lounge", 57700, 73, False, False, e1200)

    fill_price(d, p_sep22_awd, "Connect", 56500, 73, True, False, e1000)
    fill_price(d, p_sep22_awd, "Connect+", 59500, 73, True, False, e1000)
    fill_price(d, p_sep22_awd, "Lounge", 61700, 73, True, False, e1200)

    pricelists["20220901_58"] = p_sep22_small
    pricelists["20220901_73"] = p_sep22_big
    pricelists["20220901_73AWD"] = p_sep22_awd

    # ========== model2023 ============================================================
    # model 2023 prijslijst maart 2022
    p_mrt22_small_23 = {}
    p_mrt22_big_23 = {}
    p_mrt22_awd_23 = {}
    par = "maart 2022"
    fill_price(d, p_mrt22_small_23, "Style", 44305, 58, False, True, par)
    fill_price(d, p_mrt22_small_23, "Connect", 48405, 58, False, True, par)
    fill_price(d, p_mrt22_small_23, "Connect+", 51405, 58, False, True, par)
    fill_price(d, p_mrt22_small_23, "Lounge", 53805, 58, False, True, par)

    fill_price(d, p_mrt22_big_23, "Style", 47905, 77, False, True, par)
    fill_price(d, p_mrt22_big_23, "Connect", 52005, 77, False, True, par)
    fill_price(d, p_mrt22_big_23, "Connect+", 55005, 77, False, True, par)
    fill_price(d, p_mrt22_big_23, "Lounge", 57405, 77, False, True, par)

    fill_price(d, p_mrt22_awd_23, "Connect", 56005, 77, True, True, par)
    fill_price(d, p_mrt22_awd_23, "Connect+", 59005, 77, True, True, par)
    fill_price(d, p_mrt22_awd_23, "Lounge", 61405, 77, True, True, par)

    pricelists["20220301_58_2023"] = p_mrt22_small_23
    pricelists["20220301_77"] = p_mrt22_big_23
    pricelists["20220301_77AWD"] = p_mrt22_awd_23

    # model 2023 prijslijst mei 2022
    p_mei22_small_23 = {}
    p_mei22_big_23 = {}
    p_mei22_awd_23 = {}
    par = "mei 2022"
    fill_price(d, p_mei22_small_23, "Style", 44305, 58, False, True, par)
    fill_price(d, p_mei22_small_23, "Connect", 48405, 58, False, True, par)
    fill_price(d, p_mei22_small_23, "Connect+", 51405, 58, False, True, par)
    fill_price(d, p_mei22_small_23, "Lounge", 53805, 58, False, True, par)

    fill_price(d, p_mei22_big_23, "Style", 47905, 77, False, True, par)
    fill_price(d, p_mei22_big_23, "Connect", 52005, 77, False, True, par)
    fill_price(d, p_mei22_big_23, "Connect+", 55005, 77, False, True, par)
    fill_price(d, p_mei22_big_23, "Lounge", 57405, 77, False, True, par)

    fill_price(d, p_mei22_awd_23, "Connect", 56005, 77, True, True, par)
    fill_price(d, p_mei22_awd_23, "Connect+", 59005, 77, True, True, par)
    fill_price(d, p_mei22_awd_23, "Lounge", 61405, 77, True, True, par)

    pricelists["20220501_58_2023"] = p_mei22_small_23
    pricelists["20220501_77"] = p_mei22_big_23
    pricelists["20220501_77AWD"] = p_mei22_awd_23

    # model 2023 prijslijst september: 1495 euro duurder dan mei 2022
    p_sep22_small_23 = {}
    p_sep22_big_23 = {}
    p_sep22_awd_23 = {}
    par = "sept 2022"
    fill_price(d, p_sep22_small_23, "Style", 45800, 58, False, True, par)
    fill_price(d, p_sep22_small_23, "Connect", 49900, 58, False, True, par)
    fill_price(d, p_sep22_small_23, "Connect+", 52900, 58, False, True, par)
    fill_price(d, p_sep22_small_23, "Lounge", 55300, 58, False, True, par)

    fill_price(d, p_sep22_big_23, "Style", 49400, 77, False, True, par)
    fill_price(d, p_sep22_big_23, "Connect", 53500, 77, False, True, par)
    fill_price(d, p_sep22_big_23, "Connect+", 56500, 77, False, True, par)
    fill_price(d, p_sep22_big_23, "Lounge", 58900, 77, False, True, par)

    fill_price(d, p_sep22_awd_23, "Connect", 57500, 77, True, True, par)
    fill_price(d, p_sep22_awd_23, "Connect+", 60500, 77, True, True, par)
    fill_price(d, p_sep22_awd_23, "Lounge", 62900, 77, True, True, par)

    pricelists["20220901_58_2023"] = p_sep22_small_23
    pricelists["20220901_77"] = p_sep22_big_23
    pricelists["20220901_77AWD"] = p_sep22_awd_23

    # model 2023 prijslijst januari 2023: 1400 euro duurder dan september 2022
    p_jan23_small_23 = {}
    p_jan23_big_23 = {}
    p_jan23_awd_23 = {}
    par = "jan 2023"
    fill_price(d, p_jan23_small_23, "Style", 47200, 58, False, True, par)
    fill_price(d, p_jan23_small_23, "Connect", 51300, 58, False, True, par)
    fill_price(d, p_jan23_small_23, "Connect+", 54300, 58, False, True, par)
    fill_price(d, p_jan23_small_23, "Lounge", 56700, 58, False, True, par)

    fill_price(d, p_jan23_big_23, "Style", 50800, 77, False, True, par)
    fill_price(d, p_jan23_big_23, "Connect", 54900, 77, False, True, par)
    fill_price(d, p_jan23_big_23, "Connect+", 57900, 77, False, True, par)
    fill_price(d, p_jan23_big_23, "Lounge", 60300, 77, False, True, par)

    fill_price(d, p_jan23_awd_23, "Connect", 58900, 77, True, True, par)
    fill_price(d, p_jan23_awd_23, "Connect+", 61900, 77, True, True, par)
    fill_price(d, p_jan23_awd_23, "Lounge", 64300, 77, True, True, par)

    pricelists["20230101_58_2023"] = p_jan23_small_23
    pricelists["20230101_77"] = p_jan23_big_23
    pricelists["20230101_77AWD"] = p_jan23_awd_23

    # model 2023 prijslijst mei 2023: 1000 euro duurder dan januari 2023
    p_mei23_small_23 = {}
    p_mei23_big_23 = {}
    p_mei23_awd_23 = {}
    par = "mei 2023"
    fill_price(d, p_mei23_small_23, "Style", 48200, 58, False, True, par)
    fill_price(d, p_mei23_small_23, "Connect", 52300, 58, False, True, par)
    fill_price(d, p_mei23_small_23, "Connect+", 55300, 58, False, True, par)
    fill_price(d, p_mei23_small_23, "Lounge", 57700, 58, False, True, par)

    fill_price(d, p_mei23_big_23, "Style", 51800, 77, False, True, par)
    fill_price(d, p_mei23_big_23, "Connect", 55900, 77, False, True, par)
    fill_price(d, p_mei23_big_23, "Connect+", 58900, 77, False, True, par)
    fill_price(d, p_mei23_big_23, "Lounge", 61300, 77, False, True, par)

    fill_price(d, p_mei23_awd_23, "Connect", 59900, 77, True, True, par)
    fill_price(d, p_mei23_awd_23, "Connect+", 62900, 77, True, True, par)
    fill_price(d, p_mei23_awd_23, "Lounge", 65300, 77, True, True, par)

    pricelists["20230501_58_2023"] = p_mei23_small_23
    pricelists["20230501_77"] = p_mei23_big_23
    pricelists["20230501_77AWD"] = p_mei23_awd_23

    return pricelists
