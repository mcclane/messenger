from csv import DictReader
import sys
import asyncio
from functools import partial
import datetime
from datetime import datetime as dt
from dateutil.parser import parse
from collections import defaultdict
from pprint import pprint
from argparse import ArgumentParser

from twilio.rest import Client
from secret import *


class Messenger:

    from_ = None
    client = None

    def __init__(self, from_number=None):
        self.from_ = from_number
        self.client = Client(ACCOUNT_SID, AUTH_TOKEN)

    async def send_message(self, body, to, from_number=None):
        if from_number == None:
            from_number = self.from_
        return await asyncio.get_event_loop().run_in_executor(None,
                partial(self.client.messages.create, body=body, from_=from_number, to=to))


    async def list_messages(self, date_sent=None, from_number=None, to=None, limit=None, page_size=None):
        messages = await asyncio.get_event_loop().run_in_executor(None,
                partial(self.client.messages.list, 
                    date_sent=date_sent, from_=from_number, to=to, limit=limit, page_size=page_size))
        return messages

    async def conversations(self, start_date, end_date, with_number=None):
        date_diff = end_date - start_date
        dates = [start_date + datetime.timedelta(days=i) for i in range(date_diff.days)]
        # Leave raw to preserve pagination
        day_messages = await asyncio.gather(*[self.list_messages(date_sent=d, from_number=with_number) for d in dates])
#        day_messages.extend(await asyncio.gather(*[self.list_messages(date_sent=d, to=with_number) for d in dates]))

        conversations = defaultdict(list)
        for dm in day_messages:
            for m in dm:
                if m.direction == 'inbound':
                    conversations[m.from_].append(m)
                else:
                    conversations[m.to].append(m)

        # sort conversations by message date
        for p in conversations:
            conversations[p].sort(key=lambda m: m.date_sent)

        return conversations

async def send_from_file(m, messages_csv, people_csv): 
    language_to_message = {}
    with open(messages_csv) as f:
        r = DictReader(f)
        language_to_message = {line['Language']: line['Message'] for line in r}
    with open(people_csv) as f:
        r = DictReader(f)
        tasks = [m.send_message(language_to_message[line['Language']], line['Phone Number']) 
                for line in r]
    await asyncio.gather(*tasks)

def print_conversations(conversations, people_dict=None):
    if people_dict == None:
        people_dict = {}
    for p in conversations:
        print(p)
        for m in conversations[p]:
            identifier = people_dict[m.from_] if m.from_ in people_dict else m.from_
            carat = "<" if m.direction == 'inbound' else ">"
            print(f"{m.date_sent} | {identifier}{carat} {m.body}")
        print("-------------------------------------------")


async def main():
    parser = ArgumentParser()
    parser.add_argument('--list_all', action='store_true')
    parser.add_argument('--list_start', help="date to begin listing messages from")
    parser.add_argument('--list_end', help="date to begin listing messages from")
    parser.add_argument('--list_with', help="phone number to list conversation with")
    parser.add_argument('--messages', help="csv file containing messages")
    parser.add_argument('--people', help="csv file containing phone numbers")
    parser.add_argument('--send_to', help="phone number to send an individual message to") 
    parser.add_argument('--body', help="body of message to send to <to> number")
    args = parser.parse_args()

    m = Messenger(from_number=SENDER_NUMBER)
    if args.messages and args.people:
        if input(f"Send {args.messages} to {args.people}? y/N: ") != 'y':
            print("Not sent")
            exit(1)
        await send_from_file(m, args.messages, args.people)
        print("Sent!")

    if args.send_to and args.body:
        # do some processing with the phone number
        to = args.send_to
        if input(f"Send '{args.body}' to {args.send_to}? y/N: ") != 'y':
            print("Not sent")
            exit(1)
        print(await m.send_message(args.body, to))

    if args.list_all or args.list_start or args.list_end or args.list_with:
        start_date = parse(args.list_start) if args.list_start != None else dt(2021, 1, 1)
        end_date = parse(args.list_end) if args.list_end != None else dt(dt.now().year + 1, dt.now().month, dt.now().day)
        
        conversations = await m.conversations(start_date, end_date, args.list_with)
        print_conversations(conversations, people_dict={SENDER_NUMBER: " Noor Clinic"})
    
asyncio.run(main())
