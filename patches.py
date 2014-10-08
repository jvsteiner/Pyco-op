

def my_send_mail(subject, recipient, template, **context):
    """Send an email via the Flask-Mail extension.

    :param subject: Email subject
    :param recipient: Email recipient
    :param template: The name of the email template
    :param context: The context to render the template with
    """
    print "sending mail"

    context.setdefault('security', _security)
    context.update(_security._run_ctx_processor('mail'))

    msg = Message(subject,
                  sender=_security.email_sender,
                  recipients=[recipient])

    ctx = ('security/email', template)
    msg.body = render_template('%s/%s.txt' % ctx, **context)
    msg.html = render_template('%s/%s.html' % ctx, **context)

    if _security._send_mail_task:
        _security._send_mail_task(msg)
        return

    mail = current_app.extensions.get('mail')
    mail.send(msg)

