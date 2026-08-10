from uuid import UUID
from fastapi import HTTPException, status

from cx_contracts.common.actor import ActorContext


def verify_import_write_permission(actor: ActorContext, project_id: UUID | None = None) -> None:
    """Verify actor has imports:write permission and optional project scope access."""
    if "imports:write" not in actor.permissions and "*" not in actor.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: missing required permission 'imports:write'",
        )

    if project_id and actor.project_ids and project_id not in actor.project_ids:
        # Hide existence by returning 404 if outside authorized project scope
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found or outside authorized project scope",
        )


def verify_import_read_permission(actor: ActorContext, project_id: UUID | None = None) -> None:
    """Verify actor has imports:read permission and optional project scope access."""
    if (
        "imports:read" not in actor.permissions
        and "imports:write" not in actor.permissions
        and "*" not in actor.permissions
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: missing required permission 'imports:read'",
        )

    if project_id and actor.project_ids and project_id not in actor.project_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found or outside authorized project scope",
        )
