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


class SpeakerReimbursementForm(IndicoForm):
    from_address = SelectField(_("From"), [DataRequired()])
    cc_addresses = EmailListField(_("CC"),
                                  description=_("Beware, addresses in this field will receive one mail per "
                                                "registrant."))
    subject = StringField(_("Subject"), [DataRequired()])
    body = TextAreaField(
        _("Email body"), [DataRequired()], widget=CKEditorWidget(simple=True))
    recipients = IndicoEmailRecipientsField(_('Recipients'))
    copy_for_sender = BooleanField(_('Send copy to me'), widget=SwitchWidget(),
                                   description=_('Send copy of each email to my mailbox'))
    registration_id = HiddenFieldList()
    submitted = HiddenField()

    def __init__(self, *args, **kwargs):
        self.regform = kwargs.pop('regform')
        event = self.regform.event
        super(SpeakerReimbursementForm, self).__init__(*args, **kwargs)
        self.from_address.choices = event.get_allowed_sender_emails().items()
        # Submitted forms have the body set and it should not be replaced with a template
        if not self.body.data:
            self.body.data = render_plugin_template(
                'speaker_reimbursement_form_text.html')
        self.body.description = render_placeholder_info(
            'registration-email', regform=self.regform, registration=None)

    def validate_body(self, field):
        missing = get_missing_placeholders(
            'registration-email', field.data, regform=self.regform, registration=None)
        if missing:
            raise ValidationError(
                _('Missing placeholders: {}').format(', '.join(missing)))

    def is_submitted(self):
        return super(SpeakerReimbursementForm, self).is_submitted() and 'submitted' in request.form


class SpeakerReimbursementPDF(object):
    def __init__(self, event, registration_id):
        self.registration = (Registration.query.with_parent(event)
                             .filter(Registration.id == registration_id)
                             .options(subqueryload('data').joinedload('field_data'))
                             .one())
        self.data = {}

        # Get data from registration form
        for _field in self.registration.data:
            field_name = _field.field_data.field.html_field_name
            value = _field.field_data.field.get_friendly_data(
                _field, for_humans=False)
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
        self.data['event_address'] = self.registration.event.address.replace(
            '\n', ', ')
        self.data['event_start_date'] = self.registration.event.start_dt_display.strftime(
            "%d %B %Y")
        self.data['event_end_date'] = self.registration.event.end_dt_display.strftime(
            "%d %B %Y")

    def get_pdf(self):
        data = BytesIO()
        canvas = Canvas(data, pagesize=A4)
        self._build_pdf(canvas)
        canvas.save()
        data.seek(0)
        return data

    def _build_pdf(self, canvas):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        width, height = A4
        # Logo
        canvas.translate(0, 28.5*cm)
        canvas.drawImage("%s/static/img/ecmwf_logo.png" %
                         dir_path, 1*cm, -2*cm, width=19*cm, height=2.47*cm)
        # Body
        stylesheet = getSampleStyleSheet()
        normalStyle = stylesheet['Normal']
        body_data = """
        <b>%s</b>
        <b>From %s To %s</b>

        <b>Information for invited speakers</b>
        
        ECMWF will contribute  to your travel expenses up to the amount stated in the invitation email. You need to make your own travel arrangements; costs are reimbursed after the event.

        <b>You will receive a claim form</b> which you need to complete and submit together with receipts. You will need to provide flight booking confirmation, boarding passes, hotel invoice and receipts for taxi/train/bus fares . Please submit your claim as soon as possible after the event; you can email it or send it in the post.

        <b>Your expenses will be reimbursed as follows (total up to maximum contribution):</b>

        Air fare: Economy return travel
        Subsistence allowance: Consistent with date/time of workshop (100%% on receipt of hotel invoice; 50%% if staying with family or friends)
        Local travel costs: Taxi/train/bus fares as appropriate

        If receipts for costs claimed are not provided, then ECMWF is unable to reimburse these costs.

        <b>Expenses will be paid into your nominated bank account.</b> Please ensure that you have provided your bank details on the reverse of the claim form; including full postal address and account number as well as sort/swift/IBAN code (as applicable). ECWMF is unable to pay cash advances or reimburse expenses in cash.
        
        Remember to sign and date your travel claim.

        <b>It is possible for your institution to invoice ECMWF for the contribution to your travel expenses.</b> In this case ECMWF will settle the invoice up to the maximum contribution and the invoice should include receipts as mentioned above.  
        
        <b>Should you have any questions, please contact:</b>

        Regina Mansor
        Email: regina.mansor@ecmwf.int
        Telephone: +44 (0)118 949 9734

        <b>Claims to be sent to:</b>
        ECMWF
        Regina Mansor
        Administration Department
        Shinfield Park
        Reading RG2 9AX
        Berkshire
        Great Britain



        <font size=8><i>Shinfield Park, Shinfield Road, Reading, RG2 9AX, UK
        t: +44 (0)118 949 9000 | f: +44 (0)118 986 9450 | w: www.ecmwf.int</i></font>
        """ % (self.data['event_title'], self.data['event_start_date'], self.data['event_end_date'])
        body_data = body_data.replace("\n", "<br/>")
        body = Paragraph(body_data, normalStyle)
        body.wrap(540, 700)
        body.drawOn(canvas, 1*cm, -24*cm)


class SpeakerReimbursement(RHRegistrationsActionBase):
    NOT_SANITIZED_FIELDS = {'from_address'}

    def generate_reimbursement_pdf(self, registration):
        pdf = SpeakerReimbursementPDF(registration.event, registration.id)
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
            attachments = [('Reimbursement Information.pdf', self.generate_reimbursement_pdf(
                registration).getvalue())]
            email = make_email(to_list=registration.email, cc_list=form.cc_addresses.data, bcc_list=bcc,
                               from_address=form.from_address.data, template=template, html=True,
                               attachments=attachments)
            send_email(email, self.event, 'Registration')

    def _process(self):
        tpl = get_template_module(
            'events/registration/emails/custom_email_default.html')
        default_body = tpl.get_html_body()
        registration_ids = request.form.getlist('registration_id')
        form = SpeakerReimbursementForm(body=default_body, regform=self.regform, registration_id=registration_ids,
                                        recipients=[x.email for x in self.registrations])
        if form.validate_on_submit():
            self._send_emails(form)
            num_emails_sent = len(self.registrations)
            if num_emails_sent > 1:
                flash('%d emails were sent.' % (num_emails_sent), 'success')
            else:
                flash('The email was sent.', 'success')
            return jsonify_data()
        return jsonify_template('speaker_reimbursement_form.html',
                                _render_func=render_plugin_template,
                                form=form, regform=self.regform)
