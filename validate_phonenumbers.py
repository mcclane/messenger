import phonenumbers
from csv import DictReader
import sys
import pandas as pd

def format_number(mobile, home):
    n = ''
    try:
        n = phonenumbers.parse(mobile, "US")
    except Exception:
        try:
            n = phonenumbers.parse(home, "US")
        except:
            return None
    return phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)


print("PRN,Guid,Language,Phone Number")
df = pd.read_csv(sys.argv[1])
for idx, row in df.iterrows():
    n = format_number(row['mobile'], row['home'])
    print("{},{},{},{}".format(row['PRN'], row['guid'], row['language'], n))
