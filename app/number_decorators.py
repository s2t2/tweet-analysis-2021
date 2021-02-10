
#
# NUMBER DECORATORS
#

def fmt_n(large_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param large_number (int) like 1_000_000_000

    Returns (str) like '1,000,000,000'
    """
    return f"{large_number:,.0f}"


def fmt_pct(decimal_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param decimal_number (float) like 0.95555555555

    Returns (str) like '95.5%'
    """
    return f"{(decimal_number * 100):.2f}%"


def fmt_usd(my_price):
    """
    Converts a numeric value to US dollar-formatted string, for printing and display purposes.

    Param: my_price (int or float) like 4000.444444

    Returns: $4,000.44
    """
    return f"${my_price:,.2f}" #> $12,000.71
