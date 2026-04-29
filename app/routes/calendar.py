"""
日程路由
POST /api/calendar/events - 创建日程
DELETE /api/calendar/events/{id} - 删除单条日程
DELETE /api/calendar/events/batch - 批量删除日程
GET /api/calendar/events - 日程列表
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.models.calendar_event import CalendarEvent
from app.models.contract import Contract
from app.services.dingtalk import DingTalkService
from app import db

bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')


def generate_rrule(frequency, weekday, hour, minute, start_date, stop_days_before, contract_end_date):
    """生成iCalendar RRULE字符串"""
    # weekday映射
    weekday_map = {'周一': 'MO', '周二': 'TU', '周三': 'WE', '周四': 'TH', '周五': 'FR', '周六': 'SA', '周日': 'SU'}
    weekday_code = weekday_map.get(weekday, 'TH')

    # 计算结束日期
    end_date = contract_end_date - timedelta(days=stop_days_before)
    end_date_str = end_date.strftime('%Y%m%d')

    if frequency == 'daily':
        return f'FREQ=DAILY;INTERVAL=1;UNTIL={end_date_str}'
    else:  # weekly
        return f'FREQ=WEEKLY;INTERVAL=1;BYDAY={weekday_code};UNTIL={end_date_str}'


@bp.route('/events', methods=['POST'])
@login_required
def create_events():
    """创建日程提醒"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    contract_ids = data.get('contract_ids', [])
    if not contract_ids:
        return jsonify({'success': False, 'message': '未选择合同'}), 400

    reminder_days = data.get('reminder_days', 60)
    frequency = data.get('frequency', 'weekly')
    weekday = data.get('weekday', '周四')
    hour = data.get('hour', 9)
    minute = data.get('minute', 0)
    stop_days_before = data.get('stop_days_before', 5)
    overwrite = data.get('overwrite', False)

    # 检查用户是否有unionid
    if not current_user.unionid:
        return jsonify({
            'success': False,
            'message': '当前用户未配置钉钉unionId，无法创建日程'
        }), 400

    success_count = 0
    failed_count = 0
    skipped_exists = 0
    errors = []

    dingtalk_service = DingTalkService()

    for contract_id in contract_ids:
        contract = Contract.query.filter_by(
            id=contract_id,
            user_id=current_user.id,
            deleted=False
        ).first()

        if not contract:
            failed_count += 1
            errors.append({'contract_id': contract_id, 'reason': '合同不存在'})
            continue

        # 检查是否已有日程
        existing_event = CalendarEvent.query.filter_by(
            contract_id=contract_id,
            user_id=current_user.id,
            deleted=False
        ).first()

        if existing_event:
            if overwrite:
                # 先删除旧的
                try:
                    dingtalk_service.delete_calendar_event(current_user.unionid, existing_event.event_id)
                except Exception:
                    pass  # 忽略钉钉删除失败
                existing_event.deleted = True
                db.session.commit()
            else:
                skipped_exists += 1
                continue

        # 计算提醒开始日期
        reminder_start_date = contract.contract_end_date - timedelta(days=reminder_days)
        if reminder_start_date < date.today():
            reminder_start_date = date.today()

        # 计算结束日期
        reminder_end_date = contract.contract_end_date - timedelta(days=stop_days_before)
        if reminder_end_date <= reminder_start_date:
            errors.append({
                'contract_id': contract_id,
                'reason': f'合同剩余天数不足{reminder_days - stop_days_before}天，无法创建提醒'
            })
            failed_count += 1
            continue

        # 构建日程数据
        summary = f"合同到期提醒：{contract.employee_name}（{contract.unit_name or ''}）"
        description = f"员工姓名：{contract.employee_name}\n所在单位：{contract.unit_name or ''}\n合同到期日：{contract.contract_end_date}\n联系电话：{contract.employee_phone or ''}\n合同类型：{contract.contract_type or ''}"

        start_time = datetime.combine(reminder_start_date, datetime.min.time().replace(hour=hour, minute=minute))
        end_time = start_time + timedelta(minutes=30)

        rrule = generate_rrule(frequency, weekday, hour, minute, reminder_start_date, stop_days_before, contract.contract_end_date)

        try:
            # 调用钉钉API创建日程
            result = dingtalk_service.create_calendar_event(
                union_id=current_user.unionid,
                summary=summary,
                description=description,
                start_time=start_time,
                end_time=end_time,
                recurrence_rrule=rrule
            )

            if not result.get('success'):
                errors.append({'contract_id': contract_id, 'reason': result.get('error', '创建失败')})
                failed_count += 1
                continue

            event_id = result.get('event_id')

            # 保存本地记录
            calendar_event = CalendarEvent(
                user_id=current_user.id,
                contract_id=contract_id,
                event_id=event_id,
                summary=summary,
                description=description,
                start_time=start_time,
                end_time=end_time,
                recurrence=rrule,
                source='created'
            )
            db.session.add(calendar_event)
            db.session.commit()
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append({'contract_id': contract_id, 'reason': str(e)})

    return jsonify({
        'success': success_count,
        'failed': failed_count,
        'skipped_exists': skipped_exists,
        'errors': errors
    }), 200


