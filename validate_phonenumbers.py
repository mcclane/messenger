import phonenumbers
from csv import DictReader
import sys

print("PRN,Language,Phone Number")
with open(sys.argv[1]) as f:
    r = DictReader(f)
    for line in r:
        n = ''
        try:
            n = phonenumbers.parse(line['mobile'], "US")
        except Exception:
            try:
                n = phonenumbers.parse(line['home'], "US")
            except:
                continue
        n = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
        print("{},{},{}".format(line['PRN'].strip(), line['Language'].strip(), n))
