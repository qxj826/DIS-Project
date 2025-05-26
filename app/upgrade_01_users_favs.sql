ALTER TABLE "user"
  ADD COLUMN IF NOT EXISTS email    text,
  ADD COLUMN IF NOT EXISTS fullname text;

CREATE TABLE IF NOT EXISTS favourite (
  user_id  integer REFERENCES "user"(id)   ON DELETE CASCADE,
  snack_id integer REFERENCES snack(id)    ON DELETE CASCADE,
  PRIMARY KEY (user_id, snack_id)
);