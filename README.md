### FreeIPA Notification
Notify IPA Users for password expiration and locked users to admin

Required packages:
- krb5-devel

1. Create a new role for notifier
   ```shell
   ipa role-add --desc "Notification agent role" "Notification Agent"
   ```
2. Add privileges to the role
   ```shell
   ipa role-add-privilege "Notification Agent" --privileges="User Administrators"
   ipa role-add-privilege "Notification Agent" --privileges="Group Administrators"
   ipa role-add-privilege "Notification Agent" --privileges="Password Policy Readers"
   ```
3. Create a new service and assign the role to this service
   ```shell
   ipa service-add NOTIFY/ipa1.example.com
   ipa role-add-member  "Notification Agent" --services="NOTIFY/ipa1.example.com@EXAMPLE.COM"
   ipa service-allow-retrieve-keytab "NOTIFY/ipa1.example.com@EXAMPLE.COM" --hosts=ipa1.example.com
   ```
4. Obtain a keytab with fix permissions
   ```shell
   ipa-getkeytab -s ipa1.example.com -p "NOTIFY/ipa1.example.com@EXAMPLE.COM" -k ~/.priv/notify.keytab
   chmod -R 600 ~/.priv
   ```
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