# CANON MAP (PHASE 0)

| Domain | Anchor(s) | Notes |
|---|---|---|
| Tags | B03 | Namespaces and references map to strict validation later. |
| Items | B04 | Item IDs and tag links governed by canonical references. |
| Loot | B24 | Coffers/pools/row ordering and mapping coverage invariants. |
| Recipes | B21 | Strict ration craft rules and deterministic slot semantics. |
| Quests | B18 | Archive delivery objective and reward-via-coffer constraints. |
| POI | B20 | Option requires `loot_coffer_id`, open-once behavior. |
| Luck | B22 | Bonus pool limits by item class (no equip/weapon/armor). |
| RNG | B14 | Keyed deterministic RNG only, no ambient entropy. |
| Idempotency | B14 | Event-based replay safety and stable deterministic outputs. |

## Must-have anchors checklist
- B21
- B24
- B18
- B20
- B22
- B14
- B03
- B04
