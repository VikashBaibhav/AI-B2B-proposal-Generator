"""
Infrastructure — In-Memory Proposal Repository

Development/testing implementation of ProposalRepository.
Replace with a database-backed implementation (SQLite, PostgreSQL) for production.
"""
from typing import Optional
from domain.entities.proposal import Proposal
from domain.interfaces.proposal_repository import ProposalRepository


class InMemoryProposalRepository(ProposalRepository):
    """
    Thread-unsafe in-memory store — suitable for development and unit tests only.
    
    For production, create a SQLAlchemyProposalRepository or similar class
    that implements the same ProposalRepository interface.
    """

    def __init__(self) -> None:
        self._store: dict[str, Proposal] = {}

    async def save(self, proposal: Proposal) -> Proposal:
        self._store[proposal.proposal_id] = proposal
        return proposal

    async def get_by_id(self, proposal_id: str) -> Optional[Proposal]:
        return self._store.get(proposal_id)

    async def list_all(self) -> list[Proposal]:
        return list(self._store.values())

    async def delete(self, proposal_id: str) -> bool:
        if proposal_id in self._store:
            del self._store[proposal_id]
            return True
        return False
