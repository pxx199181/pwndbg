import gdb
import pwndbg.color
import pwndbg.enhance
import pwndbg.memory
import pwndbg.symbol
import pwndbg.typeinfo
import pwndbg.vmmap

LIMIT = 5

def get(address, limit=5):
    """
    Recursively dereferences an address.

    Returns:
        A list containing ``address``, followed by up to ``limit`` valid pointers.
    """
    result = []
    for i in range(limit):
        # Don't follow cycles, except to stop at the second occurrence.
        if result.count(address) >= 2:
            break

        result.append(address)
        try:
            address = int(pwndbg.memory.poi(pwndbg.typeinfo.ppvoid, address))
        except gdb.MemoryError:
            break

    return result


def format(value):
        chain = get(value, LIMIT)

        # Enhance the last entry
        # If there are no pointers (e.g. eax = 0x41414141), then enhance
        # the only element there is.
        if len(chain) == 1:
            enhanced = pwndbg.enhance.enhance(chain[-1])

        # Otherwise, the last element in the chain is the non-pointer value.
        # We want to enhance the last pointer value.
        elif len(chain) < LIMIT:
            enhanced = pwndbg.enhance.enhance(chain[-2])

        else:
            enhanced = '...'

        # Colorize the rest
        rest = []
        for link in chain[:-1]:
            symbol = pwndbg.symbol.get(link) or None
            if symbol:
                symbol = '%#x (%s)' % (link, symbol)
            rest.append(pwndbg.color.get(link, symbol))

        if len(chain) == 1:
            return enhanced

        return ' --> '.join(rest) + ' <-- ' + enhanced
