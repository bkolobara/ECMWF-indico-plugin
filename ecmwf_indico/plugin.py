from flask_pluginengine import render_plugin_template
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from notify_contact import NotifyContact


class ECMWFPlugin(IndicoPlugin):
    """ECMWF plugin

    TODO: Explain better what this plugin is about
    """

    def init(self):
        super(ECMWFPlugin, self).init()
        self.template_hook('registration-management-extra-actions', self._notify_contact)
        # self.connect(signals.event.updated, self._event_changed)
        # self.inject_css('clippy_css', WPEventManagement)
        # self.inject_js('clippy_js', WPEventManagement)

    def get_blueprints(self):
        blueprint = IndicoPluginBlueprint('ecmwf', __name__, url_prefix='/ecmwf')
        blueprint.add_url_rule(
            '/event/<confId>/manage/registration/<int:reg_form_id>/registrations/notify/contact',
            'notify_contact', NotifyContact, methods=('POST',)
        )
        return blueprint

    def register_assets(self):
        pass
        # self.register_css_bundle('clippy_css', 'css/clippy.css')
        # self.register_js_bundle('clippy_js', 'js/clippy.js', 'js/indico_clippy.js')

    def _notify_contact(self, **kwargs):
        regform = kwargs["regform"]
        return render_plugin_template('actions_dropdown_extension.html', regform=regform)
