### FreeIPA Notification
[![Upload Python Package](https://github.com/cagdasbas/ipa-notify/actions/workflows/python-publish.yml/badge.svg)](https://github.com/cagdasbas/ipa-notify/actions/workflows/python-publish.yml)

Notify IPA Users for password expiration and locked users to admin

Required packages:
- krb5-devel
- python3-pip
- python3-virtualenv (Optional)

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
5. (Optional) Create a new virtual env and activate it
   ```shell
   mkdir /opt/ipa-notify
   virtualenv -p python3 /opt/ipa-notify/venv
   source /opt/ipa-notify/venv/bin/activate
	```

6. Install this package:
   ```shell
   pip3 install ipa-notify
   ```
7. Run the command in ```noop``` mode for a successful user listing
   ```shell
   /opt/ipa-notify/bin/ipa-notify --server ipa1.example.com -p "NOTIFY/ipa1.example.com@EXAMPLE.COM" -k ~/.priv/notify.keytab \
   --limit 10 --groups users --check-expiration --noop
   ```

8. Create a script includes the command with your parameters with proper permissions under ```/usr/local/sbin/```
9. Add a crontab entry. For example ```0 0 *  *  * root /usr/local/sbin/ipa_notify.sh &>> /var/log/ipa_notify.log```
10. (Optional) You can create an email template folder and overwrite the message content. You can change the content but
    do not change file names or variable names. Template should start with `Subject:` keyword and there has to be new
    line between the subject and body. Please test your template before using.

```shell
$ python3 -c 'import ipa_notify;print(ipa_notify.__file__)'
/usr/local/lib/python3.6/site-packages/ipa_notify/__init__.py
$ cp -r /usr/local/lib/python3.6/site-packages/ipa_notify/templates ./mytemplates
# edit the content
$ ipa-notify ... --templates ./mytemplates
```

#### Parameters:

```bash
$ ipa-notify --help
usage: ipa-notify [-h] [--server SERVER] [--verify-ssl] [--no-verify-ssl] [--principal PRINCIPAL] [--keytab KEYTAB] [--groups GROUPS [GROUPS ...]] [--limit LIMIT] [--smtp-host SMTP_HOST] [--smtp-port SMTP_PORT]
                  [--smtp-security {none,STARTTLS,SSL}] [--smtp-user SMTP_USER] [--smtp-pass SMTP_PASS] [--smtp-from SMTP_FROM] [--admins ADMINS [ADMINS ...]] [--noop] [--check-expiration] [--check-locked] [--templates TEMPLATES]
                  [--log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]

IPA Notifier

optional arguments:
  -h, --help            show this help message and exit
  --server SERVER       ipa server fqdn (default: ipa.domain.com)
  --verify-ssl          verify ipa connection SSL cert (default) (default: True)
  --no-verify-ssl       do not verify ipa connection SSL cert (default: True)
  --principal PRINCIPAL
                        user principal for kerberos authentication (default: admin@DOMAIN.COM)
  --keytab KEYTAB       keytab path (default: /tmp/user.kt)
  --groups GROUPS [GROUPS ...]
                        list of user groups to check (default: ['users'])
  --limit LIMIT         number of days before notifying a user (default: 5)
  --smtp-host SMTP_HOST
                        smtp host for sending email (default: localhost)
  --smtp-port SMTP_PORT
                        smtp port for sending email (default: 25)
  --smtp-security {none,STARTTLS,SSL}
                        smtp port for sending email (default: none)
  --smtp-user SMTP_USER
                        smtp user login (default: )
  --smtp-pass SMTP_PASS
                        smtp user password (default: )
  --smtp-from SMTP_FROM
                        smtp from email address (default: noreply@domain.com)
  --admins ADMINS [ADMINS ...]
                        admin user(s) email(s) to notify about locked users (default: admin@domain.com)
  --noop                no operation mode. Do not send emails (default: False)
  --check-expiration    Check password expirations for users (default: False)
  --check-locked        Check locked out users (default: False)
  --templates TEMPLATES
                        Custom email template folder (default: )
  --log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
                        log level (default: INFO)
```
