INSERT INTO users (id, email) VALUES (1, 'user1@gmail.com');

INSERT INTO posters (id, name, qr_id, qr_value) VALUES (1, '''RN Association''', '''qr1234''', NULL);

INSERT INTO users_posters (id, users_id, posters_id) VALUES (1, 1, 1);

INSERT INTO surveys (id, comment, users_posters_id) VALUES (1, '''user 1 poster 1''', 1);

INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (1, 5, 1, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (2, 6, 2, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (3, 3, 3, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (4, 5, 4, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (5, 4, 5, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (6, 1, 6, 1);
INSERT INTO answers (id, answer, questions_id, surveys_id) VALUES (7, 2, 7, 1);
