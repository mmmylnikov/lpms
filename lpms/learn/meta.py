from datetime import date
from typing import Self

from allauth.socialaccount.models import SocialAccount
from django.db.models import QuerySet
from django.contrib.auth.models import AnonymousUser

from user.models import User
from course.models import Team, Enrollment, Course, Track
from learn.models import (
    Program,
    Week,
    Lesson,
    Challenge,
    Homework,
    HomeworkStatus,
)
from learn.enums import HomeworkStatuses


class LearnMeta:
    user: User | AnonymousUser
    user_github: SocialAccount
    teams_learn: QuerySet[Team] | None
    teams_review: QuerySet[Team] | None
    tasks_learn: QuerySet[Homework] | None
    tasks_status_learn: QuerySet[HomeworkStatus] | None
    account_fullness_errors: list[str]
    support_links: list[tuple[str, str]]

    def __init__(self, user: User | AnonymousUser) -> None:
        self.user = user
        self.get_user_github_account()

    def get_teams_learn(self) -> QuerySet[Team] | None:
        """Return teams where the user is a student"""
        if isinstance(self.user, AnonymousUser):
            return None
        self.teams_learn = self.user.team_set.all().select_related(
            "tutor", "enrollment", "enrollment__course"
        )
        return self.teams_learn

    def get_teams_review(self) -> QuerySet[Team] | None:
        """Return teams where the user is a tutor"""
        if isinstance(self.user, AnonymousUser):
            return None
        self.teams_review = (
            Team.objects.filter(tutor=self.user)
            .select_related("tutor", "enrollment", "enrollment__course")
            .prefetch_related("students")
        )
        return self.teams_review

    def get_teams(self) -> Self:
        self.get_teams_learn()
        self.get_teams_review()
        return self

    def get_tasks_learn(self, only_at_work: bool = True) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        tasks_learn = Homework.objects.filter(user=self.user)
        if not only_at_work:
            tasks_learn = tasks_learn.exclude(
                status__in=[
                    HomeworkStatuses.approved.name,
                    HomeworkStatuses.available.name,
                ]
            )
        self.tasks_learn = tasks_learn.select_related(
            "challenge",
            "challenge__track",
            "week",
            "team",
            "team__enrollment",
            "team__enrollment__course",
        )
        self.tasks_status_learn = HomeworkStatus.objects.filter(
            homework__in=self.tasks_learn
        ).select_related(
            "homework",
            "homework__challenge",
            "homework__week",
            "homework__team",
            "homework__team__enrollment",
            "homework__team__enrollment__course",
        )
        return self

    def get_tasks_status_latest(self) -> list[HomeworkStatus] | None:
        if not self.tasks_status_learn:
            return None
        tasks_all = list(self.tasks_status_learn)
        tasks_latest = []
        challenge_set: set[Challenge] = set()
        for task in tasks_all:
            challenge = task.homework.challenge
            if challenge in challenge_set:
                continue
            challenge_set.add(challenge)
            tasks_latest.append(task)
        return tasks_latest

    def get_user_github_account(self) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        accounts = {}  # type: ignore
        for (
            account
        ) in self.user.socialaccount_set.all().iterator():  # type: ignore
            providers = accounts.setdefault(account.provider, [])
            providers.append(account)
        if accounts.get("github"):
            self.user_github = accounts["github"][0]
        return self

    def check_account_fullness(self) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        errors = []
        if self.user.first_name == "" or self.user.last_name == "":
            errors.append("Заполните имя и фамилию")
        if self.user.tg_username is None:
            errors.append("Укажите ник в Telegram")
        if not hasattr(self, "user_github"):
            errors.append("Привяжите GitHub аккаунт")
        self.account_fullness_errors = errors
        return self

    def get_support_links(
        self,
        course: Course | None = None,
        enrollment: Enrollment | None = None,
        team: Team | None = None,
    ) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        support_links = []
        if course and course.tg_chat:
            support_links.append((course.tg_chat, f"Чат курса {course.name}"))
        if enrollment and enrollment.tg_chat:
            support_links.append(
                (enrollment.tg_chat, f"Чат потока {enrollment.slug}")
            )
        if team and team.tg_chat:
            support_links.append(
                (team.tg_chat, f"Чат группы (куратор {team.tutor.first_name})")
            )
        self.support_links = support_links
        return self

    def get_homework_status_ids(
        self, tutor_id: int, status: HomeworkStatuses
    ) -> list[int]:
        homework_statuses = (
            HomeworkStatus.objects.filter(
                tutor=tutor_id,
            )
            .order_by("homework_id", "-updated_at")
            .values("id", "status", "updated_at", "homework_id")
        )
        homework_set = set()
        last_statuses = []
        for homework_status in homework_statuses:
            homework_id = homework_status["homework_id"]
            if homework_id in homework_set:
                continue
            homework_set.add(homework_id)
            last_statuses.append(
                {
                    "status_id": homework_status["id"],
                    "status": homework_status["status"],
                }
            )
        statuses_ids = []
        for last_status in last_statuses:
            if not last_status["status"] == status.name:
                continue
            statuses_ids.append(last_status["status_id"])
        return statuses_ids  # type: ignore

    def get_tutor_stats(self, status: HomeworkStatuses) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        homework_status_ids = self.get_homework_status_ids(
            tutor_id=self.user.id, status=status
        )
        self.tutor_stats_review = (
            HomeworkStatus.objects.filter(
                id__in=homework_status_ids,
                status=status.name,
            )
            .select_related(
                "student",
                "homework__challenge",
                "homework__team__enrollment__course",
                "homework__week",
            )
            .order_by("updated_at")
        )
        return self

    def get_admin_stats(self, status: HomeworkStatuses) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        tutors = User.objects.filter(is_tutor=True).order_by(
            "last_name", "first_name"
        )
        admin_stats = {}
        for tutor in tutors:
            homework_status_ids = self.get_homework_status_ids(
                tutor_id=tutor.pk, status=status
            )
            tutor_stat = (
                HomeworkStatus.objects.filter(
                    id__in=homework_status_ids,
                    status=status.name,
                )
                .select_related(
                    "student",
                    "homework__challenge",
                    "homework__team__enrollment__course",
                    "homework__week",
                )
                .order_by("updated_at")
            )
            admin_stats[tutor] = tutor_stat
        self.admin_stats = admin_stats
        return self


