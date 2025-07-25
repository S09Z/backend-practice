from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from prisma import Prisma
from app.database import get_db
from app.core.security import verify_token

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: Prisma = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Implement your token verification logic here
    user = await verify_token(token.credentials, db)
    if user is None:
        raise credentials_exception
    return user