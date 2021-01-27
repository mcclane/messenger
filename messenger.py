from csv import DictReader
import sys
import asyncio

from twilio.rest import Client
from secret import *

def send_message(client, body, from_, to):
    return client.messages.create(body=body, from_=from_, to=to)

def get_language_to_messages(messages_csv):
    language_to_message = {}
    with open(messages_csv) as f:
        r = DictReader(f)
        for line in r:
            language_to_message[line['Language']] = line['Message']
    return language_to_message

async def main():
    if len(sys.argv) < 3:
        print("Usage: python messenger.py <messages.csv> <people.csv>")
        exit(1)

    messages_csv = sys.argv[1]
    people_csv = sys.argv[2]

    language_to_message = get_language_to_messages(messages_csv)

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    with open(people_csv) as f:
        r = DictReader(f)
        tasks = []
        for line in r:
            body = language_to_message[line['Language']]
            to = line['Phone Number']
            tasks.append(
                    asyncio.get_event_loop().run_in_executor(None, 
                        send_message, client, body, SENDER_NUMBER, to))

    await asyncio.gather(*tasks)



asyncio.run(main())
