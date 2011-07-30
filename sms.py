#!/usr/bin/python
import sys
import os
import csv
import re
from optparse import OptionParser

from myandroid import droid

from parsephoneno import phone_no

parser = OptionParser()
parser.add_option('-r', '--replyto', type='int',
                  help='reply to message with this id')
parser.add_option('-R', '--ReplyToLast', action='store_true',
                  help='reply to message with this id')
parser.add_option('-t', '--to', 
                  help='message recipient')
parser.add_option('-f', '--forward', 
                  help='phone number to lookup and forward')
parser.add_option('-p', '--phone', 
                  help='recipient to phone (instead of sms)')
parser.add_option('-n', '--nop', action='store_true',
                  help='dont actually do anything. dry run.')
opts, args = parser.parse_args()

if not args and not opts.phone and not opts.forward:
    print 'No message was specified!!'
    exit(2)

CSV_FILE = os.path.expanduser('~/.mobiles.csv')

def get_phone_list():
    return csv.reader(open(CSV_FILE))

px = list(get_phone_list())

def num_to_name(phone):
    matches = [p[0] for p in px for n in p[1].split(':') if n == phone]
    return matches[0] if matches else phone

def pick_mobile(recipient):
    recipient = recipient.lower()
    if re.match('^\d{5}$', recipient):
        '''phone_no only validates 10-digit numbers. 
        But we sometimes need to send an sms to 5-digit numbers too'''
        return (recipient, recipient)

    m = phone_no(recipient)
    if m:
        return (num_to_name(m), m)

    if re.match('^\+?\d+$', recipient) and opts.phone:
        return (num_to_name(recipient), recipient)
    
    names = [(p[0], n) 
             for p in px if re.search(recipient, p[0], re.I)
             for n in p[1].split(':')]

    if len(names) == 0:
        print 'Recipient: {0} not found'.format(recipient)
        exit(2)
    elif len(names) == 1:
        return names[0]
    else:
        choice = None
        while choice == None:
            for i, p in enumerate(names):
                print "{0}. {1[0]} - {1[1]}".format(i, p)
            try:
                choice = int(raw_input('Pick one: '))
            except ValueError:
                choice = None
        return names[choice]
        


if opts.replyto or opts.ReplyToLast:
    if opts.ReplyToLast:
        msgid = droid.smsGetMessageIds(False).result[0]
    else:
        msgid = opts.replyto
    msg = droid.smsGetMessageById(msgid).result
    to_num = msg['address']
else:
    to_num = opts.to or opts.phone


if not to_num:
    print 'No recipient specified'
    exit(1)

recipients = [pick_mobile(num) for num in to_num.split(',')]

msg = " ".join(args) or ""

if opts.forward:
    'Add this name+number to the sms msg'
    forward = pick_mobile(opts.forward)
    msg = '%s: %s. %s' % (forward[0],
                          forward[1],
                          msg)
    
if opts.phone:
    if len(recipients) > 1:
        print "Can't have more than one recipient for -phone"
        exit(2)
    r = recipients[0]
    print 'Calling ', r[0], r[1]
    if not opts.nop:
        droid.phoneCallNumber('+'+str(r[1]))
else:
    for r in recipients:
        print 'Sending to %s: %s. <<%s>>' % (r[0], r[1], msg)
        if not opts.nop:
            droid.smsSend('+'+str(r[1]), msg)
        else:
            print 'Not sent - because of -n'
