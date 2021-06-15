import phonenumbers
from csv import DictReader
import sys
import pandas as pd

print("PRN,Guid,Language,Phone Number")
df = pd.read_csv(sys.argv[1])
for idx, row in df.iterrows():
    n = ''
    try:
        n = phonenumbers.parse(row['mobile'], "US")
    except Exception:
        try:
            n = phonenumbers.parse(row['home'], "US")
        except:
            continue
    n = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
    print("{},{},{},{}".format(row['PRN'], row['guid'], row['language'], n))
