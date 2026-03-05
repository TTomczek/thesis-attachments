import os
from enum import Enum
from typing import Annotated, Optional, List

import jq
from mcp.types import TextContent, CallToolResult
from pydantic import Field, BaseModel
from server import mcp

from src.github_client.api.activity_api import ActivityApi
from src.github_client.api.issues_api import IssuesApi
from src.github_client.api.repos_api import ReposApi
from src.github_client.api_client import ApiClient
from src.github_client.configuration import Configuration
from src.github_client.models.branch_protection import BranchProtection
from src.github_client.models.issue import Issue
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

pat = os.environ.get("GITHUB_PAT")
if not pat:
    raise ValueError("GITHUB_PAT environment variable is required but not set")

config = Configuration(
    host="https://api.github.com"
)
api_client = ApiClient(
    configuration=config,
    header_name="Authorization",
    header_value=f"Bearer {pat}"
)
reposApi = ReposApi(api_client=api_client)
issuesApi = IssuesApi(api_client=api_client)
activityApi = ActivityApi(api_client=api_client)


class Sort(Enum):
    CREATED = "created"
    UPDATED = "updated"


class Direction(Enum):
    ASC = "asc"
    DESC = "desc"


class State(Enum):
    OPEN = "open"
    CLOSED = "closed"


class SimpleUser(BaseModel):
    """A GitHub user."""
    name: Optional[str | None]
    email: Optional[str | None]
    login: Annotated[str, Field(examples=["octocat"])]
    id: Annotated[str, Field(examples=["1"])]
    node_id: Annotated[Optional[str], Field(examples=["MDQ6VXNlcjE="])]
    avatar_url: Annotated[str, Field(examples=["https://github.com/images/error/octocat_happy.gif"])]
    gravatar_id: Annotated[str | None, Field(examples=["41d064eb2195891e12d0413f63227ea7"])]
    url: Annotated[str, Field(examples=["https://api.github.com/users/octocat"])]
    html_url: Annotated[str, Field(examples=["https://github.com/octocat"])]
    followers_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/followers"])]
    following_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/following{/other_user}"])]
    gists_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/gists{/gist_id}"])]
    starred_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/starred{/owner}{/repo}"])]
    subscriptions_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/subscriptions"])]
    organizations_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/orgs"])]
    repos_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/repos"])]
    events_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/events{/privacy}"])]
    received_events_url: Annotated[str, Field(examples=["https://api.github.com/users/octocat/received_events"])]
    type: Annotated[str, Field(examples=["User"])]
    site_admin: bool
    starred_at: Annotated[str, Field(examples=["'2020-07-09T00:17:55Z'"])]
    user_view_type: Annotated[Optional[str], Field(examples=["public"])]


class Milestone(BaseModel):
    """A collection of related issues and pull requests."""
    url: Annotated[str, Field(examples=["https://api.github.com/repos/octocat/Hello-World/milestones/1"])]
    html_url: Annotated[str, Field(examples=["https://github.com/octocat/Hello-World/milestones/v1.0"])]
    labels_url: Annotated[str, Field(examples=["https://api.github.com/repos/octocat/Hello-World/milestones/1/labels"])]
    id: Annotated[int, Field(examples=["1002604"])]
    node_id: Annotated[str, Field(examples=["MDk6TWlsZXN0b25lMTAwMjYwNA=="])]
    number: Annotated[int, Field(examples=["42"])]
    state: Annotated[State, Field(examples=[State.OPEN.value])]
    title: Annotated[str, Field(examples=["v1.0"])]
    description: Annotated[str | None, Field(examples=["Tracking milestone for version 1.0"])]
    creator: Annotated[SimpleUser | None, Field(examples=[""])]
    open_issues: Annotated[int, Field(examples=["4"])]
    closed_issues: Annotated[int, Field(examples=["8"])]
    created_at: Annotated[str, Field(examples=["2011-04-10T20:09:31Z"])]
    updated_at: Annotated[str, Field(examples=["2014-03-03T18:58:10Z"])]
    closed_at: Annotated[str | None, Field(examples=["2013-02-12T13:22:01Z"])]
    due_on: Annotated[str | None, Field(examples=["2012-10-09T23:39:01Z"])]


class StateReason(Enum):
    COMPLETED = "completed"
    NOT_PLANNED = "not_planned"
    REOPENED = "reopened"
    DUPLICATE = "duplicate"


