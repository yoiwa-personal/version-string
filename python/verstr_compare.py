"""
Comparison of two strings in version-string ordering.

It will consider sequences of digits as a unit and
applies numeric comparison on those.
Other elements are alphabetically ordered.

For example, "abc-2.20" > "abc-2.3", and "abc-2.20" < "def-2.3".

This module implements two functions:
 - verstr_compare.compare:
      compares two strings and returns the result of comparison.
 - verstr_compare.sortkey:
      generates an object for given string, that can be compared
      using ordinary operators.

Alias names verstr_compare and verstr_sortkey are provided for
easy imports.
"""

__copyright__ = """
(c) 2021- Yutaka OIWA. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__version__      = "1.0"
__author__       = "Yutaka OIWA"
__author_email__ = "yutaka@oiwa.jp"
__license__      = "Apache-2.0"

__all__ = ('verstr_compare', 'verstr_sortkey')


from enum import IntEnum as _IntEnum

class CompareResult(_IntEnum):
    """Results of comparison by verstr_compare.compare."""
    RIGHT = -1
    LESS_THAN = -1
    EQUAL = 0
    LEFT = 1
    GREATER_THAN = 1
    def symbol(self):
        return "<=>"[self.value + 1]

LEFTMOST_TOTAL_ORDER = object()

_debug = False

def compare(l, r, total_order=False):
    """Compare strings, treating sequences of digits as a numeric parts to compare.

    Return CompareResult.{LEFT, RIGHT, EQUAL} according to the larger input given.
    These enumerated values are equal to 1, 0, and -1, respectively.

    Some examples:

    "0A" < "A0" < "AA" < "AB" < "ABC" (usual string comparison)
    "3" < "20" < "100"                (numerics are so ordered)
    "A3D" < "A20C" < "A100B"          (numeric parts are so compared)
    "2.7" < "2.7.90" < "2.15.8" < "2.20.1"      (like version numbers)
    "2.007" < "2.015.8" == "2.15.08" < "2.20.1" (zero padding are ignored by default)
    "2.20.0" < "2.020.1" < "2.20.02"

    If total_order=True, if inputs are equal except for zero padding,
    it will compare number of padding zeros as a last resort, so that
    the comparison results are total. The order of comparison 
    for "same" numbers is out of specification.

    (Currently, longer zeros are treated as smaller.

    if total_order == True:
        "2.020.01" < "2.020.1" < "2.20.01" < "2.20.1" < "2.020.02"

    This rule will sometimes produce unintuitive order:
        "A00" < "A0", "A00!" < "A0!")
    """

    """
    As a special case, if total_order=verstr_compare.LEFTMOST_TOTAL_ORDER,
    ordering of zero-padded numbers are considered element-wise.
    This ordering is not consistent with default total_order=False.

    if total_order == LEFTMOST_TOTAL_ORDER:
        "2.020.01" < "2.020.1" < "2.020.02" < "2.20.01" < "2.20.1"

    # distinguish "20" and "020" in the second element at first.
    """
    _isdigit = lambda s: (s >= '0' and s <= '9')
    _d = _debug
    l = str(l)
    r = str(r)
    llen = len(l)
    rlen = len(r)

    if _d:
        r = r + "\0"
        l = l + "\0" # canaries for EOS index

    lp = 0
    rp = 0

    global_zeros = CompareResult.EQUAL
    
    while(True):
        if _d: print(f"main: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
        if lp == llen:
            if rp == rlen:
                if total_order:
                    return global_zeros
                else:
                    return CompareResult.EQUAL
            return CompareResult.RIGHT
        if rp == rlen:
            return CompareResult.LEFT

        if _isdigit(l[lp]) and _isdigit(r[rp]):
            zlp, zrp = lp, rp

            # consume leading zeros
            zeros = CompareResult.EQUAL
            while(lp < llen and l[lp] == '0' and
                  rp < rlen and r[rp] == '0'):
                if _d: print(f"c0B: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
                lp += 1
                rp += 1
            
            while(lp < llen and l[lp] == '0'):
                if _d: print(f"c0L: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
                zeros = CompareResult.RIGHT
                lp += 1
            while(rp < rlen and r[rp] == '0'):
                assert zeros != CompareResult.RIGHT
                zeros = CompareResult.LEFT
                if _d: print(f"c0R: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
                rp += 1

            if _d: print(f"zero: {lp}:{zlp}({lp - zlp}) {rp}:{zrp}({rp - zrp}): {l[lp]!r} {r[rp]!r} {zeros!r}")

            # read left-aligned digits

            digits = CompareResult.EQUAL

            while(lp < llen and _isdigit(l[lp]) and
                  rp < rlen and _isdigit(r[rp])):
                if digits == CompareResult.EQUAL:
                    if l[lp] != r[rp]:
                        digits = CompareResult.LEFT if l[lp] > r[rp] else CompareResult.RIGHT
                if _d: print(f"cdB: {lp} {rp}: {l[lp]!r} {r[rp]!r} {digits!r}")
                lp += 1
                rp += 1

            if(lp < llen and _isdigit(l[lp])):
                if _d: print(f"cdL: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
                # left longer
                return CompareResult.LEFT
            if(rp < rlen and _isdigit(r[rp])):
                if _d: print(f"cdR: {lp} {rp}: {l[lp]!r} {r[rp]!r}")
                # right longer
                return CompareResult.RIGHT

            if digits:
                if _d: print(f"digi: same len, digits larger={digits!r}")
                return digits
            if zeros:
                if _d: print(f"digi: same len, same digits, zero padding differs: shorter={zeros!r}")
                if total_order == LEFTMOST_TOTAL_ORDER:
                    return zeros
                else:
                    if not global_zeros:
                        global_zeros = zeros
            else:
                if _d: print(f"digi: same len, same digits, same padding; continue")
            continue

        # at least one input is non-digit: lexcographical comparison
        if l[lp] > r[rp]:
            return CompareResult.LEFT
        if l[lp] < r[rp]:
            return CompareResult.RIGHT
        lp += 1
        rp += 1
    raise AssertionError("notreached")

__neg_transtable = str.maketrans("0123456789", "9876543210")

def _sortable_integer(s, _integer=True, _sep=""):
    """represent non-zero-padded integer string in
    decodable and text-sortable representation.

    If input is a positive integer or a decimal string, it will return
    a self-delimiting string composed of decimal digits only, and its
    lexcographical sort order reflects the numeric order of inputs.

    Any preceeding 0s are ignored, and an empty string is treated as
    zero.

    For negative integers, output is "-" followed by self-delimiting
    digits, also lexcographically ordered.

    If input is non-decimal string, the behavior is undefined.

    """

    """The encoding scheme is an implementation detail and subject to
    change.  Currently, it is as follows:

    (1) Zero and single-digit numbers are zero-prepended:
      0 -> 00
      1 -> 01
      2 -> 02
      ...
      9 -> 09

    (2) Up to 9-digit numbers are prepended with (#digits - 1).
      10 -> 110
      99 -> 199
      100 -> 2100
      999 -> 2999
      ...
      999999999 -> 8999999999

    (3) If 10 or more digits are required, 
    the result starts with "9", 
    then (#digits - 10) is encoded using this scheme, 
    then the actual digits follows.

    [here after, parens and underbars are inserted for clarity.]

                          1000000000 -> 9001000000000  [10 digits encoded as 9_00]
                99.....9 [19 digits] -> 90999........9 [19 digits encoded as 9_09]
               10......0 [20 digits] -> 911010.......0 [20 digits encoded as 9_1_10]

             99.......9 [109 digits] -> 91999......9     [109 digits encoded as 9_1_99]
            10........0 [110 digits] -> 9210010........0 [110 digits encoded as 9_2_100]
      [this goes up to (10^9 + 9) digits, encoded as 9_8_999999999]
      99.......9 [10^9 + 9 digits]   -> 9(8_999999999)99.......9
      10........0 [10^9 + 10 digits] -> 9(900_1000000000)100.......0 (almost 2^30 digits)

      (next indirection happens in around 10^(2^30) digits, unlikely in reality.)
      (if happens, output is like "9(9(900_1000000000)1......0)10.....0".)

    (4) For negative numbers, the output starts with "-", then
    each absolute value converted by one of above three rules is
    translated to the 9's complement digits.
    For example,
               -1 -> "-98"   (1 -> "01"),
               -2 -> "-97"   (2 -> "02"),
               -9 -> "-90"   (9 -> "09"),
              -10 -> "-889"  (10 -> "110"),
              -42 -> "-857"  (42 -> "142"),
             -312 -> "-7687" (312 -> "2312"),
      -1234567890 -> "-0998765432109" (1234567890 -> "9001234567890").
    """
    
    """Currently, behavior for non-decimal string inputs is as follows:

    (1) It can be used for hexadecimal (or radix more-than-10) strings
        to produce sortable, self-delimiting hexadecimal (ditto)
        strings.

    (2) For octal or smaller-radix inputs, outputs are sortable,
        self-delimiting decimal strings.

    (3) If input is arbitrary string without preceeding 0s,
        you must specify _integer=False.
        Then output is as follows:

         - it is still self-delimiting.

         - leading zeros in inputs are NOT removed.

         - longer inputs will have output lexcographically larger.

         - within the same length inputs, the sorting order is preserved.

         - For non-empty strings, output will contain digits and characters
           in input only.  If empty input is allowed, it will still preserve
           ASCII-ness and printability.

        Some examples: (values in blackets are normal outputs with _integer=True)
                             "" -> "%"              ["00"]
                            " " -> "0 "
                            "0" -> "00"
                            "1" -> "01"
                           "-0" -> "1-0"            ["00"]
                           "-1" -> "1-1"            ["-98"]
                           "00" -> "100"            ["00"]
                         "-123" -> "3-123"          ["-2876"]
                    "123456789" -> "8123456789"
                   "0123456789" -> "9000123456789"  ["8123456789"]

    """

    # Hidden parameter _sep is for debugging: put "_" or "-" to
    # have output more readable.  It will be still self-delimiting,
    # if used _sep value is known.
    s = str(s)
    if s == "":
        return "00" if _integer else "%"

    neg = lambda x: x
    if (_integer and s[0] == "-"):
        neg = lambda x: "-" + x.translate(__neg_transtable)
        s = s[1:]
        if s == "": return "00"
    l = len(s)
    p = 0
    if _integer:
        while (p < l and s[p] == "0"):
            p += 1
        if (p == l): return "00"
        elif (p != 0):
            s = s[p:]
            l = len(s)
    if (l <= 9):
        return neg(str(l - 1) + _sep + s)
    else:
        return neg("9" + (_sep and "(") + _sortable_integer(l - 10, _sep=_sep) + (_sep and ")") + s)

def sortkey(s, total_order=False):
    """return sort key for version strings.

    The lexcographical order of returned keys are as consistent with
    the results of compare().
    """

    """internally, sort key is a sequence of characters,
    where numbers are replaced to the sortable representation above.

    If total_order is requested, the above is appended by "\0" and
    sequence of sortable encodes of negative numbers.
    "\0"s in original string are also replaced to avoid ambiguities.
    """

    _isdigit = lambda s: (s >= '0' and s <= '9')
    _d = _debug
    s = str(s)
    l = len(s)
    i = 0
    o = []
    zero_o = []
    while(i < l):
        p = i

        # text parts
        while(i < l and not _isdigit(s[i])):
            i += 1
        o.append(s[p:i])

        if i == l: break

        # leading zeros
        p = i
        while(i < l and s[i] == "0"):
            i += 1
        zero_o.append(-(i - p + 1))
        p = i
        while (i < l and _isdigit(s[i])):
            i += 1
        o.append(_sortable_integer(s[p:i]))
    o = "".join(o)
    if total_order:
        return o.replace("\0", "\0~") + "\0" + "".join(_sortable_integer(x) for x in zero_o)
        return [o] + zero_o
    else: return o

# for ease of access
for __k in ('LEFT', 'RIGHT', 'EQUAL', 'LESS_THAN', 'GREATER_THAN'):
    setattr(compare, __k, getattr(CompareResult, __k))
    globals()[__k] = getattr(CompareResult, __k)
del globals()[__k]

verstr_compare = compare
verstr_sortkey = sortkey
