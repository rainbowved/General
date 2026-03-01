# PARAM_REGISTRY (AUTO_EXTRACTED)

This registry is extracted from `Концепт_13` during AUTO_OPTIMIZE_CONCEPT_FOR_CHAT.
Rules:
- Do not treat inline examples as truth. For DATA params, the source of truth is DB_SPEC.
- Each entry includes a short evidence snippet and the anchor(s) where it was seen.
- Some entries are CANON constants (kept in text); marked by source_of_truth starting with `core/` or `CANON`.

Columns:
- param_id, domain, type, unit, constraints, value (if explicitly stated), source_of_truth, used_in (anchors), evidence.


| param_id | domain | type | unit | constraints | value | source_of_truth | used_in | evidence |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| ARMOR_PCT_CAP_MVP | COMBAT | INT |  | int; domain-specific |  | DB_SPEC/balance_combat | B08 | • ArmorPct_def:int — броня цели в процентных пунктах (0..100), но в MVP применяется с капом ARMOR_PCT_CAP_MVP (см. caps). |
| ARMOR_PEN_PCT_CAP_MVP | COMBAT | INT |  | int; domain-specific |  | DB_SPEC/balance_combat | B08 | • ArmorPenPct_atk:int — бронепробитие источника урона в процентных пунктах (0..ARMOR_PEN_PCT_CAP_MVP). |
| MISTFORM_HP_CAP_PER_ROUND | COMBAT | INT |  | int; domain-specific |  | DB_SPEC/balance_combat | B07, B08, B12 | Если цель под SPELL_MISTFORM: mistform_hp_taken_this_round:int (сброс в ROUND_START; используется для капа MISTFORM_HP_CAP_PER_ROUND). |
| BUY_MULT_BP | ECONOMY | BP | bp | int bp (0..?) |  | DB_SPEC/balance_economy | B10 | • Формулы (bp, без float): buy_mult_bp=BUY_MULT_BP; sell_mult_bp=SELL_MULT_BP. shop_buy_unit = max(0, apply_bp_floor(apply_bp_floor(P_ref, buy_mult_bp), VarBuy_bp)). shop_sell_unit = max(1, apply_bp_c |
| BUY_MULT_EXCH_BP | ECONOMY | BP | bp | int bp (0..?) | 5000 | DB_SPEC/balance_economy | B10 | • SHOP_EXCHANGE defaults: BUY_MULT_EXCH_BP:int (def=5000); SELL_MULT_EXCH_BP:int (def=14000); FEE_EXCH_BP:int (def=500). |
| DEFAULT_REPEATABLE_COOLDOWN_SEC | ECONOMY | SEC | sec | int sec >=0 | 86400 | DB_SPEC/balance_economy | B10 | [DATA] Константы: N_OFFERS=6, MAX_ACTIVE_CONTRACTS=3, DEFAULT_OFFER_TTL_DAYS=3, DEFAULT_REPEATABLE_COOLDOWN_SEC=86400. |
| DEPOSIT_FRAC_BP | ECONOMY | BP | bp | int bp (0..?) | 2000 | DB_SPEC/balance_economy | B10, B18 | [DATA] Депозит контракта (анти-абуз и sink): deposit_cu = ceil_div(reward_cu * DEPOSIT_FRAC_BP, 10000), DEPOSIT_FRAC_BP=2000 (20%); списывается при QUEST_TAKE; возвращается только при QUEST_COMPLETE; |
| FEE_EXCH_BP | ECONOMY | BP | bp | int bp (0..?) | 500 | DB_SPEC/balance_economy | B10 | • SHOP_EXCHANGE defaults: BUY_MULT_EXCH_BP:int (def=5000); SELL_MULT_EXCH_BP:int (def=14000); FEE_EXCH_BP:int (def=500). |
| HEAL_BASE_CU | ECONOMY | CU_INT | cu | int; domain-specific |  | DB_SPEC/balance_economy | B10 | • Цена за статус: cost_one = apply_bp_ceil(apply_bp_floor(HEAL_BASE_CU, TierFactor_bp(access_tier)), SeverityFactor_bp(severity)). [DATA] HEAL_BASE_CU, TierFactor_bp(tier), SeverityFactor_bp(severity) |
| IDENTIFY_FEE_MULT_BP | ECONOMY | BP | bp | int bp (0..?) |  | DB_SPEC/balance_economy | B10 | • Цена: cost=max(IDENTIFY_MIN_CU, ceil_div(P_ref(item) * IDENTIFY_FEE_MULT_BP, 10000)). [DATA] IDENTIFY_FEE_MULT_BP и IDENTIFY_MIN_CU задаются в DB_SPEC/balance. |
| IDENTIFY_MIN_CU | ECONOMY | CU_INT | cu | int; domain-specific |  | DB_SPEC/balance_economy | B10 | • Цена: cost=max(IDENTIFY_MIN_CU, ceil_div(P_ref(item) * IDENTIFY_FEE_MULT_BP, 10000)). [DATA] IDENTIFY_FEE_MULT_BP и IDENTIFY_MIN_CU задаются в DB_SPEC/balance. |
| K_SCARCITY_BP | ECONOMY | BP | bp | int bp (0..?) | 3500 | DB_SPEC/balance_economy | B10 | • K_SCARCITY_BP:int (def=3500); S_MIN_BP:int (def=8500); S_MAX_BP:int (def=13500). |
| OVERSTOCK_CAP | ECONOMY | INT |  | int; >=0 | 2 | DB_SPEC/balance_economy | B10 | • OVERSTOCK_CAP:int (def=2). |
| REPAIR_MAP_FRAC_BP | ECONOMY | BP | bp | int bp (0..?) |  | DB_SPEC/balance_economy | B10 | • Цена: для repair_map cost=max(SERVICE_MIN_COST_CU, ceil_div(P_ref(intact) * REPAIR_MAP_FRAC_BP, 10000)); для repair_yield cost=max(SERVICE_MIN_COST_CU, ceil_div(sum(P_ref(mat) * qty) * REPAIR_YIELD_ |
| REPAIR_YIELD_FRAC_BP | ECONOMY | BP | bp | int bp (0..?) |  | DB_SPEC/balance_economy | B10 | • Цена: для repair_map cost=max(SERVICE_MIN_COST_CU, ceil_div(P_ref(intact) * REPAIR_MAP_FRAC_BP, 10000)); для repair_yield cost=max(SERVICE_MIN_COST_CU, ceil_div(sum(P_ref(mat) * qty) * REPAIR_YIELD_ |
| SELL_MULT_BP | ECONOMY | BP | bp | int bp (0..?) |  | DB_SPEC/balance_economy | B10 | • Формулы (bp, без float): buy_mult_bp=BUY_MULT_BP; sell_mult_bp=SELL_MULT_BP. shop_buy_unit = max(0, apply_bp_floor(apply_bp_floor(P_ref, buy_mult_bp), VarBuy_bp)). shop_sell_unit = max(1, apply_bp_c |
| SELL_MULT_EXCH_BP | ECONOMY | BP | bp | int bp (0..?) | 14000 | DB_SPEC/balance_economy | B10 | • SHOP_EXCHANGE defaults: BUY_MULT_EXCH_BP:int (def=5000); SELL_MULT_EXCH_BP:int (def=14000); FEE_EXCH_BP:int (def=500). |
| SERVICE_MIN_COST_CU | ECONOMY | CU_INT | cu | int; domain-specific |  | DB_SPEC/balance_economy | B10 | • Цена: для repair_map cost=max(SERVICE_MIN_COST_CU, ceil_div(P_ref(intact) * REPAIR_MAP_FRAC_BP, 10000)); для repair_yield cost=max(SERVICE_MIN_COST_CU, ceil_div(sum(P_ref(mat) * qty) * REPAIR_YIELD_ |
| S_MAX_BP | ECONOMY | BP | bp | int bp (0..?) | 13500 | DB_SPEC/balance_economy | B10 | • K_SCARCITY_BP:int (def=3500); S_MIN_BP:int (def=8500); S_MAX_BP:int (def=13500). |
| S_MIN_BP | ECONOMY | BP | bp | int bp (0..?) | 8500 | DB_SPEC/balance_economy | B10 | • K_SCARCITY_BP:int (def=3500); S_MIN_BP:int (def=8500); S_MAX_BP:int (def=13500). |
| V_ITEM_BP | ECONOMY | BP | bp | int bp (0..?) | 200 | DB_SPEC/balance_economy | B10 | • V_MARKET_BP:int (def=400); V_ITEM_BP:int (def=200). |
| V_MARKET_BP | ECONOMY | BP | bp | int bp (0..?) | 400 | DB_SPEC/balance_economy | B10 | • V_MARKET_BP:int (def=400); V_ITEM_BP:int (def=200). |
| ESCAPE_DISTANCE_M | GEOMETRY | METER_INT | m | int; domain-specific |  | DB_SPEC/TBD | B06, B07 | • ESCAPE_DISTANCE_M и прочие проверки дистанции используют тот же distance_m (см. COMBAT_END). |
| FAT_AWAKE_RATE_MULT_PCT | HOME | INT |  | int; domain-specific |  | DB_SPEC/balance_home | B23 | Эффект задаётся как FAT_AWAKE_RATE_MULT_PCT (в [DATA], применяется как bp). |
| HOME_RESTED_DURATION_SEC | HOME | SEC | sec | int sec >=0 |  | DB_SPEC/balance_home | B23 | установить/обновить rested_status.time_left_sec = HOME_RESTED_DURATION_SEC |
| HOME_LUCK_CAP_PCT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | LuckHomeMultBp = clamp_bp(10000 + (HOME_LUCK_MULT_PCT + RESTED_LUCK_MULT_PCT)*100, 10000, 10000 + HOME_LUCK_CAP_PCT*100) |
| HOME_LUCK_MULT_PCT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | LuckHomeMultBp = clamp_bp(10000 + (HOME_LUCK_MULT_PCT + RESTED_LUCK_MULT_PCT) * 100, ...) |
| LUCK_ARROW_RECOVER_STEP_BP_PER_POINT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | - chance_bp = clamp_int(base_chance_bp + luck_misc * LUCK_ARROW_RECOVER_STEP_BP_PER_POINT, 0, 10000). |
| LUCK_MISC_CAP_STAT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | - luck_misc = clamp_int(max(actor_luck,0), 0, LUCK_MISC_CAP_STAT) // [DATA], обычно 100. |
| LUCK_POISON_STEP_BP_PER_POINT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | - chance_bp = clamp_int(base_chance_bp - luck_misc * LUCK_POISON_STEP_BP_PER_POINT, 0, 10000). |
| LUCK_SHIELD_STEP_BP_PER_POINT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | - chance_bp = clamp_int(base_chance_bp + luck_misc * LUCK_SHIELD_STEP_BP_PER_POINT, 0, 10000). |
| LUCK_VISIT_STEP_BP_PER_POINT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | - chance_bp = clamp_int(visit_chance_bp - luck_misc * LUCK_VISIT_STEP_BP_PER_POINT, 0, 10000). |
| RESTED_LUCK_MULT_PCT | LUCK | INT |  | int; domain-specific |  | DB_SPEC/balance_luck | B22 | LuckHomeMultBp = clamp_bp(10000 + (HOME_LUCK_MULT_PCT + RESTED_LUCK_MULT_PCT) * 100, ...) |
| COMBAT_ROUND_SEC | PLATFORM | SEC | sec | int sec >=0 |  | core/*.json (if data-backed) or CANON constant | B02, B05, B07, B09 | • Время: t_sec/таймеры/кулдауны; TIME_ADVANCE как единственный способ протекания времени вне боя; в бою — по канону COMBAT_ROUND_SEC. |
| RULE_CAP_CLAMP | PLATFORM | INT |  | int; domain-specific |  | core/*.json (if data-backed) or CANON constant | B03, B04, B08 | - rule_id: string (обязателен; стабильный ID правила, например RULE_CAP_CLAMP). |
| RULE_DMG_CAP | SPELLS | INT |  | int; >=0 |  | DB_SPEC/spells | B12 | - explain: RULE_SPELL_TOGGLE; RULE_DMG_CAP meta{spell_id, cap_hp, before, after}. |
| RULE_SPELL_CAP_CLAMP | SPELLS | INT |  | int; domain-specific |  | DB_SPEC/spells | B12 | - explain: RULE_SPELL_TICK tick_kind='barrier.recharge_check'; RULE_SPELL_TOGGLE; optional RULE_SPELL_CAP_CLAMP for clamping barrier_current. |
| RecoverChanceBp | SPELLS | CHANCE_BP | chance_bp | 0..10000 |  | DB_SPEC/spells | B12, B22 | • UI/DATA: RecoverChancePct:int (0..100). Core: RecoverChanceBp = clamp_int(RecoverChancePct*100, 0, 10000). |
| ShieldProcMeleeChanceBp | SPELLS | CHANCE_BP | chance_bp | 0..10000 |  | DB_SPEC/spells | B12, B22 | - ShieldProcMeleeChanceBp:int (0..10000) |
| ShieldProcRangedChanceBp | SPELLS | CHANCE_BP | chance_bp | 0..10000 |  | DB_SPEC/spells | B12, B22 | - ShieldProcRangedChanceBp:int (0..10000) |
| BASE_AWAKE_GAIN_PER_HOUR | SURVIVAL | INT |  | int; domain-specific |  | DB_SPEC/balance_survival | B09 | • BASE_AWAKE_GAIN_PER_HOUR:int (FAT за 3600s) — [DATA] (balance). |
| REST_RECOVERY_PER_HOUR | SURVIVAL | INT |  | int; domain-specific |  | DB_SPEC/balance_survival | B09 | • Отдых без сна (REST): REST_RECOVERY_PER_HOUR:int — [DATA]; дополнительные условия (например rest_has_food/rest_has_water) — как булевы флаги сцены (ASSUMPTION ниже). |
| SLEEP_RECOVERY_PER_HOUR_BY_BLOCK | SURVIVAL | INT |  | int; domain-specific |  | DB_SPEC/balance_survival | B09 | • Сон считается блоками по 3600s. [DATA] SLEEP_RECOVERY_PER_HOUR_BY_BLOCK задаётся в DB_SPEC/balance; применяется через apply_bp_floor (в milli-FAT). |
| THIRST_T5_HP_DOT_PER_HOUR | SURVIVAL | INT |  | int; domain-specific |  | DB_SPEC/balance_survival | B09 | • DoT THIRST на T5: THIRST_T5_HP_DOT_PER_HOUR:int (HP за 3600s) — [DATA] (balance). |
| COFFER_SLOT_COUNTS_BY_GRADE | LOOT | TABLE | slots | per-grade int>=1 | P=7; N=10; R=14; BOSS=20 | DB_SPEC/loot_coffers | B24.LOOT.DATA.11 | • [DATA] COFFER_SLOT_COUNTS_BY_GRADE (пример/дефолты; DB_SPEC): P=7, N=10, R=14, BOSS=20. |
