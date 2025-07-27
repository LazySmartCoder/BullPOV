from django import template
import locale
from BullPOVApp.models import Stock

register = template.Library()

# Set locale for Indian comma formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
except locale.Error:
    # Fallback in case locale is not supported (like on Windows)
    locale.setlocale(locale.LC_ALL, '')

@register.filter
def crores(value):
    try:
        value = float(value)
        crores = value / 1e7  # Convert to crores
        formatted = locale.format_string("%.2f", crores, grouping=True)
        return f"₹{formatted} Crores"
    except Exception:
        return "₹0.00"

@register.filter
def comma(value):
    try:
        # Separate the whole and decimal parts
        float_val = float(value)
        integer_part, dot, decimal_part = f"{float_val:.2f}".partition(".")
        
        # Format integer part in Indian comma style
        if len(integer_part) <= 3:
            formatted = integer_part
        else:
            last3 = integer_part[-3:]
            rest = integer_part[:-3]
            parts = []
            while len(rest) > 2:
                parts.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                parts.insert(0, rest)
            formatted = ','.join(parts) + ',' + last3
        
        # Combine with decimal part
        return formatted + '.' + decimal_part
    except:
        return str(value)  # fallback if value is invalid

@register.simple_tag
def img(symbol):
    url = f"https://assets-netstorage.groww.in/stock-assets/logos2/{symbol}.png"
    if len(Stock.objects.get(Symbol = symbol).Logo) == 0 or Stock.objects.get(Symbol = symbol).Logo == "NIL":
        return True
    else:
        return False