"""Get Active Bonfires Interactor.

This module implements the business logic for retrieving active bonfires.
"""

from app.domain.constants import LOG_EVENTS
from app.domain.repository.bonfire_repository import IBonfireRepository
from app.usecase.get_bonfires.interface import (
    BonfireDTO,
    GetActiveBonfiresOutput,
    IGetActiveBonfiresUseCase,
)
from app.usecase.ports.logger import ILogger


class GetActiveBonfiresInteractor(IGetActiveBonfiresUseCase):
    """Interactor for retrieving active bonfires."""

    def __init__(
        self,
        bonfire_repository: IBonfireRepository,
        logger: ILogger,
    ) -> None:
        """Initialize the interactor.

        Args:
            bonfire_repository: Repository for bonfire operations
            logger: Logger for structured logging

        """
        self.bonfire_repository = bonfire_repository
        self.logger = logger

    async def execute(self, field_id: str) -> GetActiveBonfiresOutput:
        """Get all active bonfires.

        Returns:
            Output containing list of active bonfires

        """
        bonfires: list[BonfireDTO] = []

        async for bonfire in self.bonfire_repository.find_active_bonfires(field_id):
            bonfires.append(
                BonfireDTO(
                    id=bonfire.id,
                    spark_id=bonfire.spark_id,
                    field_id=bonfire.field_id,
                    content=bonfire.content,
                    unique_user_count=bonfire.unique_user_count,
                    heat_score=bonfire.heat_score,
                    created_at=bonfire.created_at,
                    decay_at=bonfire.decay_at,
                )
            )

        self.logger.info(
            LOG_EVENTS.BONFIRE_CREATED,  # Reusing event for retrieval
            "Active bonfires retrieved",
            context={"count": len(bonfires)},
        )

        return GetActiveBonfiresOutput(
            bonfires=bonfires,
            count=len(bonfires),
        )
