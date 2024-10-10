from decimal import Decimal, getcontext


def smart_round(number: float, ndigits: int = 10) -> float:
    """
    Smart rounding function to mitigate floating point operation errors.

    Args:
        - ``number`` (float): The number to be rounded.
        - ``ndigits`` (int, optional): The number of decimal places to round to. Defaults to 10.

    Returns:
        float: The rounded number.
    """
    getcontext().prec = ndigits + 2  # Set decimal context precision
    decimal_number = Decimal(str(number))  # Convert number to Decimal
    rounded_number = round(decimal_number, ndigits)  # Round using Decimal
    return float(rounded_number)  # Convert back to float
