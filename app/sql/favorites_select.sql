SELECT s.*
  FROM favourite f
  JOIN snack s ON s.id = f.snack_id
 WHERE f.user_id = :u;
