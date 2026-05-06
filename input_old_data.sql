-- 1. Insert Test Players
-- 1 - Ethan
-- 2 - Troy
-- 3 - Kellen
-- 4 - Alex
-- 5 - Kayla
-- 6 - Rohan
-- 7 - Colt
-- 8 - Max
INSERT INTO players (player_name) VALUES 
('Ethan'), 
('Troy'), 
('Kellen'), 
('Alex'),
('Kayla'),
('Rohan'),
('Colt'),
('Max');

-- 2. Insert Test Decks (Referencing Player IDs 1-4)
INSERT INTO decks (deck_name, player_id) VALUES 
('Tymna + Dargo', 1),        -- Ethan's Deck
('Maralen, Fae Ascendant', 1),
('Akiri + Silas', 1),
('Merry + Pippin', 1),
('Alela, Cunning Conqueror', 1),
('Abdel Adrian, Gorion''s Ward', 1),
('Rootha, Mastering the Moment', 1),
('Octavia, Living Thesis', 1),
('Gut, True Soul Zealot', 1),
('Stella Lee, Wild Card', 1),
('Yuma, Proud Protector', 1),
('Green Goblin', 1),
('Ms. Bumbleflower', 1),
('Mirko, Obsessive Theorist', 1),
('Zimone and Dina', 1),
('Marchesa, Dealer of Death', 1),
('Leonardo, the Balance', 1),
('Michelangelo + Donatello', 1),
('Rionya, Fire Dancer', 1),
('Killian, Ink Duelist', 1),
('Ashling, Flame Dancer', 1),
('', 1),
('', 1),
('', 1),
('', 1),
('', 1),
('Belisarius Cawl', 2), -- Troy's Deck
('Y''shtola, Night''s Blessed', 3), -- Kellen's Deck
('Felix Five Boots', 4); -- Alex's Deck

-- 3. Insert Test Games
-- (game_date, first_blood_turn, end_turn, win_condition)
-- INSERT INTO games (game_date, first_blood_turn, end_turn, win_condition) VALUES 
-- ('2026-05-01', 4, 8, 'Combat'),
-- ('2026-05-02', 6, 12, 'Commander Damage'),
-- ('2026-05-03', 5, 7, 'Combo');

-- -- 4. Insert Participants for Game #1
-- -- (player_id, game_id, deck_id, is_winner, turn_order)
-- INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order) VALUES 
-- (1, 1, 1, 1, 1), -- Ethan wins from Seat 1
-- (2, 1, 2, 0, 2), -- Kellen loses from Seat 2
-- (3, 1, 3, 0, 3), -- Troy loses from Seat 3
-- (4, 1, 4, 0, 4); -- Alex loses from Seat 4

-- -- 5. Insert Participants for Game #2
-- INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order) VALUES 
-- (1, 2, 5, 0, 4), -- Ethan loses from Seat 4
-- (2, 2, 2, 1, 1), -- Kellen wins from Seat 1
-- (3, 2, 3, 0, 2), -- Troy loses from Seat 2
-- (4, 2, 4, 0, 3); -- Alex loses from Seat 3

-- -- 6. Insert Participants for Game #3 (A 3-player Pod Test)
-- INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order) VALUES 
-- (1, 3, 1, 0, 1), -- Ethan loses from Seat 1
-- (3, 3, 3, 1, 2), -- Troy wins from Seat 2
-- (4, 3, 4, 0, 3); -- Alex loses from Seat 3