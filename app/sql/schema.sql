CREATE TABLE IF NOT EXISTS "user"(
  id            SERIAL PRIMARY KEY,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT,
  email         TEXT,
  fullname      TEXT
);

CREATE TABLE IF NOT EXISTS snack(
  id       SERIAL PRIMARY KEY,
  name     TEXT,
  calories NUMERIC,
  grams    NUMERIC,
  protein  NUMERIC,
  carbs    NUMERIC,
  CONSTRAINT snack_name_cal_unique UNIQUE(name, calories)
);

CREATE TABLE IF NOT EXISTS favourite(
  user_id  INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
  snack_id INTEGER REFERENCES snack(id) ON DELETE CASCADE,
  PRIMARY KEY(user_id, snack_id)
);
