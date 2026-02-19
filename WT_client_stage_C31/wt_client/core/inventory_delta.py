from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence


@dataclass(frozen=True)
class InventoryDeltaError(ValueError):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


def _ensure_inventory_doc(state: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    inv = state.get("inventory")
    if inv is None:
        inv = {}
        state["inventory"] = inv
    if not isinstance(inv, dict):
        raise InventoryDeltaError("state.inventory: expected object")
    return inv


def _ensure_items_list(inv: MutableMapping[str, Any]) -> List[Dict[str, Any]]:
    items = inv.get("items")
    if items is None:
        items = []
        inv["items"] = items
    if not isinstance(items, list):
        raise InventoryDeltaError("inventory.items: expected list")
    return items  # type: ignore[return-value]


def build_add_instances(
    instances: Sequence[Mapping[str, Any]],
    *,
    container_id: str = "BAG_MAIN",
    origin: Optional[Mapping[str, Any]] = None,
    where: str = "inventory",
) -> List[Dict[str, Any]]:
    """Normalize minimal item instance payloads into inventory instance objects.

    Expected minimal input per instance: {instance_id, item_id, qty}
    Adds location + origin blocks (if provided).
    """

    out: List[Dict[str, Any]] = []
    for i, it in enumerate(instances):
        if not isinstance(it, Mapping):
            raise InventoryDeltaError(f"instances[{i}]: expected object")
        iid = it.get("instance_id")
        item_id = it.get("item_id")
        qty = it.get("qty")
        if not isinstance(iid, str) or not iid:
            raise InventoryDeltaError(f"instances[{i}].instance_id: expected non-empty str")
        if not isinstance(item_id, str) or not item_id:
            raise InventoryDeltaError(f"instances[{i}].item_id: expected non-empty str")
        if not isinstance(qty, int) or qty < 1:
            raise InventoryDeltaError(f"instances[{i}].qty: expected int >= 1")

        inst: Dict[str, Any] = {
            "instance_id": iid,
            "item_id": item_id,
            "qty": int(qty),
            "location": {"where": where, "container_id": container_id},
        }
        if origin is not None:
            inst["origin"] = dict(origin)
        out.append(inst)
    return out


def apply_add_instances(state: MutableMapping[str, Any], instances: Sequence[Mapping[str, Any]]) -> int:
    """Apply inventory add-instance delta to GameState.

    This is intentionally minimal and forward-compatible:
    - stores full instance dicts as-is
    - does not attempt stacking/merging (no new mechanics)
    """

    inv = _ensure_inventory_doc(state)
    items = _ensure_items_list(inv)
    before = len(items)
    for it in instances:
        if not isinstance(it, Mapping):
            raise InventoryDeltaError("apply_add_instances: each instance must be an object")
        items.append(copy.deepcopy(dict(it)))
    return len(items) - before


def count_item_qty(state: Mapping[str, Any]) -> Dict[str, int]:
    """Return total qty per item_id across all item instances in inventory."""
    inv = state.get("inventory")
    if not isinstance(inv, dict):
        return {}
    items = inv.get("items")
    if not isinstance(items, list):
        return {}
    out: Dict[str, int] = {}
    for it in items:
        if not isinstance(it, Mapping):
            continue
        item_id = it.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            continue
        qty = it.get("qty")
        q = int(qty) if isinstance(qty, int) else 1
        if q < 1:
            continue
        out[item_id] = out.get(item_id, 0) + q
    return out


def consume_item_qty(
    state: MutableMapping[str, Any],
    *,
    item_id: str,
    qty: int,
) -> List[Dict[str, Any]]:
    """Consume qty of a given item_id from inventory instances.

    Returns list of removal records: {instance_id, item_id, qty}
    Deterministic: consumes instances in sorted(instance_id) order.
    """
    if not isinstance(item_id, str) or not item_id:
        raise InventoryDeltaError("consume_item_qty: item_id must be non-empty string")
    need = int(qty)
    if need < 1:
        return []

    inv = _ensure_inventory_doc(state)
    items = _ensure_items_list(inv)

    # collect candidate indices
    idxs: List[int] = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        if it.get("item_id") == item_id:
            idxs.append(i)
    # stable order by instance_id
    idxs.sort(key=lambda i: str(items[i].get("instance_id", "")))

    removed: List[Dict[str, Any]] = []
    for i in idxs:
        if need <= 0:
            break
        it = items[i]
        if not isinstance(it, dict):
            continue
        iid = it.get("instance_id")
        if not isinstance(iid, str) or not iid:
            continue
        q = it.get("qty")
        cur = int(q) if isinstance(q, int) else 1
        if cur < 1:
            continue
        take = min(cur, need)
        need -= take
        new_q = cur - take
        if new_q <= 0:
            it["qty"] = 0
        else:
            it["qty"] = new_q
        removed.append({"instance_id": iid, "item_id": item_id, "qty": int(take)})

    if need > 0:
        raise InventoryDeltaError(f"inventory: недостаточно '{item_id}' (need {qty})")

    # purge zero-qty
    def _qty_nonpos(x: Any) -> bool:
        if not isinstance(x, dict):
            return False
        qv = x.get("qty")
        if isinstance(qv, int):
            return qv <= 0
        # non-int qty is treated as 1 and kept
        return False

    inv["items"] = [it for it in items if not _qty_nonpos(it)]
    return removed
