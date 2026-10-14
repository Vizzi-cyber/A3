import asyncio
import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.teacher import get_pilot_report
from app.models.user import UserModel
from app.models.knowledge import LearningRecordModel, QuizResultModel
from app.models.trend import TrendDataModel
from app.models.experiment import ExperimentLogModel
from app.models.monitor import ApiMonitorModel


class PilotReportTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        for model in (UserModel, LearningRecordModel, QuizResultModel,
                      TrendDataModel, ExperimentLogModel, ApiMonitorModel):
            model.__table__.create(self.engine)
        self.db = Session(self.engine)
        now = datetime.now(timezone.utc)
        self.db.add_all([
            UserModel(student_id="reader", username="Reader", role="student", class_id="A"),
            UserModel(student_id="quizzer", username="Quizzer", role="student", class_id="B"),
            LearningRecordModel(record_id="r", student_id="reader", kp_id="kp", action="read"),
            QuizResultModel(quiz_id="q", student_id="quizzer", kp_id="kp", score=80),
            ExperimentLogModel(student_id="experimenter", experiment_type="circuit_simulate"),
            TrendDataModel(student_id="reader", date="2026-01-01", trend_state="warning", created_at=now - timedelta(days=1)),
            TrendDataModel(student_id="reader", date="2026-01-02", trend_state="growth", created_at=now),
            TrendDataModel(student_id="reader", date="2026-01-02", trend_state="stable", created_at=now),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def report(self, student_id=None, class_id=None):
        return asyncio.run(get_pilot_report(
            days=30, student_id=student_id, class_id=class_id,
            format="json", db=self.db, _teacher="teacher",
        ))

    def test_trend_counts_each_student_once_using_latest_record(self):
        self.assertEqual(self.report()["trend_distribution"], {"stable": 1})

    def test_active_students_include_quiz_and_experiment_participants(self):
        report = self.report()
        self.assertEqual(report["summary"]["active_students"], 3)
        self.assertEqual({row["student_id"] for row in report["students"]},
                         {"reader", "quizzer", "experimenter"})

    def test_student_filter_cannot_override_class_filter(self):
        report = self.report(student_id="quizzer", class_id="A")
        self.assertEqual(report["summary"]["total_quizzes"], 0)
        self.assertEqual(report["summary"]["active_students"], 0)
        self.assertEqual(report["students"], [])
        self.assertEqual(self.report(class_id="A")["summary"]["active_students"], 1)


if __name__ == "__main__":
    unittest.main()
