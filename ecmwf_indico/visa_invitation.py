import os
import datetime

from flask import request, flash, session
from flask_pluginengine import render_plugin_template
from sqlalchemy.orm import subqueryload

from wtforms.fields import BooleanField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError

from indico.core.notifications import make_email, send_email
from indico.web.flask.templating import get_template_module
from indico.web.util import jsonify_data, jsonify_template
from indico.web.forms.fields import EmailListField
from indico.web.forms.fields.simple import HiddenFieldList, IndicoEmailRecipientsField
from indico.web.forms.widgets import CKEditorWidget, SwitchWidget
from indico.web.forms.base import IndicoForm
from indico.util.i18n import _
from indico.util.placeholders import get_missing_placeholders, render_placeholder_info, replace_placeholders
from indico.modules.events.registration.models.registrations import Registration
from indico.modules.events.registration.controllers.management.reglists import RHRegistrationsActionBase
from indico.modules.designer.pdf import DesignerPDFBase

from io import BytesIO
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


class VisaInvitationForm(IndicoForm):
    from_address = SelectField(_("From"), [DataRequired()])
    cc_addresses = EmailListField(_("CC"),
                                  description=_("Beware, addresses in this field will receive one mail per "
                                                "registrant."))
    subject = StringField(_("Subject"), [DataRequired()])
    body = TextAreaField(_("Email body"), [DataRequired()], widget=CKEditorWidget(simple=True))
    recipients = IndicoEmailRecipientsField(_('Recipients'))
    copy_for_sender = BooleanField(_('Send copy to me'), widget=SwitchWidget(),
                                   description=_('Send copy of each email to my mailbox'))
    registration_id = HiddenFieldList()
    submitted = HiddenField()

    def __init__(self, *args, **kwargs):
        self.regform = kwargs.pop('regform')
        event = self.regform.event
        super(VisaInvitationForm, self).__init__(*args, **kwargs)
        self.from_address.choices = event.get_allowed_sender_emails().items()
        self.body.description = render_placeholder_info('registration-email', regform=self.regform, registration=None)

    def validate_body(self, field):
        missing = get_missing_placeholders('registration-email', field.data, regform=self.regform, registration=None)
        if missing:
            raise ValidationError(_('Missing placeholders: {}').format(', '.join(missing)))

    def is_submitted(self):
        return super(VisaInvitationForm, self).is_submitted() and 'submitted' in request.form


class VisaInvitationPDF(object):
    def __init__(self, event, registration_id):
        self.registration = (Registration.query.with_parent(event)
                              .filter(Registration.id == registration_id)
                              .options(subqueryload('data').joinedload('field_data'))
                              .one())
        self.data = {}

        # Get data from registration form
        for _field in self.registration.data:
            field_name = _field.field_data.field.html_field_name
            value = _field.field_data.field.get_friendly_data(_field, for_humans=False)
            self.data[field_name] = value        
        # Assure this fields exist for the template
        if not 'title' in self.data:
            self.data['title'] = ''
        if not 'first_name' in self.data:
            self.data['first_name'] = ''
        if not 'last_name' in self.data:
            self.data['last_name'] = ''
        if not 'affiliation' in self.data:
            self.data['affiliation'] = ''
        if not 'address' in self.data:
            self.data['address'] = ''
        if not 'country' in self.data:
            self.data['country'] = ''

        # Get data from event
        self.data['event_title'] = self.registration.event.title
        self.data['event_address'] = self.registration.event.address.replace('\n', ', ')
        self.data['event_start_date'] = self.registration.event.start_dt_display.strftime("%d %B %Y")
        self.data['event_end_date'] = self.registration.event.end_dt_display.strftime("%d %B %Y")

    def get_pdf(self):
        data = BytesIO()
        canvas = Canvas(data, pagesize=A4)
        self._build_pdf(canvas)
        canvas.save()
        data.seek(0)
        return data

    def _build_pdf(self, canvas):
        width, height = A4
        canvas.translate(0, 29*cm)
        # Header
        canvas.drawString(1*cm, -1*cm, datetime.date.today().strftime("%d %B %Y"))
        canvas.drawRightString(20*cm, -1*cm, "karen.clarke@ecmwf.int")
        # Contact information
        stylesheet=getSampleStyleSheet()
        normalStyle = stylesheet['Normal']
        contact_data = "%s %s %s\n%s\n%s\n%s" % (
            self.data['title'], self.data['first_name'], self.data['last_name'],
            self.data['affiliation'], self.data['address'], self.data['country'])
        contact_data = contact_data.replace("\n","<br/>")
        contact = Paragraph(contact_data, normalStyle)
        contact.wrap(350, 400)
        contact.drawOn(canvas, 1*cm, -4*cm)
        # Body
        dir_path = os.path.dirname(os.path.realpath(__file__))
        body_data = """
        Dear %s %s

        You are cordially invited to attend the event <b>"%s"</b> which is being held in %s, from %s to %s.

        We look forward to your participation in the event.

        Yours sincerely

        <img src="%s/static/img/signature.png" valign="middle" width="100" height="30"/>

        Karen Clarke
        Events Manager
        """ % (self.data['title'], self.data['last_name'],
               self.data['event_title'], self.data['event_address'],
               self.data['event_start_date'], self.data['event_end_date'],
               dir_path)
        body_data = body_data.replace("\n","<br/>")
        body = Paragraph(body_data, normalStyle)
        body.wrap(500, 600)
        body.drawOn(canvas, 1*cm, -12*cm)


class VisaInvitation(RHRegistrationsActionBase):
    NOT_SANITIZED_FIELDS = {'from_address'}

    def generate_visa_invitation_pdf(self, registration):
        pdf = VisaInvitationPDF(registration.event, registration.id)
        return pdf.get_pdf()

    def _send_emails(self, form):
        for registration in self.registrations:
            email_body = replace_placeholders('registration-email', form.body.data, regform=self.regform,
                                              registration=registration)
            email_subject = replace_placeholders('registration-email', form.subject.data, regform=self.regform,
                                                 registration=registration)
            template = get_template_module('events/registration/emails/custom_email.html',
                                           email_subject=email_subject, email_body=email_body)
            bcc = [session.user.email] if form.copy_for_sender.data else []
            attachments = [('Visa invitation.pdf', self.generate_visa_invitation_pdf(registration).getvalue())]
            email = make_email(to_list=registration.email, cc_list=form.cc_addresses.data, bcc_list=bcc,
                               from_address=form.from_address.data, template=template, html=True,
                               attachments=attachments)
            send_email(email, self.event, 'Registration')

    def _process(self):
        tpl = get_template_module('events/registration/emails/custom_email_default.html')
        default_body = tpl.get_html_body()
        registration_ids = request.form.getlist('registration_id')
        form = VisaInvitationForm(body=default_body, regform=self.regform, registration_id=registration_ids,
                                  recipients=[x.email for x in self.registrations])
        if form.validate_on_submit():
            self._send_emails(form)
            num_emails_sent = len(self.registrations)
            if num_emails_sent > 1:
                flash('%d emails were sent.' % (num_emails_sent), 'success')
            else:
                flash('The email was sent.', 'success')
            return jsonify_data()
        return jsonify_template('send_visa_invite_form.html',
                                _render_func=render_plugin_template,
                                form=form, regform=self.regform)
