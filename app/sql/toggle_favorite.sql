WITH ins AS (
  INSERT INTO favourite(user_id, snack_id)
  VALUES (:u, :s) ON CONFLICT DO NOTHING RETURNING 1
)
DELETE FROM favourite
      WHERE user_id=:u AND snack_id=:s
        AND NOT EXISTS (SELECT 1 FROM ins);