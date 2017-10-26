from flask_pluginengine import render_plugin_template
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.modules.events.management.views import WPEventManagement

from notify_contact import NotifyContact


class ECMWFPlugin(IndicoPlugin):
    """ECMWF plugin

    TODO: Explain better what this plugin is about
    """

    def init(self):
        super(ECMWFPlugin, self).init()
        self.template_hook('registration-management-extra-actions', self._notify_contact)
        self.inject_css('ecmwf_css', WPEventManagement)

    def get_blueprints(self):
        blueprint = IndicoPluginBlueprint('ecmwf', __name__, url_prefix='/ecmwf')
        blueprint.add_url_rule(
            '/event/<confId>/manage/registration/<int:reg_form_id>/registrations/notify/contact',
            'notify_contact', NotifyContact, methods=('POST',)
        )
        return blueprint

    def register_assets(self):
        self.register_css_bundle('ecmwf_css', 'css/ecmwf.css')

    def _notify_contact(self, **kwargs):
        regform = kwargs["regform"]
        return render_plugin_template('actions_dropdown_extension.html', regform=regform)
