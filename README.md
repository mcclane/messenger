# messenger

Send messages from to a list of phone numbers. Created as a cheap, basic alternative to CareMessage, for use at the [Noor Clinic](https://slonoorfoundation.org/).

Minimal CLI at the moment. More coming.

# Requirement
- python3.7+ (asyncio)
- twilio

# Usage:
```
python messenger.py [-h] [-list_all] [--messages MESSAGES] [--people PEOPLE]

optional arguments:
  -h, --help           show this help message and exit
  -list_all
  --messages MESSAGES  csv file containing messages
  --people PEOPLE      csv file containing phone numbers
  ```
  
## messages.csv format:
| Language | Message |
|----------|---------|
| Spanish | Hola Mundo |
| English | Hello World |

## people.csv format:
| phone number | language |
|--------------|----------|
| 1234567890 | English |
