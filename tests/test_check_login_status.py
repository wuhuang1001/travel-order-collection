import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
import json
from service.login_service import check_login_status


class TestCheckLoginStatus:

    def test_valid_token_returns_true(self):
        """errno=0 时返回 True"""
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"errno": 0, "errmsg": "ok"})

        with patch('service.login_service.send_get_request', return_value=mock_resp):
            result = check_login_status("valid_token", "13800138000", "omgid", "wsgsig")
            assert result is True

    def test_invalid_token_returns_false(self):
        """errno=1 (需重新登录) 时返回 False"""
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"errno": 1, "errmsg": "请您重新登录再试一次！"})

        with patch('service.login_service.send_get_request', return_value=mock_resp):
            result = check_login_status("expired_token", "13800138000", "omgid", "wsgsig")
            assert result is False

    def test_json_decode_error_returns_false(self):
        """响应非合法 JSON 时返回 False"""
        mock_resp = MagicMock()
        mock_resp.text = "<html>nginx error</html>"

        with patch('service.login_service.send_get_request', return_value=mock_resp):
            result = check_login_status("any_token", "13800138000", "omgid", "wsgsig")
            assert result is False

    def test_request_params_include_token(self):
        """验证请求参数中包含 token 和 phone"""
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({"errno": 0})

        with patch('service.login_service.send_get_request') as mock_send:
            mock_send.return_value = mock_resp
            check_login_status("my_token", "13900001111", "omgid_123", "wsgsig_456")

            args = mock_send.call_args
            params = args[0][2]  # 第三个位置参数是 params dict
            assert params['token'] == 'my_token'
            assert params['phone'] == '13900001111'
            assert params['omgid'] == 'omgid_123'
            assert params['wsgsig'] == 'wsgsig_456'
            assert params['pagenum'] == 0
            assert params['timemode'] == '202001'
