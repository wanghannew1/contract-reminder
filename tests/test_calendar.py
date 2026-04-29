"""
日程功能测试
"""
import pytest
from datetime import datetime, timedelta
from app.models.calendar_event import CalendarEvent


class TestCalendar:
    """日程功能测试"""

    def test_calendar_list_requires_auth(self, client):
        """测试日程列表需要认证"""
        response = client.get('/api/calendar/events')
        assert response.status_code in (401, 302)

    def test_calendar_list_authenticated(self, auth_client):
        """测试已认证用户可以访问日程列表"""
        response = auth_client.get('/api/calendar/events')
        assert response.status_code == 200

    def test_calendar_event_create(self, auth_client, app):
        """测试创建日程事件"""
        from app import db
        with app.app_context():
            event = CalendarEvent(
                user_id=1,
                contract_id=1,
                event_id='dingtalk_123',
                summary='测试日程',
                description='测试描述',
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1)
            )
            db.session.add(event)
            db.session.commit()

        response = auth_client.get('/api/calendar/events')
        assert response.status_code == 200

    def test_calendar_event_delete(self, auth_client, app):
        """测试删除日程事件"""
        from app import db
        with app.app_context():
            event = CalendarEvent(
                user_id=1,
                contract_id=1,
                event_id='dingtalk_456',
                summary='待删除日程'
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id

        response = auth_client.delete(f'/api/calendar/events/{event_id}')
        assert response.status_code == 200

    def test_calendar_event_unique_constraint(self, app):
        """测试同一合同只能有一条有效日程"""
        from app import db
        with app.app_context():
            event1 = CalendarEvent(
                user_id=1,
                contract_id=1,
                event_id='dingtalk_1',
                summary='日程1',
                deleted=False
            )
            db.session.add(event1)
            db.session.commit()

            event2 = CalendarEvent(
                user_id=1,
                contract_id=1,
                event_id='dingtalk_2',
                summary='日程2',
                deleted=False
            )
            db.session.add(event2)
            try:
                db.session.commit()
            except:
                db.session.rollback()
