""" Tests for ui_controller """
import unittest
import requests
import ckanext.notify.controllers.ui_controller as controller
from mock import MagicMock, patch, Mock


class TestUIController(unittest.TestCase):
    def setUp(self):
        self._plugins = controller.plugins
        controller.plugins = MagicMock()

        self._toolkit = controller.toolkit
        controller.toolkit = MagicMock()
        controller.toolkit._ = self._toolkit._
        self.controller_instance = controller.DataRequestsNotifyUI()

        self._c = controller.c
        controller.c = MagicMock()

        self._request = controller.request
        controller.request = MagicMock()

        self._model = controller.model
        controller.model = MagicMock()

        self._helpers = controller.helpers
        controller.helpers = MagicMock()

        self._base = controller.base
        controller.base = MagicMock()

        self.expected_context = {
            'model': controller.model,
            'session': controller.model.Session,
            'user': controller.c.user,
            'auth_user_obj': controller.c.userobj
        }

    def tearDown(self):
        controller.plugins = self._plugins
        controller.toolkit = self._toolkit
        controller.c = self._c
        controller.request = self._request
        controller.model = self._model
        controller.request = self._request
        controller.helpers = self._helpers
        controller.base = self._base

    @patch('ckanext.notify.controllers.ui_controller.base.render_jinja2')
    @patch.object(requests, 'post')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action')
    def test_slack_notifications_for_registered_organisations(self, mock_get_action, mock_post, mock_jinja):
        result = dict(organization={'name': 'andela', 'title': 'Andela'}, datarequest_url='http://ckan.andela.com',
                      title='Testing Bunch', description='Issa Testing Bunch')
        template = 'datarequest-create'
        result_dict = [
            dict(webhook_url='https://hooks.slack.com/services/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')]
        mock_get_action.return_value = lambda context, data_dict: result_dict
        mock_post.return_value = {'status_code': 200}
        mock_jinja.return_value = 'hello'
        self.controller_instance.send_slack_notification(template, result)
        mock_post.assert_called_with('https://hooks.slack.com/services/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',
                                     data='{"text": "hello"}', headers={'Content-type': 'application/json'})

    @patch('ckanext.notify.controllers.ui_controller.toolkit.render')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action',
           side_effect=[lambda context, data: 'Andela', lambda context, data: 'data-requests',
                        lambda context, data: 'test@yahoo.com'])
    def test_organization_channels(self, mock_get_action_email, mock_render):
        self.controller_instance.organization_channels('andela')
        mock_render.assert_called_with('notify/channels.html', extra_vars=dict(email_channels='test@yahoo.com',
                                                                               slack_channels='data-requests'))

    @patch('ckanext.notify.controllers.ui_controller.toolkit.render')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action')
    @patch('ckanext.notify.controllers.ui_controller.DataRequestsNotifyUI.post_email_form')
    def test_update_email(self, mock_pef, mock_c, mock_render):
        mock_c.return_value = lambda context, email_data: {}
        required_vars = {'data': {}, 'errors': {}, 'errors_summary': {}, 'new_form': False}
        self.controller_instance.update_email_details(u'f86464e6-ad3f-474c-ad60-c114d711c505', 'andela')
        mock_render.assert_called_with('notify/register_email.html', extra_vars=required_vars)

    @patch('ckanext.notify.controllers.ui_controller.toolkit.render')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action')
    @patch('ckanext.notify.controllers.ui_controller.DataRequestsNotifyUI.post_slack_form')
    def test_update_slack(self, mock_pef, mock_c, mock_render):
        mock_c.return_value = lambda context, slack_data: {}
        required_vars = {'data': {}, 'errors': {}, 'errors_summary': {}, 'new_form': False}
        self.controller_instance.update_slack_details(u'f86464e6-ad3f-474c-ad60-c114d711c505', 'andela')
        mock_render.assert_called_with('notify/register_slack.html', extra_vars=required_vars)

    @patch('ckanext.notify.controllers.ui_controller.toolkit.check_access')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.render')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action')
    @patch('ckanext.notify.controllers.ui_controller.DataRequestsNotifyUI.post_email_form')
    def test_email_form(self, mock_pef, mock_get_action, mock_render, mock_check_access):
        required_vars = {'new_form': True, 'errors': {}, 'data': {'organization_id': 'andela'}, 'errors_summary': {}}
        self.controller_instance.email_form('andela')
        mock_render.assert_called_with('notify/register_email.html', extra_vars=required_vars)

    @patch('ckanext.notify.controllers.ui_controller.toolkit.check_access')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.render')
    @patch('ckanext.notify.controllers.ui_controller.toolkit.get_action')
    @patch('ckanext.notify.controllers.ui_controller.DataRequestsNotifyUI.post_slack_form')
    def test_slack_form(self, mock_pef, mock_get_action, mock_render, mock_check_access):
        required_vars = {'new_form': True, 'errors': {}, 'data': {'organization_id': 'andela'}, 'errors_summary': {}}
        self.controller_instance.slack_form('andela')
        mock_render.assert_called_with('notify/register_slack.html', extra_vars=required_vars)


if __name__ == '__main__':
    unittest.main(verbosity=2)
