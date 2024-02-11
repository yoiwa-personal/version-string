import verstr_compare

from verstr_compare import verstr_compare, verstr_sortkey

import unittest

testcases = [
        "",
        "*",
        "0A",
        "2.",
        "2.*",
        "2.0",
        "2.007",
        "2.7",
        "2.07!",
        "2.7.90",
        "2.007=",
        "2.015.8",
        "2.15.08",
        "2.15.8",
        "2.20.0",
        "2.020.01",
        "2.020.1",
        "2.20.01",
        "2.20.1",
        "2.020.02",
        "2.20.02",
        "2.=",
        "3",
        "20",
        "100",
        "=",
        "A00",
        "A0",
        "A0D",
        "A3D",
        "A20C",
        "A100B",
        "AA",
        "AB",
        "ABC",
        "ABCD0B",
        "ABCD0B\0",
        "ABCD0B\0\0",
    ]

class TestVerstrCompare(unittest.TestCase):

    def test_compare(self):
        x = testcases[0]
        for y in testcases[1:]:
            self.assertNotEqual(verstr_compare(x, y), verstr_compare.LEFT)
            x = y

    def test_compare_total(self):
        x = testcases[0]
        for y in testcases[1:]:
            self.assertEqual(verstr_compare(x, y, total_order=True), verstr_compare.RIGHT)
            x = y

    def test_key(self):
        x = testcases[0]
        for y in testcases[1:]:
            self.assertLessEqual(verstr_sortkey(x), verstr_sortkey(y))
            x = y
        
    def test_key_total(self):
        x = testcases[0]
        for y in testcases[1:]:
            self.assertLessEqual(verstr_sortkey(x, total_order=True), verstr_sortkey(y, total_order=True))
            x = y

if __name__ == '__main__':
    unittest.main()

if False:
    import sys
    argv = sys.argv[1:]
    total_order = False

    if len(argv) > 0 and argv[0] == '-t':
        total_order = True
        argv.pop(0)

    if (argv[0] == 'testcases'):
        x = testcases.pop(0)
        for y in testcases:
            s = verstr_compare(x, y, total_order=total_order).symbol()
            print(f"{x!r} {s} {y!r}")
            x = y
    elif (argv[0] == 'testcases_key'):
        total_order = len(sys.argv) > 2
        x = testcases.pop(0)
        xk = verstr_sortkey(x, total_order=total_order)
        for y in testcases:
            yk = verstr_sortkey(y, total_order=total_order)
            s = "=" if xk == yk else "<" if xk < yk else ">"
            print(f"{x!r} {s} {y!r}\t({xk!r}, {yk!r})")
            x = y
            xk = yk
    elif (argv[0] == 'si'):
        sep = "-" if total_order else ""
        s = "1"
        t = "9"
        for x in range(200):
            print(_sortable_integer(s, _sep=sep))
            print(_sortable_integer(t, _sep=sep))
            s += "0"
            t += "9"
    else:
        _debug = True
        x, y = argv
        s = verstr_compare(x, y, total_order=total_order).symbol()
        print(f"{x!r} {s} {y!r}")
