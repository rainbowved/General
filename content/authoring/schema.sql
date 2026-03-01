PRAGMA foreign_keys = ON;

CREATE TABLE tags (
  tag_id TEXT PRIMARY KEY,
  namespace TEXT NOT NULL,
  code TEXT NOT NULL,
  UNIQUE(namespace, code)
);

CREATE TABLE items (
  item_id TEXT PRIMARY KEY,
  item_class TEXT NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE item_tags (
  item_id TEXT NOT NULL,
  tag_id TEXT NOT NULL,
  PRIMARY KEY (item_id, tag_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id),
  FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

CREATE TABLE loot_coffers (
  coffer_id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE loot_pools (
  pool_id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE loot_pool_rows (
  pool_id TEXT NOT NULL,
  row_id INTEGER NOT NULL,
  item_id TEXT NOT NULL,
  weight_bp INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  PRIMARY KEY (pool_id, row_id),
  FOREIGN KEY (pool_id) REFERENCES loot_pools(pool_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE coffer_pool_map (
  coffer_id TEXT NOT NULL,
  pool_id TEXT NOT NULL,
  ordering_key INTEGER NOT NULL,
  PRIMARY KEY (coffer_id, pool_id),
  FOREIGN KEY (coffer_id) REFERENCES loot_coffers(coffer_id),
  FOREIGN KEY (pool_id) REFERENCES loot_pools(pool_id)
);

CREATE TABLE recipes (
  recipe_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  time_sec INTEGER NOT NULL
);

CREATE TABLE recipe_slots (
  recipe_id TEXT NOT NULL,
  slot_no INTEGER NOT NULL,
  item_id TEXT NOT NULL,
  qty INTEGER NOT NULL,
  PRIMARY KEY (recipe_id, slot_no),
  FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE quests (
  quest_id TEXT PRIMARY KEY,
  objective_type TEXT NOT NULL,
  reward_coffer_id TEXT NOT NULL,
  FOREIGN KEY (reward_coffer_id) REFERENCES loot_coffers(coffer_id)
);

CREATE TABLE quest_objective_filter_tags (
  quest_id TEXT NOT NULL,
  tag_id TEXT NOT NULL,
  PRIMARY KEY (quest_id, tag_id),
  FOREIGN KEY (quest_id) REFERENCES quests(quest_id),
  FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

CREATE TABLE pois (
  poi_id TEXT PRIMARY KEY,
  option_text TEXT NOT NULL,
  loot_coffer_id TEXT NOT NULL,
  open_once INTEGER NOT NULL CHECK(open_once IN (0,1)),
  FOREIGN KEY (loot_coffer_id) REFERENCES loot_coffers(coffer_id)
);
