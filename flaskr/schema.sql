DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posters;
DROP TABLE IF EXISTS users_posters;
DROP TABLE IF EXISTS surveys;
DROP TABLE IF EXISTS answers;

-- Table: questions
CREATE TABLE questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  question TEXT (250) NOT NULL
);
INSERT INTO questions (id, question) VALUES (1, 'How much do you like cars?');
INSERT INTO questions (id, question) VALUES (2, 'How much do you like planes?');
INSERT INTO questions (id, question) VALUES (3, 'How much do you like halo?');
INSERT INTO questions (id, question) VALUES (4, 'How much do you like mario?');
INSERT INTO questions (id, question) VALUES (5, 'How much do you like pizza?');
INSERT INTO questions (id, question) VALUES (6, 'How much do you like vegetables?');
INSERT INTO questions (id, question) VALUES (7, 'How much do you like bikes?');


-- Table: users
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE
);

-- Table: posters
CREATE TABLE posters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE, 
  qr_id TEXT UNIQUE, 
  qr_value TEXT
);

-- Table: users_posters
CREATE TABLE users_posters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  users_id INTEGER UNIQUE REFERENCES users (id)
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION NOT NULL, 
  posters_id INTEGER
  REFERENCES posters (id) 
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION UNIQUE NOT NULL
);

-- Table: surveys
CREATE TABLE surveys (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comment TEXT (250),
  users_posters_id INTEGER NOT NULL 
  REFERENCES users_posters (id) 
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION
);

-- Table: answers
CREATE TABLE answers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  answer INTEGER NOT NULL DEFAULT(0),
  questions_id INTEGER NOT NULL REFERENCES questions
  (id) ON DELETE NO ACTION 
  ON UPDATE NO ACTION, 
  surveys_id INTEGER
  REFERENCES surveys(id) 
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION 
  NOT NULL
);
