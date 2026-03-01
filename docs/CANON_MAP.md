# CANON MAP (Stage C verified)

| Domain | Anchor(s) | Notes |
|---|---|---|
| Tags | `B03`, `B03.EVENT_ID_AND_ORDERING` | Stable event ordering and deterministic IDs for canonical references. |
| Items | `B14` | Inventory/item domain and item-centric runtime contracts. |
| Loot | `B24`, `B24.LOOT.CANON.01` | LOOT/COFFER/POOLS canonical algorithm and data shape. |
| Recipes | `B21` | Field ration recipes: strict slots/time and deterministic craft constraints. |
| Quests | `B18` | Archive objective and reward-via-coffer constraints. |
| POI | `B20` | POI interaction contract requiring loot coffer linkage. |
| Luck | `B22`, `B22.LUCK.CANON.03` | LUCK effects and constraints for bonus loot slots. |
| RNG | `B03.RNG_STATE_POLICY`, `B04.FIXED_POINT` | Keyed deterministic RNG policy and integer-only probability math. |
| Idempotency | `B03.EVENT_ID_AND_ORDERING` | `applied_event_ids` and stable event ordering for replay/idempotency. |

## Must-have anchors checklist
- B21
- B24
- B18
- B20
- B22
- B14
- B03
- B04
