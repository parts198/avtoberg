from django.db import transaction
from .models import Product, ProductGroup, OfferCandidate

def normalize_offer(offer_id: str) -> str:
    return offer_id.replace('-', '').lower()

def find_candidates(user, offer_id):
    norm = normalize_offer(offer_id)
    return Product.objects.filter(store__user=user).extra(where=["REPLACE(LOWER(offer_id), '-', '') = %s"], params=[norm])

@transaction.atomic
def confirm_group(user, offer_ids):
    products = Product.objects.select_for_update().filter(store__user=user, offer_id__in=offer_ids)
    group, _ = ProductGroup.objects.get_or_create(user=user, name=f"Группа {offer_ids[0]}")
    group.confirmed = True
    group.save()
    for product in products:
        product.product_group = group
        product.save(update_fields=['product_group'])
    return group

@transaction.atomic
def propose_candidate(user, source_offer, target_offer):
    return OfferCandidate.objects.get_or_create(user=user, source_offer_id=source_offer, target_offer_id=target_offer)[0]
