import logging

from fastapi import APIRouter, Depends, HTTPException, Query
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
logger = logging.getLogger(__name__)


@router.get('', response_model=list[StoreOut])
def list_stores(
    include_disabled: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(MarketplaceStore).where(MarketplaceStore.user_id == current_user.id)
    if not include_disabled:
        query = query.where(MarketplaceStore.is_enabled.is_(True))
    rows = db.scalars(query.order_by(MarketplaceStore.id.desc())).all()
    return rows


@router.post('', response_model=StoreOut)
def create_store(
    payload: StoreCreateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        duplicate = db.scalar(
            select(MarketplaceStore).where(
                MarketplaceStore.user_id == current_user.id,
                MarketplaceStore.name == payload.name,
                MarketplaceStore.marketplace == payload.marketplace,
                MarketplaceStore.is_enabled.is_(True),
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail='Active store with this name and marketplace already exists',
            )

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
        db.refresh(sync_job)

        try:
            job_id = enqueue_initial_sync(store.id)
            sync_job.details = {'queue_job_id': job_id}
            db.commit()
        except Exception as enqueue_exc:  # noqa: BLE001
            logger.exception('Failed to enqueue initial sync for store_id=%s: %s', store.id, enqueue_exc)
            sync_job.status = SyncStatus.failed
            sync_job.details = {'error': str(enqueue_exc)}
            db.commit()
            raise HTTPException(
                status_code=503,
                detail='Store connected, but failed to enqueue initial sync. Check Redis/worker.',
            )

        return store
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.exception('create_store failed user_id=%s marketplace=%s: %s', current_user.id, payload.marketplace, exc)
        raise HTTPException(status_code=500, detail='Failed to create store')


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
        )
    )
    if not store:
        raise HTTPException(status_code=404, detail='Store not found')

    try:
        rows = db.scalars(select(ApiCredential).where(ApiCredential.store_id == store.id)).all()
        for row in rows:
            if row.key_name in payload.credentials:
                row.encrypted_value = encrypt_secret(payload.credentials[row.key_name])

        existing_keys = {row.key_name for row in rows}
        for key_name, value in payload.credentials.items():
            if key_name not in existing_keys:
                db.add(ApiCredential(store_id=store.id, key_name=key_name, encrypted_value=encrypt_secret(value)))

        client = get_marketplace_client(store.marketplace)
        check = client.check_connection(payload.credentials)
        if not check.success:
            store.connection_status = f'failed: {check.message}'
            db.commit()
            raise HTTPException(status_code=400, detail=check.message)

        store.connection_status = 'connected'
        sync_job = SyncJob(store_id=store.id, job_type='initial_sync', status=SyncStatus.pending)
        db.add(sync_job)
        db.commit()
        db.refresh(sync_job)

        try:
            job_id = enqueue_initial_sync(store.id)
            sync_job.details = {'queue_job_id': job_id}
            db.commit()
        except Exception as enqueue_exc:  # noqa: BLE001
            logger.exception('Failed to enqueue re-sync for store_id=%s: %s', store.id, enqueue_exc)
            sync_job.status = SyncStatus.failed
            sync_job.details = {'error': str(enqueue_exc)}
            db.commit()
            raise HTTPException(
                status_code=503,
                detail='Credentials updated, but failed to enqueue sync. Check Redis/worker.',
            )

        db.refresh(store)
        return store
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.exception('update_store_credentials failed store_id=%s user_id=%s: %s', store_id, current_user.id, exc)
        raise HTTPException(status_code=500, detail='Failed to update store credentials')


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


@router.delete('/{store_id}')
def delete_store(
    store_id: int,
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

    store.is_enabled = False
    db.commit()
    return {'ok': True}