class Label(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class PullRequest(BaseModel):
    merged_at: Optional[str] = None
    diff_url: Optional[str]
    html_url: Optional[str]
    patch_url: Optional[str]
    url: Optional[str]


@mcp.tool()
@rate_limit()
@sanitize_output()
async def issues_list_for_repo(owner: Annotated[
    str, Field(description="The account owner of the repository. The name is not case sensitive.")], repo: Annotated[
    str, Field(description="The name of the repository without the `.git` extension. The name is not case sensitive.")],
                               milestone: Annotated[Optional[Milestone], Field(
                                   description="A collection of related issues and pull requests.")] = None,
                               state: Annotated[Optional[State], Field(
                                   description="Indicates the state of the issues to return.")] = None,
                               assignee: Annotated[Optional[str], Field(
                                   description="Can be the name of a user. Pass in `none` for issues with no assigned user, and `*` for issues assigned to any user.")] = None,
                               issue_type: Annotated[Optional[str], Field(
                                   description="Can be the name of an issue type. If the string `*` is passed, issues with any type are accepted. If the string `none` is passed, issues without type are returned.")] = None,
                               creator: Annotated[
                                   Optional[str], Field(description="The user that created the issue.")] = None,
                               mentioned: Annotated[
                                   Optional[str], Field(description="A user that's mentioned in the issue.")] = None,
                               labels: Annotated[Optional[str], Field(
                                   description="A list of comma separated label names. Example: `bug,ui,@high`")] = None,
                               sort: Annotated[Optional[Sort], Field(
                                   description="The property to sort the results by.")] = Sort.CREATED,
                               since: Annotated[Optional[str], Field(
                                   description="Only show results that were last updated after the given time. This is a timestamp in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format: `YYYY-MM-DDTHH:MM:SSZ`.")] = None,
                               direction: Annotated[Optional[Direction], Field(
                                   description="The direction to sort the results by.")] = Direction.DESC,
                               per_page: Annotated[
                                   Optional[int], Field(description="The number of results per page (max 100).")] = 30,
                               page: Annotated[
                                   Optional[int], Field(description="The page number of the results to fetch.")] = 1,
                               jq_filter: Annotated[Optional[str], Field(
                                   description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """
    List issues in a repository. Only open issues will be listed.

        > [!NOTE]
        > GitHub's REST API considers every pull request an issue, but not every issue is a pull request. For this reason, "Issues" endpoints may return both issues and pull requests in the response. You can identify pull requests by the `pull_request` key. Be aware that the `id` of a pull request returned from "Issues" endpoints will be an _issue id_. To find out the pull request id, use the "[List pull requests](https://docs.github.com/rest/pulls/pulls#list-pull-requests)" endpoint.
    """
    nullsafe_state = state if state is None else state.value
    nullsafe_sort = sort if sort is None else sort.value
    nullsafe_direction = direction if direction is None else direction.value
    try:
        issues: List[Issue] = await issuesApi.issues_list_for_repo(owner=owner, repo=repo, milestone=milestone,
                                                                   state=nullsafe_state,
                                                                   assignee=assignee, type=issue_type, creator=creator,
                                                                   mentioned=mentioned, labels=labels,
                                                                   sort=nullsafe_sort,
                                                                   direction=nullsafe_direction, since=since,
                                                                   per_page=per_page,
                                                                   page=page)
        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([issue.model_dump(mode="json") for issue in issues]).all()
        else:
            return issues
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


class CreateIssueRequest(BaseModel):
    title: Annotated[str | int, Field(description="The title of the issue.")]
    body: Annotated[Optional[str], Field(description="The contents of the issue.")] = ""
    assignee: Annotated[Optional[str], Field(
        description="Login for the user that this issue should be assigned to. _NOTE: Only users with push access can set the assignee for new issues. The assignee is silently dropped otherwise. **This field is closing down.**_")] = None
    milestone: Annotated[Optional[int], Field(
        description="The `number` of the milestone to associate this issue with. _NOTE: Only users with push access can set the milestone for new issues. The milestone is silently dropped otherwise._")] = None
    labels: Annotated[Optional[List[str | Label]], Field(
        description="Labels to associate with this issue. _NOTE: Only users with push access can set labels for new issues. Labels are silently dropped otherwise._")] = None
    assignees: Annotated[Optional[List[str]], Field(
        description="Logins for Users to assign to this issue. _NOTE: Only users with push access can set assignees for new issues. Assignees are silently dropped otherwise._")] = []
    issue_type: Annotated[Optional[str], Field(
        description="The name of the issue type to associate with this issue. _NOTE: Only users with push access can set the type for new issues. The type is silently dropped otherwise._")] = None


@mcp.tool()
@rate_limit()
@sanitize_output()
async def issues_create(owner: Annotated[
    str, Field(description="The account owner of the repository. The name is not case sensitive.")], repo: Annotated[
    str, Field(description="The name of the repository without the `.git` extension. The name is not case sensitive.")],
                        issue: CreateIssueRequest,
                        jq_filter: Annotated[Optional[str], Field(
                            description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """
    Any user with pull access to a repository can create an issue. If [issues are disabled in the repository](https://docs.github.com/articles/disabling-issues/), the API returns a `410 Gone` status.

        This endpoint triggers [notifications](https://docs.github.com/github/managing-subscriptions-and-notifications-on-github/about-notifications). Creating content too quickly using this endpoint may result in secondary rate limiting. For more information, see "[Rate limits for the API](https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api#about-secondary-rate-limits)"
        and "[Best practices for using the REST API](https://docs.github.com/rest/guides/best-practices-for-using-the-rest-api)."
    """
    try:
        create_issue_request = {
            "title": {"actual_instance": issue.title},
            "body": issue.body,
            "milestone": issue.milestone,
            "labels": [{"actual_instance": label} for label in issue.labels],
            "assignees": issue.assignees,
            "type": issue.issue_type
        }
        created_issue = await issuesApi.issues_create(owner=owner, repo=repo,
                                                      issues_create_request=create_issue_request)
        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value(created_issue.model_dump(mode="json")).all()
        else:
            return created_issue
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def issues_list_labels_for_repo(owner: Annotated[
    str, Field(description="The account owner of the repository. The name is not case sensitive.")], repo: Annotated[
    str, Field(description="The name of the repository without the `.git` extension. The name is not case sensitive.")],
                                      per_page: Annotated[Optional[int], Field(
                                          description="The number of results per page (max 100).")] = 30,
                                      page: Annotated[Optional[int], Field(
                                          description="The page number of the results to fetch.")] = 1,
                                      jq_filter: Annotated[Optional[str], Field(
                                          description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """Lists all issue labels for a repository."""
    try:
        labels = await issuesApi.issues_list_labels_for_repo(owner=owner, repo=repo, per_page=per_page, page=page)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([label.model_dump(mode="json") for label in labels]).all()
        else:
            return labels
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


class Commit(BaseModel):
    sha: str
    url: str


class ShortBranch(BaseModel):
    """Short Branch"""
    name: str
    commit: Commit
    protected: bool
    protection: Optional[BranchProtection] = None
    protection_url: Optional[str]


@mcp.tool()
@rate_limit()
@sanitize_output()
async def repos_list_branches(owner: Annotated[
    str, Field(description="The account owner of the repository. The name is not case sensitive.")], repo: Annotated[
    str, Field(description="The name of the repository without the `.git` extension. The name is not case sensitive.")],
                              protected: Annotated[Optional[bool], Field(
                                  description="Setting to `true` returns only branches protected by branch protections or rulesets. When set to `false`, only unprotected branches are returned. Omitting this parameter returns all branches.")],
                              per_page: Annotated[
                                  Optional[int], Field(description="The number of results per page (max 100).")] = 30,
                              page: Annotated[
                                  Optional[int], Field(description="The page number of the results to fetch.")] = 1,
                              jq_filter: Annotated[Optional[str], Field(
                                  description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """List branches of a repository."""
    try:
        branches = await reposApi.repos_list_branches(owner=owner, repo=repo, protected=protected, per_page=per_page,
                                                      page=page)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([branch.model_dump(mode="json") for branch in branches]).all()
        else:
            return branches
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def repos_get_branch_protection(owner: Annotated[
    str, Field(description="The account owner of the repository. The name is not case sensitive.")], repo: Annotated[
    str, Field(description="The name of the repository without the `.git` extension. The name is not case sensitive.")],
                                      branch: Annotated[str, Field(
                                          description="The name of the branch. Cannot contain wildcard characters.")],
                                      jq_filter: Annotated[Optional[str], Field(
                                          description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """
    Get details of protection configured for the given branch.
    """
    try:
        protection = await reposApi.repos_get_branch_protection(owner=owner, repo=repo, branch=branch)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value(protection.model_dump(mode="json")).all()
        else:
            return protection
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def activity_list_repos_starred_by_authenticated_user(
        sort: Annotated[Optional[Sort], Field(description="The property to sort the results by.")] = Sort.CREATED,
        direction: Annotated[
            Optional[Direction], Field(description="The direction to sort the results by.")] = Direction.DESC,
        per_page: Annotated[Optional[int], Field(description="The number of results per page (max 100).")] = 30,
        page: Annotated[Optional[int], Field(description="The page number of the results to fetch.")] = 1,
        jq_filter: Annotated[Optional[str], Field(
            description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """
    Lists repositories the authenticated user has starred.
    """
    try:
        repos = await activityApi.activity_list_repos_starred_by_authenticated_user(sort=sort.value,
                                                                                    direction=direction.value,
                                                                                    per_page=per_page, page=page)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([repo.model_dump(mode="json") for repo in repos]).all()
        else:
            return repos
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
