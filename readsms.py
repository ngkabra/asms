#!/usr/bin/python
import sys
import os
import csv
import re
from optparse import OptionParser

from myandroid import droid


parser = OptionParser()
parser.add_option('-r', '--read', action='store_true',
                  help='fetch read sms too')
parser.add_option('-n', '--num-msgs', type='int',
                  help='number of messages to fetch')
parser.add_option('-d', '--delete-msg', type='int', 
                  help='delete specified message')
parser.add_option('-D', '--delete-last', action='store_true',
                  help='delete the most recent message')
parser.add_option('-b', '--bulk-sms-show', action='store_true',
                  help='show only bulk smss')
parser.add_option('-B', '--bulk-sms-delete', action='store_true',
                  help='delete all bulk smss')
parser.add_option('-m', '--dont-mark', action='store_true',
                  help='do not mark messages as read')

opts, args = parser.parse_args()

CSV_FILE = os.path.expanduser('~/.mobiles.csv')

def get_phone_list():
    return csv.reader(open(CSV_FILE))

def num_to_name(phone):
    phone = phone[1:] # get rid of the +
    px = get_phone_list()
    matches = [p[0] for p in px for n in p[1].split(':') if n == phone]
    return matches[0] if matches else phone

def is_bulk_sms(msg):
    return not re.match('^\+\d+$', msg['address'])    

def delete_bulk_sms():
    msgs = droid.smsGetMessage(False).result
    if not msgs:
        print 'Nothing to delete'
    else:
        print 'Deleting', len(msgs), 'messages',
        for msgid in [m['_id'] for m in msgs if is_bulk_sms(m)]:
            print ',', msgid, 
            droid.smsDeleteMessage(msgid)
        print '...done'
    exit(0)

if opts.bulk_sms_delete:
    delete_bulk_sms()

if opts.delete_last or opts.delete_msg:
    if opts.delete_last:
        msgid = droid.smsGetMessageIds(False).result[0]
    else:
        msgid = int(opts.delete_msg)
    print 'Deleting msg', msgid, 
    # droid.smsDeleteMessage(msgid)
    print '...done'
    exit(0)

if opts.bulk_sms_show:
    msgs = [m for m in droid.smsGetMessages(False).result if is_bulk_sms(m)]
elif opts.num_msgs:
    # num_msgs implies get "read" messages
    msgids = droid.smsGetMessageIds(False).result[:opts.num_msgs]
    msgs = [droid.smsGetMessageById(msgid).result for msgid in msgids]
else:
    msgs = droid.smsGetMessages(not opts.read).result

for i, msg in enumerate(msgs):
    print '[{id} {alpha}] {num}: {msg}'.format(id=msg['_id'],
                                               alpha=chr(ord('a')+i),
                                               num=num_to_name(msg['address']),
                                               msg=msg['body'])

if not opts.dont_mark and not opts.read and not opts.num_msgs and not opts.bulk_sms_show:
    droid.smsMarkMessageRead([msg['_id'] for msg in msgs], True)

