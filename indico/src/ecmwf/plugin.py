import os

from flask_pluginengine import render_plugin_template
from indico.core import signals
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.modules.events.management.views import WPEventManagement

from notify_contact import NotifyContact
from visa_invitation import VisaInvitation
from speaker_reimbursement import SpeakerReimbursement
from ecmwf_abstracts import ECMWFAbstracts


class ECMWFPlugin(IndicoPlugin):

    def init(self):
        super(ECMWFPlugin, self).init()

        # Override Indico pages with custom ECMWF html
        self.connect(signals.plugin.get_template_customization_paths, self._override_templates)

        # Inject ECMWF specific html into <head> (Open Sans, Fontawesome & Favicon)
        self.template_hook('html-head', self._ecmwf_head)

        # Add ECMWF button to performa a set of actions into the registrations page
        self.template_hook('registration-status-action-button', self._ecmwf_registrations_menu)
        # Inject main css
        self.inject_bundle('main.css')
        # Inject main js
        self.inject_bundle('main.js')

    def get_blueprints(self):
        blueprint = IndicoPluginBlueprint(
            'ecmwf', __name__, url_prefix='/ecmwf')
        blueprint.add_url_rule(
            '/event/<confId>/manage/registration/<int:reg_form_id>/registrations/notify-contact',
            'notify_contact', NotifyContact, methods=('POST',)
        )
        blueprint.add_url_rule(
            '/event/<confId>/manage/registration/<int:reg_form_id>/registrations/send-visa-invitation',
            'visa_invitation', VisaInvitation, methods=('POST',)
        )
        blueprint.add_url_rule(
            '/event/<confId>/manage/registration/<int:reg_form_id>/registrations/send-keynote-speaker-reimbursement',
            'speaker_reimbursement', SpeakerReimbursement, methods=('POST',)
        )
        blueprint.add_url_rule(
            '/event/<confId>/abstracts',
            'ecmwf_abstracts', ECMWFAbstracts
        )
        return blueprint

    def _override_templates(self, sender, **kwargs):
        return os.path.join(self.root_path, 'indico_template_overrides')

    def _ecmwf_head(self, **kwargs):
        return render_plugin_template('head.html')

    def _ecmwf_registrations_menu(self, **kwargs):
        regform = kwargs["regform"]
        return render_plugin_template('actions_dropdown_extension.html', regform=regform)

