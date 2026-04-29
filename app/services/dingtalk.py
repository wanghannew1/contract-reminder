"""
钉钉API服务
"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.models.system_config import SystemConfig


class DingTalkService:
    """钉钉开放平台API封装"""

    BASE_URL = "https://api.dingtalk.com"
    API_BASE_URL = "https://api.dingtalk.com/v1.0"
    OAUTH_URL = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    USER_API_URL = "https://oapi.dingtalk.com/topapi/v2/user"

    def __init__(self, app_key: str = None, app_secret: str = None):
        self.app_key = app_key or SystemConfig.get_value('dingtalk_appkey', '')
        self.app_secret = app_secret or SystemConfig.get_value('dingtalk_appsecret', '')
        self._access_token = None
        self._token_expires_at = None

    def get_access_token(self) -> str:
        """获取access_token（带缓存）"""
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        url = self.OAUTH_URL
        payload = {
            "appKey": self.app_key,
            "appSecret": self.app_secret
        }
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data['accessToken']
        # 钉钉token有效期2小时，提前5分钟过期
        self._token_expires_at = datetime.now() + timedelta(hours=2, minutes=-5)
        return self._access_token

    def _headers(self) -> Dict[str, str]:
        """请求头（带token）"""
        return {
            "x-acs-dingtalk-access-token": self.get_access_token(),
            "Content-Type": "application/json"
        }

    def test_connection(self) -> Dict[str, Any]:
        """测试钉钉连接"""
        try:
            token = self.get_access_token()
            return {"success": True, "message": "连接成功", "access_token": token[:10] + "..."}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}

    def get_userid_by_mobile(self, mobile: str) -> Dict[str, Any]:
        """
        通过手机号获取用户ID（包括unionid）

        Args:
            mobile: 手机号

        Returns:
            {"success": True, "userid": "xxx", "name": "xxx", "unionid": "xxx"}
            或 {"success": False, "error": "xxx"}
        """
        url = f"{self.USER_API_URL}/getbymobile"
        params = {"access_token": self.get_access_token()}
        payload = {"mobile": mobile}

        try:
            resp = requests.post(url, params=params, json=payload, timeout=10)
            data = resp.json()
            if data.get("errcode") == 0:
                result = data["result"]
                userid = result.get("userid", "")
                # unionid可能为空，需要通过userid再获取
                unionid = result.get("unionid", "")
                name = result.get("name", "")

                # 如果unionid为空，通过userid获取完整信息
                if not unionid and userid:
                    user_info = self.get_user_by_userid(userid)
                    if user_info.get("success"):
                        unionid = user_info.get("unionid", "")
                        name = user_info.get("name", name)

                return {
                    "success": True,
                    "userid": userid,
                    "name": name,
                    "unionid": unionid
                }
            else:
                return {"success": False, "error": data.get("errmsg", "获取用户信息失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_by_userid(self, userid: str) -> Dict[str, Any]:
        """
        通过用户ID获取用户信息（包括unionid）

        Args:
            userid: 用户ID

        Returns:
            {"success": True, "unionid": "xxx", "name": "xxx"}
            或 {"success": False, "error": "xxx"}
        """
        url = f"{self.USER_API_URL}/get"
        params = {"access_token": self.get_access_token()}
        payload = {"userid": userid, "language": "zh_CN"}

        try:
            resp = requests.post(url, params=params, json=payload, timeout=10)
            data = resp.json()
            if data.get("errcode") == 0:
                return {
                    "success": True,
                    "unionid": data["result"].get("unionid", ""),
                    "name": data["result"].get("name", "")
                }
            else:
                return {"success": False, "error": data.get("errmsg", "获取用户信息失败")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_calendar_event(
        self,
        union_id: str,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        recurrence_rrule: str = None,
        is_all_day: bool = False,
        reminders: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        在用户主日历创建日程事件

        Args:
            union_id: 钉钉用户unionId
            summary: 日程标题
            description: 日程描述
            start_time: 开始时间
            end_time: 结束时间
            recurrence_rrule: RRULE重复规则字符串，如 "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20260525"
            is_all_day: 是否全天事件
            reminders: 提醒设置，如 [{"method": "dingtalk", "minutes": 30}]

        Returns:
            {"success": True, "event_id": "xxx"} 或 {"success": False, "error": "xxx"}
        """
        url = f"{self.API_BASE_URL}/calendar/users/{union_id}/calendars/primary/events"

        payload = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "timeZone": "Asia/Shanghai"
            },
            "end": {
                "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "timeZone": "Asia/Shanghai"
            },
            "isAllDay": is_all_day,
        }

        # 添加重复规则（RRULE字符串格式）
        if recurrence_rrule:
            payload["recurrence"] = [recurrence_rrule]

        # 添加提醒
        if reminders:
            payload["reminders"] = reminders

        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=15)
            data = resp.json()
            if resp.status_code == 200:
                return {"success": True, "event_id": data.get("id", "")}
            else:
                return {"success": False, "error": data.get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_calendar_event(self, union_id: str, event_id: str) -> Dict[str, Any]:
        """
        取消/删除日历事件

        Returns:
            {"success": True} 或 {"success": False, "error": "xxx"}
        """
        url = f"{self.API_BASE_URL}/calendar/users/{union_id}/calendars/primary/events/{event_id}"

        try:
            resp = requests.delete(url, headers=self._headers(), timeout=15)
            if resp.status_code in (200, 204):
                return {"success": True}
            data = resp.json()
            return {"success": False, "error": data.get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_calendar_event(self, union_id: str, event_id: str) -> Dict[str, Any]:
        """
        删除日历事件

        Returns:
            {"success": True} 或 {"success": False, "error": "xxx"}
        """
        return self.cancel_calendar_event(union_id, event_id)

    @staticmethod
    def generate_rrule(frequency: str, interval: int, until: datetime, by_day: str = None) -> str:
        """
        生成RRULE重复规则字符串

        Args:
            frequency: "WEEKLY" 或 "DAILY"
            interval: 间隔（1=每周/每天）
            until: 结束日期
            by_day: 星期几（仅weekly时），如 "TH" 或 "MO"

        Returns:
            RRULE字符串，如 "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=TH;UNTIL=20260525"
        """
        day_map = {
            "monday": "MO", "tuesday": "TU", "wednesday": "WE",
            "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU",
            "周一": "MO", "周二": "TU", "周三": "WE", "周四": "TH",
            "周五": "FR", "周六": "SA", "周日": "SU",
            "TH": "TH", "MO": "MO", "TU": "TU", "WE": "WE",
            "FR": "FR", "SA": "SA", "SU": "SU",
            "thursday": "TH", "monday": "MO", "tuesday": "TU", "wednesday": "WE",
            "friday": "FR", "saturday": "SA", "sunday": "SU",
        }

        freq = frequency.upper()  # WEEKLY or DAILY
        until_str = until.strftime("%Y%m%d")

        if freq == "WEEKLY" and by_day:
            # 先转小写查找
            abbr = day_map.get(by_day.lower(), day_map.get(by_day.upper(), by_day.upper()))
            return f"RRULE:FREQ={freq};INTERVAL={interval};BYDAY={abbr};UNTIL={until_str}"
        else:
            return f"RRULE:FREQ={freq};INTERVAL={interval};UNTIL={until_str}"

    def list_calendar_events(
        self,
        union_id: str,
        time_min: datetime,
        time_max: datetime,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        列出日历事件

        Args:
            union_id: 钉钉用户unionId
            time_min: 开始时间
            time_max: 结束时间
            max_results: 最大返回条数

        Returns:
            {"success": True, "events": [...]} 或 {"success": False, "error": "xxx"}
        """
        url = f"{self.API_BASE_URL}/calendar/users/{union_id}/calendars/primary/events"
        params = {
            "timeMin": time_min.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "timeMax": time_max.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "maxResults": max_results
        }

        try:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=15)
            data = resp.json()
            if resp.status_code == 200:
                return {"success": True, "events": data.get("events", [])}
            else:
                return {"success": False, "error": data.get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局单例（延迟初始化）
_dingtalk_service = None


def get_dingtalk_service() -> DingTalkService:
    global _dingtalk_service
    if _dingtalk_service is None:
        _dingtalk_service = DingTalkService()
    return _dingtalk_service
