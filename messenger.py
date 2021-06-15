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
from twilio.base.exceptions import TwilioRestException
from secret import *


class Messenger:

    from_ = None
    client = None

    def __init__(self, from_number=None):
        self.from_ = from_number
        self.client = Client(ACCOUNT_SID, AUTH_TOKEN)

    def try_send_message(self, body, to, from_number=None):
        try:
            self.client.messages.create(body=body, from_=from_number, to=to)
            print(f"{to} SENT: {body}")
        except TwilioRestException as e:
            print(f"{to} ERROR: {e}")

    async def send_message(self, body, to, from_number=None):
        if from_number == None:
            from_number = self.from_
        return await asyncio.get_event_loop().run_in_executor(None,
                partial(self.try_send_message, body, to, from_number=from_number))


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

async def send_from_file(messenger, messages_csv, people_csv, test=None): 
    group_to_message = {}
    seen = defaultdict(list)
    with open(messages_csv) as f:
        r = DictReader(f)
        group_to_message = {line['Group']: line['Message'] for line in r}
    with open(people_csv) as f:
        r = DictReader(f)
        tasks = []
        for line in r:
            g = line['Group']
            p = line['Phone Number']
            m = None
            if g in group_to_message:
                m = group_to_message[g]
            else:
                print(f"{p} ERROR: No message found for group {g}. Not sending a message.")
                continue
            if p in seen and m in seen[p]:
                print(f"{p} INFO: Skipping duplicate group {g}.")
                continue

            seen[p].append(m)
            if not test:
                tasks.append(messenger.send_message(m, p))
            else:
                print(f"{p} TEST: {m}")

        if not test:
            await asyncio.gather(*tasks)

        print("Done!")

def print_conversations(conversations, people_dict=None, responses_only=None):
    if people_dict == None:
        people_dict = {}
    for p in conversations:
        if responses_only and not any([m.direction == 'inbound' for m in conversations[p]]):
            continue
        print(p)
        for m in conversations[p]:
            identifier = people_dict[m.from_] if m.from_ in people_dict else m.from_
            carat = "<" if m.direction == 'inbound' else ">"
            print(f"{m.date_sent} | {identifier}{carat} {m.body}")
        print("-------------------------------------------")


async def main():
    parser = ArgumentParser()
    parser.add_argument('--list_all', action='store_true')
    parser.add_argument('--list_responses_only', action='store_true')
    parser.add_argument('--list_start', help="date to begin listing messages from")
    parser.add_argument('--list_end', help="date to begin listing messages from")
    parser.add_argument('--list_with', help="phone number to list conversation with")
    parser.add_argument('--messages', help="csv file containing messages")
    parser.add_argument('--people', help="csv file containing phone numbers")
    parser.add_argument('--send_to', help="phone number to send an individual message to") 
    parser.add_argument('--body', help="body of message to send to <to> number")
    parser.add_argument('--test', action='store_true', help="Print out what would be sent, without actually sending anything")
    args = parser.parse_args()

    m = Messenger(from_number=SENDER_NUMBER)
    if args.messages and args.people:
        if args.test:
            print("TEST")
        if input(f"Send {args.messages} to {args.people}? y/N: ") != 'y':
            print("Not sent")
            exit(1)
        await send_from_file(m, args.messages, args.people, test=args.test)

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
        print_conversations(conversations, people_dict={SENDER_NUMBER: " Noor Clinic"}, responses_only=args.list_responses_only)
    
asyncio.run(main())
