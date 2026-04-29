"""
钉钉服务测试
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.dingtalk import DingTalkService


class TestDingTalkService:
    """钉钉服务测试"""

    def test_get_access_token_success(self):
        """测试获取access_token成功"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {'accessToken': 'test_token_123', 'expireIn': 7200}
            mock_post.return_value = mock_resp

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            token = service.get_access_token()

            assert token == 'test_token_123'
            mock_post.assert_called_once()

    def test_get_access_token_failure(self):
        """测试获取access_token失败"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            with pytest.raises(Exception):
                service.get_access_token()

    def test_test_connection_success(self):
        """测试连接成功"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {'accessToken': 'valid_token'}
            mock_post.return_value = mock_resp

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            result = service.test_connection()

            assert result['success'] is True

    def test_test_connection_failure(self):
        """测试连接失败"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection refused")

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            result = service.test_connection()

            assert result['success'] is False

    def test_get_userid_by_mobile_success(self):
        """测试通过手机号获取用户ID"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            # First call for token, second call for user API
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {'accessToken': 'test_token'}

            user_resp = MagicMock()
            user_resp.json.return_value = {
                "errcode": 0,
                "errmsg": "ok",
                "result": {
                    "userid": "1855404625945034",
                    "name": "王涵",
                    "unionid": "JblB9ViiEHFuDuJva79ii60QiEiE"
                }
            }
            mock_post.side_effect = [token_resp, user_resp]

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            result = service.get_userid_by_mobile('18843112066')

            assert result['success'] is True
            assert result['userid'] == '1855404625945034'
            assert result['name'] == '王涵'
            assert result['unionid'] == 'JblB9ViiEHFuDuJva79ii60QiEiE'

    def test_get_userid_by_mobile_failure(self):
        """测试通过手机号获取用户ID失败"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {'accessToken': 'test_token'}

            user_resp = MagicMock()
            user_resp.json.return_value = {"errcode": 40014, "errmsg": "invalid mobile"}
            mock_post.side_effect = [token_resp, user_resp]

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            result = service.get_userid_by_mobile('invalid')

            assert result['success'] is False

    def test_create_calendar_event_success(self):
        """测试创建日程成功"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            # Token request
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {'accessToken': 'test_token'}
            # Event request
            event_resp = MagicMock()
            event_resp.status_code = 200
            event_resp.json.return_value = {'id': 'event_123'}
            mock_post.side_effect = [token_resp, event_resp]

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            from datetime import timedelta
            result = service.create_calendar_event(
                union_id='union_123',
                summary='合同到期提醒：张三',
                description='测试描述',
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1)
            )

            assert result['success'] is True
            assert result['event_id'] == 'event_123'

    def test_create_calendar_event_with_recurrence(self):
        """测试创建重复日程"""
        with patch('app.services.dingtalk.requests.post') as mock_post:
            token_resp = MagicMock()
            token_resp.status_code = 200
            token_resp.json.return_value = {'accessToken': 'test_token'}
            event_resp = MagicMock()
            event_resp.status_code = 200
            event_resp.json.return_value = {'id': 'event_456'}
            mock_post.side_effect = [token_resp, event_resp]

            service = DingTalkService(app_key='test_key', app_secret='test_secret')
            rrule = service.generate_rrule('weekly', 1, datetime(2026, 12, 31), 'thursday')
            from datetime import timedelta
            result = service.create_calendar_event(
                union_id='union_123',
                summary='合同到期提醒',
                description='测试',
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                recurrence_rrule=rrule
            )

            assert result['success'] is True
            # 验证RRULE格式正确
            assert rrule == "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20261231"

    def test_cancel_calendar_event_success(self):
        """测试取消日程成功"""
        with patch('app.services.dingtalk.requests.delete') as mock_delete:
            with patch('app.services.dingtalk.requests.post') as mock_post:
                # Token request
                token_resp = MagicMock()
                token_resp.status_code = 200
                token_resp.json.return_value = {'accessToken': 'test_token'}
                mock_post.return_value = token_resp
                # Delete request
                mock_delete.return_value = MagicMock(status_code=200, json=lambda: {})

                service = DingTalkService(app_key='test_key', app_secret='test_secret')
                result = service.cancel_calendar_event('union_123', 'event_456')

                assert result['success'] is True

    def test_delete_calendar_event_success(self):
        """测试删除日程成功"""
        with patch('app.services.dingtalk.requests.delete') as mock_delete:
            with patch('app.services.dingtalk.requests.post') as mock_post:
                token_resp = MagicMock()
                token_resp.status_code = 200
                token_resp.json.return_value = {'accessToken': 'test_token'}
                mock_post.return_value = token_resp
                mock_delete.return_value = MagicMock(status_code=200, json=lambda: {})

                service = DingTalkService(app_key='test_key', app_secret='test_secret')
                result = service.delete_calendar_event('union_123', 'event_456')

                assert result['success'] is True

    def test_generate_rrule_weekly(self):
        """测试生成每周重复规则"""
        rule = DingTalkService.generate_rrule(
            frequency='weekly',
            interval=1,
            until=datetime(2026, 12, 31),
            by_day='thursday'
        )

        assert rule == "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20261231"

    def test_generate_rrule_daily(self):
        """测试生成每日重复规则"""
        rule = DingTalkService.generate_rrule(
            frequency='daily',
            interval=1,
            until=datetime(2026, 12, 31)
        )

        assert rule == "RRULE:FREQ=DAILY;INTERVAL=1;UNTIL=20261231"

    def test_list_calendar_events_success(self):
        """测试列出日程"""
        with patch('app.services.dingtalk.requests.get') as mock_get:
            with patch('app.services.dingtalk.requests.post') as mock_post:
                token_resp = MagicMock()
                token_resp.status_code = 200
                token_resp.json.return_value = {'accessToken': 'test_token'}
                mock_post.return_value = token_resp

                mock_get.return_value = MagicMock(
                    status_code=200,
                    json=lambda: {
                        "events": [
                            {"id": "event1", "summary": "日程1"},
                            {"id": "event2", "summary": "日程2"}
                        ]
                    }
                )

                service = DingTalkService(app_key='test_key', app_secret='test_secret')
                result = service.list_calendar_events(
                    union_id='union_123',
                    time_min=datetime(2026, 1, 1),
                    time_max=datetime(2026, 12, 31)
                )

                assert result['success'] is True
                assert len(result['events']) == 2
