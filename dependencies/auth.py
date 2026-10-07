from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from models.user import User, UserRole


# --------------------------------------------------
# Swagger / OpenAPI Bearer Authentication
# --------------------------------------------------


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


# --------------------------------------------------
# Get Current Authenticated User
# --------------------------------------------------

def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> User:

    user = getattr(
        request.state,
        "current_user",
        None
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user


# --------------------------------------------------
# RBAC
# --------------------------------------------------

def require_role(*roles: UserRole):

    def checker(
        current_user: User = Depends(
            get_current_user
        )
    ) -> User:

        if current_user.role not in roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return checker