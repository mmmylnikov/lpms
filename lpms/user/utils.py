from typing import Never
import inspect

from github import Github
from github.Auth import Auth, Token
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.PullRequestReview import PullRequestReview
from github.GithubException import UnknownObjectException

from config.settings import GITHUB_API_TOKEN, DEBUG


class GithubApi:
    api: Github
    _api_token: str | None
    _auth: Auth | None
    rate_request: int
    rate_request_before: int
    rate_limit: int
    rate_reset_time: int

    def __init__(self) -> None:
        self._api_token = GITHUB_API_TOKEN
        self._set_auth()
        self.rate_request = 0
        self.rate_request_before = 0
        self.rate_limit = 0

    def _set_auth(self) -> None:
        if self._api_token:
            self._auth = Token(self._api_token)

    def _connect(self) -> None:
        if self._auth:
            self.api = Github(auth=self._auth)
        else:
            self.api = Github()
        self._rate_limiting()

    def _disconnect(self) -> None:
        if DEBUG:
            rate_cost = self.rate_request_before - self.rate_request
            current_frame = inspect.currentframe()
            if current_frame:
                outer_frame = current_frame.f_back
            if outer_frame:
                caller_function_name = outer_frame.f_code.co_name
                output = f"{caller_function_name}: "
                output += f"{rate_cost} ({self.rate_request})"
                print(output)  # noqa: T201
        self.api.close()

    def _rate_limiting(self) -> None:
        self.rate_request_before = self.rate_request
        self.rate_request, self.rate_limit = self.api.rate_limiting

    def get_repos_from_user(self, login: str) -> list[Repository]:
        self._connect()
        user = self.api.get_user(login=login)
        repos = list(user.get_repos())
        self._rate_limiting()
        self._disconnect()
        return repos

    def get_pulls_from_repo(self,
                            full_name_or_id: int | str) -> list[PullRequest]:
        self._connect()
        repo = self.api.get_repo(full_name_or_id=full_name_or_id)
        pulls = list(repo.get_pulls(state='all'))
        self._rate_limiting()
        self._disconnect()
        return pulls

    def get_pr_by_url(
        self, url: str
    ) -> (
        list[PullRequestReview]
        | PaginatedList[PullRequestReview]
        | list[Never]
    ):
        self._connect()
        items = url.split('/')
        repo_fullname = f'{items[3]}/{items[4]}'
        pull_num = int(items[6])
        repo = None
        pr = None
        reviews: (
            PaginatedList[PullRequestReview]
            | list[PullRequestReview]
            | list[Never]
        ) = []
        try:
            repo = self.api.get_repo(repo_fullname)
        except UnknownObjectException:
            repo = None
            reviews = []
        if repo:
            try:
                pr = repo.get_pull(pull_num)
            except UnknownObjectException:
                pr = None
        else:
            pr = None
        if pr:
            reviews = pr.get_reviews()
            commits = pr.get_commits()
            last_commit = commits[commits.totalCount-1]
            reviews = [
                review
                for review in reviews
                if review.submitted_at > last_commit.commit.committer.date
            ]
        self._rate_limiting()
        self._disconnect()
        return reviews
