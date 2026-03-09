from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def price_format(value):
    """Format price with comma as thousand separator, strip trailing decimal zeros.

    Examples: 15000.00 -> '15,000', 1000000.5 -> '1,000,000.5'
    """
    if value is None:
        return ''
    try:
        d = Decimal(str(value))
        if d == d.to_integral_value():
            return f'{int(d):,}'
        # Up to 2 decimal places, trailing zeros stripped
        formatted = f'{float(d):,.2f}'.rstrip('0')
        integer_part, decimal_part = formatted.split('.')
        return f'{integer_part}.{decimal_part}'
    except (ValueError, TypeError):
        return str(value)
