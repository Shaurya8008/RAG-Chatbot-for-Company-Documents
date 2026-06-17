"""
Permission service for role-based access control.
Filters documents and chunks based on user role before retrieval.
"""

import logging
from typing import List, Dict, Any, Optional

from app.models import UserRole, PermissionLevel

logger = logging.getLogger(__name__)

# Role → accessible permission levels mapping
ROLE_PERMISSIONS = {
    UserRole.EMPLOYEE: [PermissionLevel.ALL_EMPLOYEES],
    UserRole.MANAGER: [PermissionLevel.ALL_EMPLOYEES, PermissionLevel.MANAGERS_ONLY],
    UserRole.HR_ADMIN: [
        PermissionLevel.ALL_EMPLOYEES,
        PermissionLevel.MANAGERS_ONLY,
        PermissionLevel.HR_ONLY,
    ],
    UserRole.ADMIN: [
        PermissionLevel.ALL_EMPLOYEES,
        PermissionLevel.MANAGERS_ONLY,
        PermissionLevel.HR_ONLY,
        PermissionLevel.ADMIN_ONLY,
    ],
}


def get_allowed_permission_levels(role: UserRole) -> List[str]:
    """Get the list of permission levels accessible to a given role."""
    levels = ROLE_PERMISSIONS.get(role, [PermissionLevel.ALL_EMPLOYEES])
    return [level.value for level in levels]


def filter_chunks_by_permission(
    chunks: List[Dict[str, Any]],
    user_role: UserRole,
) -> List[Dict[str, Any]]:
    """
    Filter retrieved chunks based on user's role.
    This is the access control gate BEFORE generation.
    """
    allowed = get_allowed_permission_levels(user_role)
    filtered = []

    for chunk in chunks:
        chunk_permission = chunk.get("permission_level", "all_employees")
        if chunk_permission in allowed:
            filtered.append(chunk)
        else:
            logger.info(
                f"Access denied: User role '{user_role.value}' cannot access "
                f"chunk with permission '{chunk_permission}'"
            )

    return filtered


def can_access_document(user_role: UserRole, document_permission: str) -> bool:
    """Check if a user role can access a document with the given permission level."""
    allowed = get_allowed_permission_levels(user_role)
    return document_permission in allowed
