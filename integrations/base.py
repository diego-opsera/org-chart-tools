"""
Abstract base class for tool integrations.

Each integration fetches access data from a remote API and yields
AccessEntry objects that conform to the same schema as access.yaml.

To add a new integration:
1. Create integrations/<tool_id>.py
2. Subclass BaseIntegration
3. Set tool_id to match the key in access.yaml tools section
4. Implement fetch()

Future sync.py will call all registered integrations and merge their output
into access.yaml (or a separate access.generated.yaml).
"""

from abc import ABC, abstractmethod
from typing import Iterator, TypedDict


class AccessEntry(TypedDict):
    person_key: str       # "Last, First" — must match roster NAME column
    tool: str             # tool ID from access.yaml
    role: str             # role ID from access.yaml tool definition
    scope: str | None     # e.g. "project:PLATFORM", "account:prod", or None
    source: str           # e.g. "jira_api", "github_api"
    fetched_at: str       # ISO 8601 timestamp


class BaseIntegration(ABC):
    """Base class for all tool integrations."""

    tool_id: str  # Subclasses must set this to match access.yaml tools key

    @abstractmethod
    def fetch(self) -> Iterator[AccessEntry]:
        """
        Fetch current access grants from the remote API.
        Yields one AccessEntry per person-role-scope combination.
        """
        ...

    def fetch_all(self) -> list[AccessEntry]:
        """Convenience wrapper: collect all entries into a list."""
        return list(self.fetch())
