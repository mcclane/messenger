# messenger

Send messages from to a list of phone numbers. Created as a cheap, basic alternative to CareMessage, for use at the [Noor Clinic](https://slonoorfoundation.org/).

Minimal CLI at the moment. More coming.

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
