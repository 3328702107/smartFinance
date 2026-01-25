from datetime import datetime, timedelta
import uuid

from app import create_app
from core.database import db
from models.user import User, AuthAccount
from models.data import LoginLog, DataSource, DataQualityIssue
from models.device import Device
from models.transaction import FinancialTransaction
from models.risk import RiskEvent, EventTimeline, Alert
from models.analysis import RelatedUser, RiskAnalysisRecommendation

app = create_app("dev")


def main():
    with app.app_context():
        # 确保表存在
        db.create_all()

        # 清空旧数据（仅开发环境使用，生产千万别这么写）
        # 按外键依赖顺序删除：先删除子表，再删除父表
        for model in [
            Alert,
            RiskAnalysisRecommendation,
            RelatedUser,
            EventTimeline,
            RiskEvent,
            FinancialTransaction,
            LoginLog,
            DataQualityIssue,
            DataSource,
            Device,
            AuthAccount,
            User,
        ]:
            db.session.query(model).delete()
        db.session.commit()

        now = datetime.utcnow()

        # ========== 第一步：插入基础数据（无外键依赖） ==========

        # 用户（与 smartfinance.sql 中示例数据对齐）
        # 管理/测试账号 1
        u1 = User(
            user_id="58b84e778dff4ea48413c2a3b2ca1f59",
            username="test_user1",
            phone="13800000010",
            email="test_user1@example.com",
            status="正常",
            account_level="普通",
            registration_time=datetime(2026, 1, 13, 7, 41, 18),
        )
        # 管理/测试账号 2
        u2 = User(
            user_id="f3eb5f1e21a5432487c1f48918e4f36f",
            username="adon",
            phone="13800000000",
            email="alice@example.com",
            department="风险管理部",
            role="manager",
            employee_id="EMP-2023001",
            status="正常",
            account_level="普通",
            registration_time=datetime(2026, 1, 20, 9, 7, 31),
        )
        # 业务测试用户 1
        u3 = User(
            user_id="u_test_001",
            username="alice",
            phone="13800000001",
            email="alice@test.com",
            status="正常",
            account_level="普通",
            registration_time=datetime(2025, 10, 5, 14, 37, 47),
        )
        # 业务测试用户 2
        u4 = User(
            user_id="u_test_002",
            username="bob",
            phone="13800000002",
            email="bob@test.com",
            status="正常",
            account_level="VIP",
            registration_time=datetime(2025, 6, 27, 14, 37, 47),
        )
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # 数据源（丰富一些用于前端展示）
        # 交易数据中心
        s_trade_center = DataSource(
            source_id="src_trade_center",
            source_name="交易数据中心",
            source_type="数据库",
            connection_url="db-trade-01.internal",
            status="正常",
            last_sync_time=now - timedelta(minutes=5),
            sync_progress=78.0,
            collection_status="running",
            today_collected=148_562,
            estimated_completion="14:45",
        )
        # 用户行为分析平台
        s_behavior = DataSource(
            source_id="src_user_behavior",
            source_name="用户行为分析平台",
            source_type="API",
            connection_url="api-user-behavior.vpc",
            status="正常",
            last_sync_time=now - timedelta(minutes=10),
            sync_progress=45.0,
            collection_status="running",
            today_collected=326_891,
            estimated_completion="15:30",
        )
        # 图像存储服务
        s_image = DataSource(
            source_id="src_image_storage",
            source_name="图像存储服务",
            source_type="文件",
            connection_url="img-storage-02",
            status="异常",
            last_sync_time=now - timedelta(minutes=20),
            sync_progress=35.0,
            error_count=5,
            last_error_message="连接超时，已尝试 5 次重连",
            collection_status="stopped",
            today_collected=8_452,
        )
        # 设备指纹系统
        s_device = DataSource(
            source_id="src_device_fingerprint",
            source_name="设备指纹系统",
            source_type="API",
            connection_url="device-fingerprint-service",
            status="正常",
            last_sync_time=now - timedelta(minutes=3),
            sync_progress=92.0,
            collection_status="running",
            today_collected=67_321,
            estimated_completion="14:40",
        )
        # 第三方信用评估接口
        s_credit = DataSource(
            source_id="src_third_party_credit",
            source_name="第三方信用评估接口",
            source_type="API",
            connection_url="api.thirdparty-credit.com",
            status="正常",
            last_sync_time=now - timedelta(minutes=15),
            sync_progress=23.0,
            collection_status="running",
            today_collected=12_456,
            estimated_completion="16:10",
        )
        # 兼容其它示例中使用的两个数据源 ID
        s_tx = DataSource(
            source_id="src_tx",
            source_name="交易日志源",
            source_type="数据库",
            status="正常",
            last_sync_time=now,
            sync_progress=100.0,
            collection_status="running",
        )
        s_login = DataSource(
            source_id="src_login",
            source_name="登录日志源",
            source_type="API",
            status="异常",
            last_sync_time=now - timedelta(hours=3),
            sync_progress=80.0,
            error_count=3,
            last_error_message="网络超时",
            collection_status="running",
        )
        db.session.add_all([s_trade_center, s_behavior, s_image, s_device, s_credit, s_tx, s_login])
        db.session.commit()

        # ========== 第二步：插入依赖 User 的数据 ==========

        from werkzeug.security import generate_password_hash

        # 认证账户（密码），为 4 个用户都生成默认密码 123456
        a1 = AuthAccount(user_id="58b84e778dff4ea48413c2a3b2ca1f59", password_hash=generate_password_hash("123456"))
        a2 = AuthAccount(user_id="f3eb5f1e21a5432487c1f48918e4f36f", password_hash=generate_password_hash("123456"))
        a3 = AuthAccount(user_id="u_test_001", password_hash=generate_password_hash("123456"))
        a4 = AuthAccount(user_id="u_test_002", password_hash=generate_password_hash("123456"))
        db.session.add_all([a1, a2, a3, a4])

        # 设备
        d1 = Device(
            device_id="d_test_001",
            user_id="u_test_001",
            device_name="Alice iPhone",
            os_type="iOS",
            ip_address="1.1.1.1",
            location="武汉",
            is_normal=True,
            last_login_time=now - timedelta(hours=1),
        )
        d2 = Device(
            device_id="d_test_002",
            user_id="u_test_002",
            device_name="Bob Android",
            os_type="Android",
            ip_address="2.2.2.2",
            location="北京",
            is_normal=False,
            last_login_time=now - timedelta(hours=2),
        )
        db.session.add_all([d1, d2])
        db.session.commit()

        # ========== 第三步：插入依赖 DataSource 的数据 ==========

        # 为不同数据源造一些数据质量问题，数量与原型示例基本一致：
        # 交易数据中心：12 个；行为平台：5 个；图像存储：0 个；设备指纹：0 个；第三方信用：39 个
        quality_issues = []

        # 交易数据中心：12 个问题（混合多种类型）
        for i in range(12):
            quality_issues.append(
                DataQualityIssue(
                    source_id="src_trade_center",
                    issue_type=["缺失字段", "格式错误", "值异常", "数据不一致"][i % 4],
                    description="交易明细字段存在缺失或异常",
                    affected_records_count=100 + i * 5,
                    severity=["中", "低", "高"][i % 3],
                    status="未处理",
                )
            )

        # 用户行为分析平台：5 个问题
        for i in range(5):
            quality_issues.append(
                DataQualityIssue(
                    source_id="src_user_behavior",
                    issue_type="值异常",
                    description="用户会话时长出现异常尖刺",
                    affected_records_count=200 + i * 10,
                    severity="中",
                    status="未处理",
                )
            )

        # 第三方信用评估接口：39 个格式问题
        for i in range(39):
            quality_issues.append(
                DataQualityIssue(
                    source_id="src_third_party_credit",
                    issue_type="格式错误",
                    description="返回 JSON 字段缺失或类型错误",
                    affected_records_count=20 + i,
                    severity="低",
                    status="未处理",
                )
            )

        # 登录日志源：1 个中等问题（沿用原有示例）
        quality_issues.append(
            DataQualityIssue(
                source_id="src_login",
                issue_type="缺失字段",
                description="部分登录记录缺失地理位置信息",
                affected_records_count=50,
                severity="中",
                status="未处理",
            )
        )

        db.session.add_all(quality_issues)
        db.session.commit()

        # ========== 第四步：插入依赖 User 和 Device 的数据 ==========

        # 登录日志
        log1 = LoginLog(
            user_id="u_test_001",
            device_id="d_test_001",
            ip_address="1.1.1.1",
            login_time=now - timedelta(hours=1),
            login_status="成功",
            login_location="武汉",
            client_type="APP",
            session_token="token1",
        )
        log2 = LoginLog(
            user_id="u_test_001",
            device_id="d_test_001",
            ip_address="3.3.3.3",
            login_time=now - timedelta(minutes=10),
            login_status="成功",
            login_location="上海",
            client_type="WEB",
            session_token="token2",
        )
        db.session.add_all([log1, log2])

        # 交易
        tx1 = FinancialTransaction(
            tx_id="tx_test_001",
            user_id="u_test_001",
            device_id="d_test_001",
            amount=500.00,
            currency="CNY",
            transaction_time=now - timedelta(minutes=30),
            status="成功",
            category="消费",
            ip_address="1.1.1.1",
        )
        tx2 = FinancialTransaction(
            tx_id="tx_test_002",
            user_id="u_test_001",
            device_id="d_test_001",
            amount=20000.00,
            currency="CNY",
            transaction_time=now - timedelta(minutes=5),
            status="成功",
            category="转账",
            ip_address="3.3.3.3",
        )
        db.session.add_all([tx1, tx2])
        db.session.commit()

        # ========== 第五步：插入风险事件及关联数据 ==========

        ev_id = "ev_test_001"
        ev = RiskEvent(
            event_id=ev_id,
            event_type="异常交易",
            risk_level="高",
            score=90,
            description="大额异地交易，短时间内多笔交易",
            detection_time=now - timedelta(minutes=4),
            duration="0h 4m",
            status="待处理",
            user_id="u_test_001",
            device_id="d_test_001",
            ip_address="3.3.3.3",
            trigger_rule="规则引擎",
            severity_scope="个人",
        )
        db.session.add(ev)
        db.session.commit()

        # 时间线
        tl1 = EventTimeline(
            event_id=ev_id,
            step_no=1,
            step_title="登录",
            step_description="用户在武汉登录",
            timestamp=now - timedelta(hours=1),
            type="登录",
            related_entity=str(log1.log_id),
        )
        tl2 = EventTimeline(
            event_id=ev_id,
            step_no=2,
            step_title="异地登录",
            step_description="用户在上海再次登录",
            timestamp=now - timedelta(minutes=10),
            type="登录",
            related_entity=str(log2.log_id),
        )
        tl3 = EventTimeline(
            event_id=ev_id,
            step_no=3,
            step_title="大额交易",
            step_description="发生一笔 20000 元转账",
            timestamp=now - timedelta(minutes=5),
            type="交易",
            related_entity="tx_test_002",
        )
        db.session.add_all([tl1, tl2, tl3])

        # 告警
        al1 = Alert(
            alert_id="al_test_001",
            event_id=ev_id,
            alert_type="异常交易告警",
            alert_level="高",
            triggered_at=now - timedelta(minutes=4),
            status="待处理",
        )
        db.session.add(al1)

        # 关联用户
        ru1 = RelatedUser(
            event_id=ev_id,
            user_id="u_test_002",
            relationship_type="同IP注册",
            risk_score=70,
        )
        db.session.add(ru1)

        # 风险分析建议
        rec1 = RiskAnalysisRecommendation(
            event_id=ev_id,
            risk_assessment="该用户近期存在多次异地登录和大额交易，疑似账户被盗用。",
            recommendation_text="建议立即冻结账户，联系用户进行身份核验。",
            priority="高",
        )
        db.session.add(rec1)

        db.session.commit()

        print("Test data inserted.")


if __name__ == "__main__":
    main()
