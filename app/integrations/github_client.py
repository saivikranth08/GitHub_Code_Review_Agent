from github import Github
from github.PullRequest import PullRequest
import httpx
from app.config import settings
import structlog

logger = structlog.get_logger()


class GithubClient:
    """
    Wrapper around PyGithub for interacting with the GitHub API.
    Handles fetching PR diffs and posting review comments.
    """
    
    def __init__(self):
        # Authenticate using the token from .env
        self.client = Github(settings.github_token)

    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """
        Fetches the raw `.diff` file for a given Pull Request.
        PyGithub doesn't natively fetch raw diff text easily, so we use httpx
        with the appropriate Accept header, using our token for auth.
        """
        logger.info("fetching_pr_diff", repo=repo_full_name, pr_number=pr_number)
        
        # GitHub API endpoint for a specific Pull Request
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        
        headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3.diff"  # CRITICAL: asks GitHub for the raw diff string
        }
        
        # We use a synchronous request here because Celery workers handle blocking I/O fine
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            diff_text = response.text
            logger.info("fetched_pr_diff_success", repo=repo_full_name, pr_number=pr_number, diff_length=len(diff_text))
            return diff_text

    def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str) -> None:
        """
        Posts a standard issue comment on the Pull Request.
        """
        logger.info("posting_pr_comment", repo=repo_full_name, pr_number=pr_number)
        
        repo = self.client.get_repo(repo_full_name)
        pr: PullRequest = repo.get_pull(pr_number)
        
        # We post an issue comment rather than an inline review comment for now
        pr.create_issue_comment(body)
        logger.info("posted_pr_comment_success", repo=repo_full_name, pr_number=pr_number)
