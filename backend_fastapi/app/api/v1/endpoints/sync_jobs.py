from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MarketplaceStore, SyncJob, User

router = APIRouter(prefix='/sync-jobs', tags=['sync-jobs'])


@router.get('')
def list_sync_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    store_ids = db.scalars(select(MarketplaceStore.id).where(MarketplaceStore.user_id == current_user.id)).all()
    rows = db.scalars(select(SyncJob).where(SyncJob.store_id.in_(store_ids)).order_by(SyncJob.id.desc())).all()
    return [
        {
            'id': row.id,
            'store_id': row.store_id,
            'job_type': row.job_type,
            'status': row.status.value,
            'details': row.details,
            'created_at': row.created_at,
            'started_at': row.started_at,
            'finished_at': row.finished_at,
        }
        for row in rows
    ]
