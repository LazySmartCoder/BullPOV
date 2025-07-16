from django import template
import locale

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
        num = str(int(float(value)))  # handles float input
        if len(num) <= 3:
            return num
        last3 = num[-3:]
        rest = num[:-3]
        # group digits in twos from the right
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        return ','.join(parts) + ',' + last3
    except:
        return value  # fallback if not a valid number