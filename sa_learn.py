#!/usr/bin/env python3

import argparse
import chardet
import datetime
import email
import os
import subprocess
import sys

from enum import Enum, unique, auto

@unique
class MessageType(Enum):
    SPAM = auto()
    HAM = auto()

def predict_encoding(file_path, n_lines=1024):
    '''Predict a file's encoding'''

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

def get_email(path):
    """Gets the destination email address from a specified email message.

    Args:
        path: Absolute path to email message.
    Returns:
        Destination email of None if it couldn't be found.
    """
    left_marker = 'for <'
    right_marker = '>;'

    try:
        predicted_encoding = predict_encoding(path)

        with open(path, encoding=predicted_encoding) as f:
            msg = email.message_from_string(f.read())
            for received in msg.get_all('Received'):
                if left_marker not in received:
                    continue
                email_address = received[received.index(left_marker) + len(left_marker):received.index(right_marker)]
                return email_address.lower()
            return None
    except Exception as e:
        print('Error processing %s: %s' % (path, e), file=sys.stderr)
        raise

def process_message(path, message_type):
    email = get_email(path)

    if not email:
        print('Could not find email in %s, try something else' % (path), file=sys.stderr)
        return

    args = ['/usr/bin/sa-learn']

    if message_type is MessageType.SPAM:
        args.append('--spam')
    else:
        args.append('--ham')

    args.append('--username=' + email)
    args.append('--siteconfigpath=/etc/spamassassin')
    args.append(path)

    print('Learning %s for %s' % (message_type, email))
    subprocess.run(args)

def suitable_for_learning(path):
    """Whether or not the email has already been marked by SpamAssassin.

    We only want to learn from messages that SpamAssassin has already marked,
    ie, they have the X-Spam-Status header. This is because there's no use in
    training on messages that aren't suitable anyway -- too large to be
    scanned or originated from a system process.

    Args:
        path: Absolute path to email message.
    Returns:
        Boolean if we should learn from the email.
    """

    try:
        with open(path) as f:
            return any('X-Spam-Status: ' in line for line in f.read().splitlines())
    except Exception as e:
        print('Error reading email %s: %s' % (path, e), file=sys.stderr)
    return False

def process_dir(base_path, ago, message_type):
    for root, dirs, files in os.walk(base_path):
        for fname in files:
            path = os.path.join(root, fname)
            st = os.stat(path)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)

            if mtime > ago and suitable_for_learning(path):
                process_message(path, message_type)

def main(base_dir, ago, spam_dir, ham_dir):
    ago_spam = datetime.datetime.now() - datetime.timedelta(minutes=ago)
    ago_ham = datetime.datetime.now() - datetime.timedelta(minutes=ago)

    for domain in os.listdir(base_dir):
        for account in os.listdir(os.path.join(base_dir, domain)):
            base_account_dir = os.path.join(base_dir, domain, account)

            process_dir(os.path.join(base_account_dir, spam_dir, 'new'), ago_spam, MessageType.SPAM)
            process_dir(os.path.join(base_account_dir, spam_dir, 'cur'), ago_spam, MessageType.SPAM)

            process_dir(os.path.join(base_account_dir, ham_dir, 'new'), ago_ham, MessageType.HAM)
            process_dir(os.path.join(base_account_dir, ham_dir, 'cur'), ago_ham, MessageType.HAM)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run sa-learn from SpamAssassin against spam and ham messages.')
    parser.add_argument('--base_dir', required=True,
                        help='Base directory to search under.')
    parser.add_argument('--ago', required=True,
                        help='Number of minutes to look back.')
    parser.add_argument('--spam_dir', required=True,
                        help='The folder in each email account where spam is located. Example: .Spam')
    parser.add_argument('--ham_dir', required=True,
                        help='The folder in each email account where ham is located. Example: .Trash')

    args = parser.parse_args()

    main(args.base_dir, args.ago, args.spam_dir, args.ham_dir)

