import re
from titlecase import titlecase

def get_scaling_factor(value):
    # @TODO: translation...
    if value > 1000000000:
        return (1000000000, '{:,.1f} billion', '{:,.1f}bn')
    elif value > 1100000:
        return (1000000, '{:,.1f} million', '{:,.1f}m')
    return (1, '{:,.0f}', '{:,.0f}')


def scale_value(value, abbreviate=False):
    scale = get_scaling_factor(value)
    if abbreviate:
        return scale[2].format(value / scale[0])
    return scale[1].format(value / scale[0])


def correct_titlecase(s, first_upper=True):

    if not isinstance(s, str):
        return s

    if not s.isupper() and not s.islower():
        return s

    s = titlecase(s)

    substitutions = [
        (r'\b([^aeiouyAEIOUY,0-9]+)\b', lambda x: x[0].upper() if x[0] else x),
        (r'\'S\b', "'s"),
        (r'\'T\b', "'t"),
        (r'\bOf\b', "of"),
        (r'\bThe\b', "the"),
        (r'\bFor\b', "for"),
        (r'\bAnd\b', "and"),
        (r'\bIn\b', "in"),
        (r'\bWith\b', "with"),
        (r'\bTo\b', "to"),
        (r'\bUk\b', "UK"),
        (r'\bSt\b', "St"),
        (r'([0,4-9])Th\b', r"\1th"),
        (r'1St\b', "1st"),
        (r'2Nd\b', "2nd"),
        (r'3Rd\b', "3rd"),
        (r'\bmr\b', "Mr"),
        (r'\bmrs\b', "Mrs"),
        (r'\bltd\b', "Ltd"),
        (r'\bdr\b', "Dr"),
        (r'\bdrs\b', "Drs"),
        (r'\bcwm\b', "Cwm"),
        (r'\bClwb\b', "Clwb"),
    ]


    for pattern, replacement in substitutions:
        try:
            s = re.sub(pattern, replacement, s, flags=re.IGNORECASE)
        except:
            continue


    if first_upper:
        s = s[0].upper() + s[1:]
    return s
