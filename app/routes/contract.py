"""
合同路由
GET /api/contracts/stats - 合同统计
POST /api/contracts/upload - 上传CSV文件
GET /api/contracts/ - 合同列表
DELETE /api/contracts/{id} - 删除合同
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.models.contract import Contract
from app.models.import_log import ImportLog
from app.services.csv_importer import CSVImporter
from app import db

bp = Blueprint('contract', __name__, url_prefix='/api/contracts')


def mask_id_number(id_number):
    """身份证号脱敏"""
    if not id_number or len(id_number) < 8:
        return id_number or ''
    return id_number[:4] + '****' + id_number[-4:]


def mask_phone(phone):
    """手机号脱敏"""
    if not phone or len(phone) < 7:
        return phone or ''
    return phone[:3] + '****' + phone[-4:]


@bp.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    """上传并导入CSV合同文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': '只支持CSV格式文件'}), 400

    try:
        importer = CSVImporter(current_user.id)
        result = importer.import_file(file)

        return jsonify({
            'success': True,
            'summary': {
                'imported': result['imported'],
                'skipped_expired': result['skipped_expired'],
                'skipped_terminated': result['skipped_terminated'],
                'skipped_duplicate': result['skipped_duplicate'],
                'failed': result['failed']
            },
            'failed_detail': result.get('failed_detail', []),
            'import_log_id': result.get('import_log_id')
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@login_required
def get_contracts():
    """获取合同列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search', '')
    expire_within = request.args.get('expire_within', type=int)
    has_reminder = request.args.get('has_reminder', type=bool)

    # 构建查询
    query = Contract.query.filter_by(user_id=current_user.id, deleted=False)

    # 关键词搜索
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Contract.employee_name.ilike(search_pattern),
                Contract.id_number.ilike(search_pattern),
                Contract.unit_name.ilike(search_pattern)
            )
        )

    # N天内到期筛选
    if expire_within:
        target_date = date.today() + timedelta(days=expire_within)
        query = query.filter(Contract.contract_end_date <= target_date)

    # 按到期日期升序排列
    query = query.order_by(Contract.contract_end_date.asc())

    # 分页
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    contracts = pagination.items

    # 构建响应数据
    items = []
    today = date.today()
    for contract in contracts:
        days_until = (contract.contract_end_date - today).days if contract.contract_end_date else None
        items.append({
            'id': contract.id,
            'employee_name': contract.employee_name,
            'id_number': mask_id_number(contract.id_number),
            'employee_phone': mask_phone(contract.employee_phone),
            'contract_start_date': contract.contract_start_date.isoformat() if contract.contract_start_date else None,
            'contract_end_date': contract.contract_end_date.isoformat() if contract.contract_end_date else None,
            'days_until_expiry': days_until,
            'unit_name': contract.unit_name,
            'contract_type': contract.contract_type,
            'has_reminder': False  # 需要单独查询
                         if hasattr(contract, 'calendar_events') else False
        })

    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/<int:contract_id>', methods=['DELETE'])
@login_required
def delete_contract(contract_id):
    """删除合同（软删除）"""
    contract = Contract.query.filter_by(
        id=contract_id,
        user_id=current_user.id,
        deleted=False
    ).first()

    if not contract:
        return jsonify({'success': False, 'message': '合同不存在'}), 404

    contract.deleted = True
    contract.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True}), 200


@bp.route('/stats', methods=['GET'])
@login_required
def get_contract_stats():
    """获取合同统计数据"""
    today = date.today()
    reminder_days = 60  # 默认60天内到期为即将到期

    # 查询未删除的合同
    query = Contract.query.filter_by(user_id=current_user.id, deleted=False)

    # 总数
    total = query.count()

    # 有效合同（未过期）
    active = query.filter(Contract.contract_end_date > today).count()

    # 即将到期（60天内）
    expiring_date = today + timedelta(days=reminder_days)
    expiring_soon = query.filter(
        Contract.contract_end_date > today,
        Contract.contract_end_date <= expiring_date
    ).count()

    # 已过期
    expired = query.filter(Contract.contract_end_date <= today).count()

    return jsonify({
        'total': total,
        'active': active,
        'expiring_soon': expiring_soon,
        'expired': expired
    }), 200
