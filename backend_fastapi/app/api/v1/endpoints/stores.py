from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import encrypt_secret
from app.db.session import get_db
from app.models.entities import ApiCredential, MarketplaceStore, SyncJob, SyncStatus, User
from app.schemas.store import StoreCreateIn, StoreCredentialsUpdateIn, StoreOut, StoreUpdateIn
from app.services.marketplaces import get_marketplace_client
from app.services.sync import enqueue_initial_sync

router = APIRouter(prefix='/stores', tags=['stores'])


@router.get('', response_model=list[StoreOut])
def list_stores(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(MarketplaceStore)
        .where(MarketplaceStore.user_id == current_user.id, MarketplaceStore.is_enabled.is_(True))
        .order_by(MarketplaceStore.id.desc())
    ).all()
    return rows


@router.post('', response_model=StoreOut)
def create_store(
    payload: StoreCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_store = db.scalar(
        select(MarketplaceStore).where(
            MarketplaceStore.user_id == current_user.id,
            MarketplaceStore.marketplace == payload.marketplace,
            MarketplaceStore.name == payload.name,
            MarketplaceStore.is_enabled.is_(True),
        )
    )
    if existing_store:
        raise HTTPException(status_code=409, detail='Store with same name and marketplace already exists')

    store = MarketplaceStore(
        user_id=current_user.id,
        name=payload.name,
        marketplace=payload.marketplace,
        connection_status='checking',
    )
    db.add(store)
    db.flush()

    for key_name, value in payload.credentials.items():
        db.add(ApiCredential(store_id=store.id, key_name=key_name, encrypted_value=encrypt_secret(value)))

    client = get_marketplace_client(payload.marketplace)
    check = client.check_connection(payload.credentials)
    if not check.success:
        db.rollback()
        raise HTTPException(status_code=400, detail=check.message)

    store.connection_status = 'connected'
    sync_job = SyncJob(store_id=store.id, job_type='initial_sync', status=SyncStatus.pending)
    db.add(sync_job)
    db.commit()
    db.refresh(store)

    job_id = enqueue_initial_sync(store.id)
    sync_job.details = {'queue_job_id': job_id}
    db.commit()
    return store


@router.patch('/{store_id}', response_model=StoreOut)
def update_store(
    store_id: int,
    payload: StoreUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = db.scalar(
        select(MarketplaceStore).where(
            MarketplaceStore.id == store_id,
            MarketplaceStore.user_id == current_user.id,
        )
    )
    if not store:
        raise HTTPException(status_code=404, detail='Store not found')

    if payload.name is not None:
        store.name = payload.name
    if payload.is_enabled is not None:
        store.is_enabled = payload.is_enabled
    db.commit()
    db.refresh(store)
    return store


@router.patch('/{store_id}/credentials', response_model=StoreOut)
def update_store_credentials(
    store_id: int,
    payload: StoreCredentialsUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = db.scalar(
        select(MarketplaceStore).where(
            MarketplaceStore.id == store_id,
            MarketplaceStore.user_id == current_user.id,
            MarketplaceStore.is_enabled.is_(True),
        )
    )
    if not store:
        raise HTTPException(status_code=404, detail='Store not found')

    client = get_marketplace_client(store.marketplace)
    check = client.check_connection(payload.credentials)
    if not check.success:
        raise HTTPException(status_code=400, detail=check.message)

    db.query(ApiCredential).filter(ApiCredential.store_id == store.id).delete()
    for key_name, value in payload.credentials.items():
        db.add(ApiCredential(store_id=store.id, key_name=key_name, encrypted_value=encrypt_secret(value)))

    store.connection_status = 'connected'
    db.commit()
    db.refresh(store)
    return store


@router.delete('/{store_id}', status_code=204)
def delete_store(
    store_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = db.scalar(
        select(MarketplaceStore).where(
            MarketplaceStore.id == store_id,
            MarketplaceStore.user_id == current_user.id,
            MarketplaceStore.is_enabled.is_(True),
        )
    )
    if not store:
        raise HTTPException(status_code=404, detail='Store not found')

    store.is_enabled = False
    db.commit()
    return Response(status_code=204)
