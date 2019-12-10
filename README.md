### FreeIPA Notification
Notify IPA Users for password expiration and locked users to admin
1. Obtain a keytab and save it to a secure location with obtain_keytab.sh
2. Create a new virtual environment and install requirements.txt

```pip install -r requirements.txt```
3. Run with required parameters. 
```bash
$ python ip_notify.py --help
usage: ip_notify.py [-h] [--server SERVER] [--verify-ssl] [--no-verify-ssl]
                    [--admin ADMIN] [--keytab KEYTAB]
                    [--groups GROUPS [GROUPS ...]] [--limit LIMIT]
                    [--noop NOOP]

IPA Notifier

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       ipa server fqdn
  --verify-ssl          verify ipa connection SSL cert (default)
  --no-verify-ssl       do not verify ipa connection SSL cert
  --admin ADMIN         admin user email to notify about locked users
  --keytab KEYTAB       keytab path
  --groups GROUPS [GROUPS ...]
                        list of user groups to check
  --limit LIMIT         number of days before notifying a user
  --noop NOOP           no operation mode. Do not send emails


```