class StudentLearnMeta(LearnMeta):
    # course
    team: Team
    enrollment: Enrollment
    course: Course
    tutor: User
    tracks: QuerySet[Track]
    # learn
    program: Program | None
    weeks: QuerySet[Week]
    week_current: Week | None
    week_current_number: int
    week: Week
    week_number: int
    week_tracks: QuerySet[Track]
    week_lessons: dict[Track, list[Lesson]]
    week_challenges: (
        dict[
            Track,
            list[tuple[Challenge, Homework | None, HomeworkStatus | None]],
        ]
        | None
    ) = None

    def __init__(
        self, user: User | AnonymousUser, team: Team, week_number: int
    ) -> None:
        super().__init__(user)
        self.init_course_meta(team=team)
        self.init_learn_meta(week_number=week_number)

    def init_course_meta(self, team: Team) -> None:
        self.team = team
        self.enrollment = team.enrollment
        self.course = self.enrollment.course
        self.tracks = Track.objects.filter(course=self.course)
        self.tutor = self.team.tutor

    def init_learn_meta(self, week_number: int) -> None:
        self.week_number = week_number

        self.program = (
            Program.objects.filter(enrollments__in=[self.enrollment])
            .prefetch_related("weeks")
            .last()
        )
        if not self.program:
            return

        self.weeks = self.program.weeks.all()
        if not self.weeks:
            return

        self.get_current_week()
        if not self.week:
            return

        self.get_lessons_from_week()
        self.get_challenges_from_week()

    def get_current_week(self) -> None:
        self.week_current_number = (
            date.today() - self.enrollment.start
        ).days // 7 + 1
        self.week_current = self.weeks.filter(
            number=self.week_current_number
        ).last()
        if not self.week_number and self.week_current:
            self.week_number = self.week_current_number
            self.week = self.week_current
        elif self.weeks:
            self.week = self.weeks.get(number=self.week_number)

    def get_lessons_from_week(self) -> None:
        lessons = list(self.week.lessons.all().select_related("track"))
        self.week_lessons = {
            track: [lesson for lesson in lessons if lesson.track == track]
            for track in self.tracks
        }  # type: ignore

    def get_challenges_from_week(self) -> None:
        challenges = list(self.week.challenges.all().select_related("track"))
        week_challenges = dict()
        if not self.tracks:
            self.week_challenges = None
            return None
        for track in self.tracks:
            week_homework = []
            for challenge in challenges:
                if challenge.track != track:
                    continue
                week_homework.append((challenge, None, None))
            week_challenges.update(
                {
                    track: week_homework,
                }
            )
        self.week_challenges = week_challenges  # type: ignore

    def add_task_for_week_challenges(self) -> Self:
        if self.user == self.tutor:
            return self
        if not self.tasks_learn or not self.tasks_status_learn:
            return self
        tasks = list(self.tasks_learn)
        tasks_status = list(self.tasks_status_learn)
        week_challenges = {}
        if not self.week_challenges:
            return self
        for track, homework in self.week_challenges.items():
            week_homework = []
            challenges = [items[0] for items in homework]
            for challenge in challenges:
                task = None
                task_status = None
                week_tasks = [
                    task for task in tasks if task.challenge == challenge
                ]
                if week_tasks:
                    task = week_tasks[0]
                    task_statuses = [
                        status
                        for status in tasks_status
                        if status.homework == task
                    ]
                    if task_statuses:
                        task_status = task_statuses[0]
                week_homework.append((challenge, task, task_status))
            week_challenges.update(
                {
                    track: week_homework,
                }
            )
        self.week_challenges = week_challenges
        return self


