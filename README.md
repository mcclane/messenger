# messenger

Send messages from a csv file of phone numbers. Created as a cheap, basic alternative to CareMessage.

# Requirement
- python3.7+ (asyncio)
- twilio

# Usage:
`python messenger.py <messsages.csv> <people.csv>`

## messages.csv format:
| Language | Message |
|----------|---------|
| Spanish | Hola Mundo |
| English | Hello World |

## people.csv format:
| phone number | language |
|--------------|----------|
| 1234567890 | English |
