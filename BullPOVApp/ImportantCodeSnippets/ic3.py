'''
def indian_format(n):
        n = round(n, 2)
        s = f"{n:.2f}"
        if '.' in s:
            int_part, dec_part = s.split('.')
        else:
            int_part, dec_part = s, ""

        if len(int_part) > 3:
            start = int_part[-3:]
            rest = int_part[:-3]
            parts = []
            while len(rest) > 2:
                parts.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                parts.insert(0, rest)
            int_part = ','.join(parts + [start])
        return f"{int_part}.{dec_part}"

    def format_to_crores(amount):
        crores = amount / 1e7
        formatted = indian_format(crores)
        return f"({formatted}) Crores"
'''