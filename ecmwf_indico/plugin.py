from flask_pluginengine import render_plugin_template
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.modules.events.management.views import WPEventManagement

from notify_contact import NotifyContact
from visa_invitation import VisaInvitation
from speaker_reimbursement import SpeakerReimbursement


class ECMWFPlugin(IndicoPlugin):
    """ECMWF plugin

    Main features:
    - Notify contact with selected registrations.
    """

    def init(self):
        super(ECMWFPlugin, self).init()
        self.template_hook(
            'registration-status-action-button', self._ecmwf_menu)
        self.template_hook('page-header', self._google_analytics)
        self.template_hook('conference-header',
                           self._event_iframe_detection)
        self.inject_css('ecmwf_css')

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
        return blueprint

    def register_assets(self):
        self.register_css_bundle('ecmwf_css', 'css/ecmwf.css')

    def _ecmwf_menu(self, **kwargs):
        regform = kwargs["regform"]
        return render_plugin_template('actions_dropdown_extension.html', regform=regform)

    def _google_analytics(self, **_kwargs):
        return render_plugin_template('google_analytics.html')

    def _event_iframe_detection(self, **_kwargs):
        """Inject a script into the page that enables/disables the header/footer.
        If the page is displayed inside an iFrame then the header/footer is disabled. 
        """
        return render_plugin_template('event_iframe_detection.html')
