from github import Github
from github.Auth import Auth, Token
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.PullRequestReview import PullRequestReview

from config.settings import GITHUB_API_TOKEN


class GithubApi:
    api: Github
    _api_token: str | None
    _auth: Auth | None
    rate_request: int
    rate_limit: int
    rate_reset_time: int

    def __init__(self) -> None:
        self._api_token = GITHUB_API_TOKEN
        self._set_auth()

    def _set_auth(self) -> None:
        if self._api_token:
            self._auth = Token(self._api_token)

    def _connect(self) -> None:
        if self._auth:
            self.api = Github(auth=self._auth)
        else:
            self.api = Github()

    def _disconnect(self) -> None:
        self.api.close()

    def _rate_limiting(self) -> None:
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
        pulls = list(repo.get_pulls())
        self._rate_limiting()
        self._disconnect()
        return pulls

    def get_pr_by_url(self, url: str) -> list[PullRequestReview]:
        self._connect()
        items = url.split('/')
        repo_fullname = f'{items[3]}/{items[4]}'
        pull_num = int(items[6])
        repo = self.api.get_repo(repo_fullname)
        pr = repo.get_pull(pull_num)
        reviews = pr.get_reviews()
        self._rate_limiting()
        self._disconnect()
        return list(reviews)
