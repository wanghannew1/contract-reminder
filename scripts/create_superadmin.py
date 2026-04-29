#!/usr/bin/env python3
"""
创建超级管理员脚本

用法：
    python scripts/create_superadmin.py --name "管理员" --phone 13800000000 --password "Admin@123456"
    python scripts/create_superadmin.py --name "管理员" --phone 13800000000 --password "Admin@123456" --unionid "xxx"
"""
import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User


def main():
    parser = argparse.ArgumentParser(description='创建超级管理员账号')
    parser.add_argument('--name', required=True, help='管理员姓名')
    parser.add_argument('--phone', required=True, help='手机号（登录名）')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--unionid', default='', help='钉钉unionId（可选）')

    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        # 检查手机号是否已存在
        existing = User.query.filter_by(phone=args.phone).first()
        if existing:
            print(f"错误：手机号 {args.phone} 已存在")
            sys.exit(1)

        # 创建用户
        user = User(
            name=args.name,
            phone=args.phone,
            unionid=args.unionid if args.unionid else None,
            is_active=True,
            is_superadmin=True
        )
        user.set_password(args.password)

        db.session.add(user)
        db.session.commit()

        print(f"✓ 超级管理员创建成功！")
        print(f"  姓名：{args.name}")
        print(f"  手机号：{args.phone}")
        print(f"  角色：超级管理员")
        print(f"  请使用手机号和密码登录系统")


if __name__ == '__main__':
    main()