class TutorLearnMeta(StudentLearnMeta):
    # review
    students: dict[User, SocialAccount]
    week_reviews: (
        dict[User, list[tuple[Homework | None, HomeworkStatus | None]]] | None
    ) = None

    def __init__(
        self, user: User | AnonymousUser, team: Team, week_number: int
    ) -> None:
        super().__init__(user, team, week_number)
        self.get_students()
        self.get_week_reviews()

    def get_students(self) -> None:
        accounts = SocialAccount.objects.filter(
            user__in=list(self.team.students.all())
        ).select_related("user")
        self.students = {account.user: account for account in accounts}

    def get_week_reviews(self) -> None:
        if isinstance(self.user, AnonymousUser):
            return None
        reviews = Homework.objects.filter(
            week=self.week,
            team=self.team,
        ).select_related(
            "user",
            "challenge",
        )
        week_reviews: dict[
            User, list[tuple[Homework | None, HomeworkStatus | None]]
        ] = dict()
        review_statuses = list(
            HomeworkStatus.objects.filter(tutor=self.user).select_related(
                "student", "tutor", "homework"
            )
        )
        for review in reviews:
            if not week_reviews.get(review.user):
                week_reviews[review.user] = []
            student_review_status = [
                status
                for status in review_statuses
                if (
                    status.student == review.user and status.homework == review
                )
            ]
            if not student_review_status:
                continue
            review_status = student_review_status[0]
            if review_status.status not in [
                HomeworkStatuses.review.name,
                HomeworkStatuses.approved.name,
            ]:
                continue
            week_reviews[review.user].append((review, review_status))
        self.week_reviews = week_reviews
