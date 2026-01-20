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

        # 用户
        u1 = User(
            user_id="u_test_001",
            username="alice",
            phone="13800000001",
            email="alice@test.com",
            status="正常",
            account_level="普通",
            registration_time=now - timedelta(days=100),
        )
        u2 = User(
            user_id="u_test_002",
            username="bob",
            phone="13800000002",
            email="bob@test.com",
            status="正常",
            account_level="VIP",
            registration_time=now - timedelta(days=200),
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        # 数据源
        s1 = DataSource(
            source_id="src_tx",
            source_name="交易日志源",
            source_type="数据库",
            status="正常",
            last_sync_time=now,
            sync_progress=100.0,
        )
        s2 = DataSource(
            source_id="src_login",
            source_name="登录日志源",
            source_type="API",
            status="异常",
            last_sync_time=now - timedelta(hours=3),
            sync_progress=80.0,
            error_count=3,
            last_error_message="网络超时",
        )
        db.session.add_all([s1, s2])
        db.session.commit()

        # ========== 第二步：插入依赖 User 的数据 ==========

        from werkzeug.security import generate_password_hash

        # 认证账户（密码）
        a1 = AuthAccount(
            user_id="u_test_001",
            password_hash=generate_password_hash("123456")
        )
        a2 = AuthAccount(
            user_id="u_test_002",
            password_hash=generate_password_hash("123456")
        )
        db.session.add_all([a1, a2])

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

        q1 = DataQualityIssue(
            source_id="src_login",
            issue_type="缺失字段",
            description="部分登录记录缺失地理位置信息",
            affected_records_count=50,
            severity="中",
            status="未处理",
        )
        db.session.add(q1)
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
