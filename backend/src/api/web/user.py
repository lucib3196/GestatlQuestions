# --- Third-Party ---
from fastapi import APIRouter

# --- Internal ---
from src.api.models import UserBase
from src.api.service.user import UserManagerDependeny
from src.api.models.models import User
from src.api.core.logging import logger


router = APIRouter(prefix="/users", tags=["users"])
@router.post("/")
async def create_user(
    user_manager: UserManagerDependeny,
    data: UserBase,
) -> User:
    """
    Create a new user in the system.

    Args:
        user_manager (UserManagerDependeny): Dependency providing user management operations.
        data (UserBase): Incoming user registration data (email, fb_id, etc.).

    Returns:
        User: The newly created user object.
    """
    logger.info("Creating user with email='%s' and fb_id='%s'", data.email, data.fb_id)

    created_user = user_manager.create_user(
        uid=data.fb_id,
        email=data.email,
        username=data.email,
    )

    logger.info("User created successfully: uid='%s'", created_user.uid)
    return created_user


@router.get("/{id}")
async def get_user(
    user_manager: UserManagerDependeny,
    id: str,
) -> User:
    """
    Retrieve a user by their unique ID.

    Args:
        user_manager (UserManagerDependeny): User management service.
        id (str): The user ID to retrieve.

    Returns:
        User: The user with the specified ID.
    """
    logger.info("Fetching user with id='%s'", id)

    user = user_manager.get_user(id)

    logger.info("Retrieved user: uid='%s', email='%s'", user.uid, user.email)
    return user


@router.delete("/{id}")
async def delete_user(
    user_manager: UserManagerDependeny,
    id: str,
):
    """
    Delete a user by their ID.

    Args:
        user_manager (UserManagerDependeny): User management service.
        id (str): User ID to delete.

    Returns:
        dict: Success message.
    """
    logger.warning("Deleting user with id='%s'", id)

    user_manager.delete_user(id)

    logger.info("User successfully deleted: id='%s'", id)
    return {"detail": "user deleted"}


@router.put("/{id}")
async def update_user(
    user_manager: UserManagerDependeny,
    id: str,
    data: UserBase,
) -> User:
    """
    Update an existing user's information.

    Args:
        user_manager (UserManagerDependeny): User service handler.
        id (str): ID of the user to update.
        data (UserBase): Updated user information.

    Returns:
        User: The updated user object.
    """
    logger.info("Updating user id='%s' with new email='%s'", id, data.email)

    updated_user = user_manager.update_user(id, data)

    logger.info("User updated successfully: id='%s'", id)
    return updated_user
