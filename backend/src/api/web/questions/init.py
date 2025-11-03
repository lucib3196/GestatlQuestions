from .crud import router as qcrud_router
from .files import router as qfile_router
from .sync import router as sync_router


routes = [qcrud_router, qfile_router, sync_router]