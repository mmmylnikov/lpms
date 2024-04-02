from datetime import date
from typing import Self

from allauth.socialaccount.models import SocialAccount
from django.db.models import QuerySet
from django.contrib.auth.models import AnonymousUser

from user.models import User
from course.models import Team, Enrollment, Course, Track
from learn.models import Program, Week, Lesson, Challenge, Homework
from learn.enums import HomeworkStatuses


class LearnMeta:
    user: User | AnonymousUser
    user_github: SocialAccount
    teams_learn: QuerySet[Team] | None
    teams_review: QuerySet[Team] | None
    tasks_learn: QuerySet[Homework] | None

    def __init__(self, user: User | AnonymousUser) -> None:
        self.user = user
        self.get_user_github_account()

    def get_teams_learn(self) -> QuerySet[Team] | None:
        """ Return teams where the user is a student """
        if isinstance(self.user, AnonymousUser):
            return None
        self.teams_learn = self.user.team_set.all().select_related(
            'tutor', 'enrollment', 'enrollment__course')
        return self.teams_learn

    def get_teams_review(self) -> QuerySet[Team] | None:
        """ Return teams where the user is a tutor """
        if isinstance(self.user, AnonymousUser):
            return None
        self.teams_review = Team.objects.filter(tutor=self.user)
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
            tasks_learn = tasks_learn.exclude(status__in=[
                HomeworkStatuses.approved.name,
                HomeworkStatuses.available.name])
        self.tasks_learn = tasks_learn.select_related(
                    'сhallenge', 'сhallenge__track', 'week',
                    'team', 'team__enrollment', 'team__enrollment__course')
        return self

    def get_user_github_account(self) -> Self:
        if isinstance(self.user, AnonymousUser):
            return self
        accounts = {}  # type: ignore
        for account in self.user.socialaccount_set.all(  # type: ignore
                ).iterator():
            providers = accounts.setdefault(account.provider, [])
            providers.append(account)
        if accounts.get('github'):
            self.user_github = accounts['github'][0]
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
    week_lessons = dict[Track, list[Lesson]]
    week_challenges = dict[Track, list[tuple[Challenge, Homework | None]]]

    def __init__(self,
                 user: User | AnonymousUser,
                 team: Team,
                 week_number: int) -> None:
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

        self.program = Program.objects.filter(
            enrollments__in=[self.enrollment]).prefetch_related('weeks').last()
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
            date.today() - self.enrollment.start).days // 7 + 1
        self.week_current = self.weeks.filter(
            number=self.week_current_number).last()
        if not self.week_number and self.week_current:
            self.week_number = self.week_current_number
            self.week = self.week_current
        elif self.weeks:
            self.week = self.weeks.get(number=self.week_number)

    def get_lessons_from_week(self) -> None:
        lessons = list(self.week.lessons.all().select_related('track'))
        self.week_lessons = {track: [
            lesson for lesson in lessons if lesson.track == track
            ] for track in self.tracks}  # type: ignore

    def get_challenges_from_week(self) -> None:
        challenges = list(self.week.challenges.all().select_related('track'))
        week_challenges = {}
        for track in self.tracks:
            week_homework = []
            for challenge in challenges:
                if challenge.track != track:
                    continue
                week_homework.append((challenge, None))
            week_challenges.update({
                track: week_homework,
            })
        self.week_challenges = week_challenges  # type: ignore

    def add_task_for_week_challenges(self) -> Self:
        if not self.tasks_learn:
            return self
        tasks = list(self.tasks_learn)
        week_challenges = {}
        for track, homework in self.week_challenges.items():  # type: ignore
            week_homework = []
            for challenge, _ in homework:  # type: ignore
                task = None
                week_tasks = [
                    task for task in tasks if task.сhallenge == challenge]
                if week_tasks:
                    task = week_tasks[0]
                week_homework.append((challenge, task))
            week_challenges.update({
                track: week_homework,
            })
        self.week_challenges = week_challenges  # type: ignore
        return self