@bp.route('/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """删除单条日程"""
    mode = request.args.get('mode', 'hard')

    event = CalendarEvent.query.filter_by(
        id=event_id,
        user_id=current_user.id,
        deleted=False
    ).first()

    if not event:
        return jsonify({'success': False, 'message': '日程不存在'}), 404

    dingtalk_deleted = False

    if mode == 'hard':
        # 硬删除：同时删除钉钉日程
        if current_user.unionid:
            try:
                dingtalk_service = DingTalkService()
                result = dingtalk_service.delete_calendar_event(current_user.unionid, event.event_id)
                dingtalk_deleted = result.get('success', False)
            except Exception:
                pass  # 钉钉删除失败不影响本地删除

    # 软删除或硬删除都标记为删除
    event.deleted = True
    event.sync_time = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'dingtalk_deleted': dingtalk_deleted}), 200


@bp.route('/events/batch', methods=['DELETE'])
@login_required
def delete_events_batch():
    """批量删除日程"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    ids = data.get('ids', [])
    mode = data.get('mode', 'hard')

    if not ids:
        return jsonify({'success': False, 'message': '未选择日程'}), 400

    deleted_count = 0
    dingtalk_deleted_count = 0

    events = CalendarEvent.query.filter(
        CalendarEvent.id.in_(ids),
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.deleted == False
    ).all()

    if mode == 'hard' and current_user.unionid:
        dingtalk_service = DingTalkService()
        for event in events:
            try:
                dingtalk_service.delete_calendar_event(current_user.unionid, event.event_id)
                dingtalk_deleted_count += 1
            except Exception:
                pass

    for event in events:
        event.deleted = True
        event.sync_time = datetime.utcnow()
        deleted_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'deleted_count': deleted_count,
        'dingtalk_deleted_count': dingtalk_deleted_count
    }), 200


@bp.route('/events', methods=['GET'])
@login_required
def get_events():
    """获取日程列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search', '')

    query = CalendarEvent.query.filter_by(
        user_id=current_user.id,
        deleted=False
    )

    # 关键词搜索（搜索员工姓名或单位名称）
    if search:
        search_pattern = f'%{search}%'
        query = query.join(Contract).filter(
            db.or_(
                Contract.employee_name.ilike(search_pattern),
                Contract.unit_name.ilike(search_pattern)
            )
        )

    # 按创建时间倒序
    query = query.order_by(CalendarEvent.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    events = pagination.items

    items = []
    for event in events:
        contract = Contract.query.get(event.contract_id) if event.contract_id else None
        items.append({
            'id': event.id,
            'summary': event.summary,
            'employee_name': contract.employee_name if contract else None,
            'contract_end_date': contract.contract_end_date.isoformat() if contract and contract.contract_end_date else None,
            'start_time': event.start_time.isoformat() if event.start_time else None,
            'recurrence': event.recurrence,
            'created_at': event.created_at.isoformat() if event.created_at else None
        })

    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200
