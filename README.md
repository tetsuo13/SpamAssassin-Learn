# SpamAssassin Learn

[![Actions Status](https://github.com/tetsuo13/SpamAssassin-Learn/workflows/Continuous integration/badge.svg)](https://github.com/tetsuo13/SpamAssassin-Learn/actions)

SpamAssassin Learn is a script designed to work with [SpamAssassin](https://spamassassin.apache.org/) and the associated Bayesian classifier trainer, [sa-learn](https://spamassassin.apache.org/full/3.4.x/doc/sa-learn.html). It's purpose is to periodically scan two specific directories, one that contains spam messages and another ham, for all email accounts on a server. That function alone can be reproduced using a Bash script using several `for` loops however SpamAssassin Learn takes it a bit further.

Instead of simply reproducing

```
sa-learn --ham message_email_file
```

to learn messages, it will learn messages for specific users in order to maintain per-user Bayes. This works for systems where each email account has their own classifications. It mimics the command

```
sa-learn --ham --username=foo@example.com message_email_file
```

by automatically determining the user name by examining the email message. Emails assumed to be in maildir format.

It's designed to be run periodically from cron as often as is necessary even on system with high volume. It will only scan new messages since the last time it was run. Match the `--ago` parameter against how often the script is set to run from cron. So if you configure the script to run every 15 minutes then set `--ago=15`.

## Installing

There is no formal installation process. Instead, copy the `sa_learn.py` script convienent for use.

For example, if running from cron copy to the `/etc/cron.d` directory.

The script must be run with as a user that has permission to access the email messages as well as the SpamAssassin Bayesian database (when not using the SQL option). Unfortunately this typically means running as root.

## Usage

Synopsis:

```
sa_learn.py --base_dir BASE_DIR --ago AGO --spam_dir SPAM_DIR --ham_dir HAM_DIR
```

**base_dir**

The root directory where all email accounts are under.

For example, `/var/mail/vhosts` could be the root with the following subdirectories:

```
+--/var/mail/vhosts
   +--bar.com
   |  +--foo
   |  +--baz
   +--qux.com
      +--derry
```

This would be the structure for the following emails: foo@bar.com, baz@bar.com, derry@qux.com.

**ago**

Will find messages newer than this many minutes ago. If set to 15 then it will only search for messages created in the last 15 minutes.

This value should match the cron interval.

**spam_dir**

The subdirectory which contains messages which should be used to train as spam. This may not match exactly what's shown in the mail client. For example, if the folder shown in the client is "Junk" the directory may be .Junk instead.

**ham_dir**

The subdirectory which contains messages which should be used to train as ham.

```
sa_learn.py --base_dir /var/mail/vhosts --ago 15 --spam_dir .Junk --ham_dir .Trash
```

See also `sa_learn.py --help`.

## Tests

A standalone test runner is available by executing

```
./run_tests.py
```

## Notes

This script was running in production environments using [Dovecot](https://www.dovecot.org/) email server for years. It started out highly specialized but has since evolved to handle other situations.

## License

Project license can be found [here](LICENSE.md).

