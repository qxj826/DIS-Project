CREATE TABLE IF NOT EXISTS snack (
    id       SERIAL PRIMARY KEY,
    name     text,
    calories numeric,
    grams    numeric,
    protein  numeric,
    carbs    numeric
);


BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'snack_name_cal_unique'
    ) THEN
        ALTER TABLE snack
          ADD CONSTRAINT snack_name_cal_unique
          UNIQUE (name, calories);
    END IF;
END;
