from flask import request, flash
from flask_pluginengine import render_plugin_template

from wtforms.fields import HiddenField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError

from indico.core.notifications import make_email, send_email
from indico.web.flask.templating import get_template_module
from indico.web.util import jsonify_data, jsonify_template
from indico.web.forms.fields import EmailListField
from indico.web.forms.widgets import CKEditorWidget
from indico.web.forms.base import IndicoForm
from indico.util.i18n import _
from indico.util.placeholders import replace_placeholders, get_missing_placeholders
from indico.modules.events.registration.controllers.management.reglists import RHRegistrationsActionBase


class NotifyContactForm(IndicoForm):
    from_address = SelectField(_("From"), [DataRequired()])
    to_address = EmailField(_("To"), [DataRequired()])
    cc_addresses = EmailListField(_("CC"))
    subject = StringField(_("Subject"), [DataRequired()])
    body = TextAreaField(_("Email body"), [DataRequired()],
                         widget=CKEditorWidget(simple=True, height="430"))
    submitted = HiddenField()

    def __init__(self, *args, **kwargs):
        super(NotifyContactForm, self).__init__(*args, **kwargs)
        self.regform = kwargs.pop('regform')
        registrations = kwargs.pop('registrations')

        self.from_address.choices = self.regform.event.get_allowed_sender_emails().items()
        self.body.data = render_plugin_template('notify_contact_form_text.html',
                                                registrations=registrations)
        self.body.description = """<b>Available placeholders</b><br/>
        {event_link}: Link to the event<br/>
        {event_title}: The title of the event<br/>
        {link}: The link to the registration details
        """

    def validate_body(self, field):
        missing = get_missing_placeholders('registration-email', field.data,
                                           regform=self.regform, registration=None)
        if missing:
            raise ValidationError(_('Missing placeholders: {}').format(', '.join(missing)))

    def is_submitted(self):
        return super(NotifyContactForm, self).is_submitted() and 'submitted' in request.form


class NotifyContact(RHRegistrationsActionBase):
    """Previews the email that will be sent to country contacts"""

    def _send_emails(self, form):
        email_body = replace_placeholders('registration-email', form.body.data,
                                          regform=self.regform, registration=None)
        template = get_template_module('events/registration/emails/custom_email.html',
                                        email_subject=form.subject.data, email_body=email_body)
        email = make_email(to_list=form.to_address.data, cc_list=form.cc_addresses.data,
                           from_address=form.from_address.data, template=template, html=True)
        send_email(email, self.event, 'NotifyContact')

    def _process(self):
        form = NotifyContactForm(regform=self.regform, registrations=self.registrations)
        if form.validate_on_submit():
            self._send_emails(form)
            flash(_('The email was sent.'), 'success')
            return jsonify_data()
        return jsonify_template('notify_contact_form.html',
                                _render_func=render_plugin_template,
                                form=form, regform=self.regform)
