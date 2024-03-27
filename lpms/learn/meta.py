from datetime import date
from typing import Self

from django.db.models import QuerySet
from django.contrib.auth.models import AnonymousUser

from user.models import User
from course.models import Team, Enrollment, Course, Track
from learn.models import Program, Week, Lesson, Challenge


class LearnMeta:
    user: User | AnonymousUser
    teams_learn: QuerySet[Team] | None
    teams_review: QuerySet[Team] | None

    def __init__(self, user: User | AnonymousUser) -> None:
        self.user = user

    def get_teams_learn(self) -> QuerySet[Team] | None:
        """ Return teams where the user is a student """
        if isinstance(self.user, AnonymousUser):
            return None
        self.teams_learn = self.user.team_set.all()
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
    lessons = dict[Track, QuerySet[Lesson]]
    challenges = dict[Track, QuerySet[Challenge]]

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
            enrollments__in=[self.enrollment]).last()
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
        self.lessons = {track: self.week.lessons.filter(
            track=track) for track in self.tracks}        # type: ignore
        """
        for "type: ignore": I don't know how to resolve it:
        --------------------------------------------------------------
        mypy: learn/meta.py:104: error: Incompatible types in assignment
        (expression has type "dict[Track, _QuerySet[Lesson, Lesson]]",
        variable has type "type[dict[Any, Any]]")  [assignment]
        --------------------------------------------------------------
        """

    def get_challenges_from_week(self) -> None:
        self.challenges = {track: self.week.challenges.filter(
            track=track) for track in self.tracks}              # type: ignore
        """
        for "type: ignore": I don't know how to resolve it:
        --------------------------------------------------------------------
        mypy: learn/meta.py:116: error: Incompatible types in assignment
        (expression has type "dict[Track, _QuerySet[Challenge, Challenge]]",
        variable has type "type[dict[Any, Any]]")  [assignment]
        --------------------------------------------------------------------
        """
