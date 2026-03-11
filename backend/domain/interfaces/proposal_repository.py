"""
Domain Interface — Proposal Repository (Abstract)

Defines the contract for persisting and retrieving proposals.
Swap between in-memory, SQLite, PostgreSQL, etc. without touching business logic.
"""
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.proposal import Proposal


class ProposalRepository(ABC):
    """Abstract repository for Proposal persistence."""

    @abstractmethod
    async def save(self, proposal: Proposal) -> Proposal:
        """Persist a proposal and return the saved instance."""
        ...

    @abstractmethod
    async def get_by_id(self, proposal_id: str) -> Optional[Proposal]:
        """Retrieve a proposal by its unique ID. Returns None if not found."""
        ...

    @abstractmethod
    async def list_all(self) -> list[Proposal]:
        """Return all stored proposals."""
        ...

    @abstractmethod
    async def delete(self, proposal_id: str) -> bool:
        """Delete a proposal by ID. Returns True if deleted, False if not found."""
        ...
