from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint

class ECMWFPlugin(IndicoPlugin):
    """ECMWF plugin

    TODO: Explain better what this plugin is about
    """

    def init(self):
        super(ECMWFPlugin, self).init()
        self.template_hook('additional-content', self._show_hide_clippy)
        self.connect(signals.event.updated, self._event_changed)
        self.inject_css('clippy_css', WPEventManagement)
        self.inject_js('clippy_js', WPEventManagement)

    def get_blueprints(self):
        return IndicoPluginBlueprint(self.name, __name__)

    def register_assets(self):
        self.register_css_bundle('clippy_css', 'css/clippy.css')
        self.register_js_bundle('clippy_js', 'js/clippy.js', 'js/indico_clippy.js')

    def _event_changed(self, event, changes, **kwargs):
        if 'title' not in changes:
            return
        old_title = changes['title'][0]
        new_title = changes['title'][1]
        template = get_template_module('clippy:clippy_mail.html', old_title=old_title, new_title=new_title)
        email = make_email(to_list=event.all_manager_emails, from_address='clippy@exam.ple',
                           template=template, html=True)
        send_email(email)

    def _show_hide_clippy(self):
        return render_plugin_template('hide_clippy.html')