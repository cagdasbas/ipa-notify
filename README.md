### FreeIPA Notification
Notify IPA Users for password expiration and locked users to admin
1. Obtain a keytab with ```ipa-getkeytab```
2. Run the command in ```noop``` mode for a successful user listing
3. Create a script with proper permissions under ```/usr/local/sbin/```
4. Add a crontab entry. For example ```0 0 *  *  * root ipa_notify.sh > /var/log/ipa_notify.log```


#### Parameters:
```bash
$ ipa-notify --help
usage: ipa_notify.py [-h] [--server SERVER] [--verify-ssl] [--no-verify-ssl] [--principal PRINCIPAL] [--keytab KEYTAB] [--groups GROUPS [GROUPS ...]] [--limit LIMIT] [--smtp-host SMTP_HOST] [--smtp-port SMTP_PORT]
                     [--smtp-user SMTP_USER] [--smtp-pass SMTP_PASS] [--smtp-from SMTP_FROM] [--admin ADMIN] [--noop NOOP] [--loglevel {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]

IPA Notifier

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       ipa server fqdn
  --verify-ssl          verify ipa connection SSL cert (default)
  --no-verify-ssl       do not verify ipa connection SSL cert
  --principal PRINCIPAL
                        user principal for kerberos authentication
  --keytab KEYTAB       keytab path
  --groups GROUPS [GROUPS ...]
                        list of user groups to check
  --limit LIMIT         number of days before notifying a user
  --smtp-host SMTP_HOST
                        smtp host for sending email
  --smtp-port SMTP_PORT
                        smtp port for sending email
  --smtp-user SMTP_USER
                        smtp user login
  --smtp-pass SMTP_PASS
                        smtp user password
  --smtp-from SMTP_FROM
                        smtp from email address
  --admin ADMIN         admin user email to notify about locked users
  --noop NOOP           no operation mode. Do not send emails
  --loglevel {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
                        log level

```