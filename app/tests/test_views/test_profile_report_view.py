from unittest.mock import mock_open, patch

from rest_framework.test import force_authenticate

from app.tests.base import BaseTestCase
from app.tests.mock_objects import (
    MockCeleryAsyncResult, MockOpenFileNotFound, MockObj, MockRequest
)
from app.views.profile.profile_report_view import ProfileReportView

file_path = 'app.views.profile.profile_report_view'


class ProfileReportViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.view = ProfileReportView()
        self.request = MockRequest(method='POST', user=self.profile_1.user)
        force_authenticate(self.request, user=self.profile_1.user)

    def test_dispatch_assigns_task_id(self):
        test_id = 'test-a343-id'
        self.view.dispatch(self.request, task_id=test_id)
        self.assertEqual(test_id, self.view.task_id)

    def test_get_with_task_id_falsey(self):
        resp = self.view.get(self.request)
        self.assertEqual(400, resp.status_code)

    @patch(f'{file_path}.AsyncResult',
           side_effect=MockCeleryAsyncResult.create_not_ready)
    def test_get_with_task_not_ready(self, ar_pch):
        self.view.task_id = '123'
        resp = self.view.get(self.request)
        self.assertEqual(200, resp.status_code)
        self.assertEqual({'status': 'Not ready'}, resp.data)

    @patch(f'{file_path}.open', new_callable=mock_open, read_data='data')
    @patch(f'{file_path}.os.remove')
    @patch(f'{file_path}.AsyncResult',
           side_effect=MockCeleryAsyncResult.create_ready)
    def test_get_with_task_ready(self, ar_pch, os_rm_patch, open_patch):
        self.view.task_id = '123'
        resp = self.view.get(self.request)
        self.assertEqual(200, resp.status_code)
        self.assertEqual('data'.encode(), resp.content)

    @patch(f'{file_path}.open', side_effect=MockOpenFileNotFound)
    @patch(f'{file_path}.AsyncResult',
           side_effect=MockCeleryAsyncResult.create_ready)
    def test_get_with_task_ready_file_not_found(self, ar_pch, open_patch):
        self.view.task_id = '123'
        resp = self.view.get(self.request)
        self.assertEqual(204, resp.status_code)

    def test_post_method_falsey_request_data(self):
        resp = self.view.post(self.request)
        self.assertEqual(400, resp.status_code)

    @patch(f'{file_path}.profile_report_pdf.delay')
    def test_post_method_task_accepted(self, task_patch):
        param_ids, removed_stats = ['2'], ['5']
        task_id = '123'
        task_patch.return_value = MockObj(id=task_id)
        self.request.data = {'param_ids': param_ids,
                             'removed_stats': removed_stats}
        resp = self.view.post(self.request)
        self.assertEqual({'task_id': task_id}, resp.data)
        self.assertEqual(202, resp.status_code)
        task_patch.assert_called_with(
            self.request.user.profile.id, date_str='', param_ids=param_ids,
            removed_stats=removed_stats
        )
