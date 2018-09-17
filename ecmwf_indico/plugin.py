from flask_pluginengine import render_plugin_template
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.modules.events.management.views import WPEventManagement

from notify_contact import NotifyContact
from visa_invitation import VisaInvitation
from speaker_reimbursement import SpeakerReimbursement
from ecmwf_abstracts import ECMWFAbstracts


class ECMWFPlugin(IndicoPlugin):
    """ECMWF plugin

    Main features:
    - Notify contact with selected registrations.
    """

    def init(self):
        super(ECMWFPlugin, self).init()
        self.template_hook(
            'registration-status-action-button', self._ecmwf_menu)
        self.inject_css('ecmwf_css')
        self.inject_js('linkify_js')
        self.inject_js('ecmwf_js')

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

    def register_assets(self):
        self.register_css_bundle('ecmwf_css', 'css/ecmwf.css')
        self.register_js_bundle('linkify_js', 'js/linkify.min.js', 'js/linkify-jquery.min.js')
        self.register_js_bundle('ecmwf_js', 'js/ecmwf.js')

    def _ecmwf_menu(self, **kwargs):
        regform = kwargs["regform"]
        return render_plugin_template('actions_dropdown_extension.html', regform=regform)