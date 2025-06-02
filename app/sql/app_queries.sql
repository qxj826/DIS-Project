/* ---------- user update --------------------------------- */
UPDATE "user"
   SET username=:u, email=:e, fullname=:f
 WHERE id=:id;
