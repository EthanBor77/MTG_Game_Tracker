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

-- 2. Insert Test Decks
INSERT INTO decks (deck_name, player_id) VALUES 
('Tymna + Dargo', 1),
('Ral, Monsoon Mage', 1),
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
('Omnath, Locus of Creation', 1),
('Jon Irenicus, Shattered One', 2),
('Grolnok, the Omnivore', 2),
('Baru, Wurmspeaker', 2),
('Karumonix, the Rat King', 2),
('Liberty Prime, Recharged', 2),
('The Colossal Dreadmaw', 2),
('Lucius the Eternal', 2),
('Hogaak, Arisen Necropolis', 2),
('Patron of the Moon', 2),
('Sidisi, Undead Vizier', 2),
('Muddle, the Ever-Changing', 2),
('Phelddagrif', 2),
('Dogmeat, Ever Loyal', 2),
('Deathleaper, Terror Weapon', 2),
('Belisarius Cawl', 2),
('Imotekh the Stormlord', 2),
('Shadowheart, Dark Justiciar', 2),
('Tayam, Luminous Enigma', 2),
('The Master, Transcendent', 2),
('Sliver Legion', 2),
('Magus Lucea Kane', 2),
('Magnus the Red', 2),
('King of the Oathbreakers', 2),
('Feather, Radiant Arbiter', 2),
('Raggadragga, Goreguts Boss', 2),
('Neriv, Crackling Vanguard', 2),
('Mortarion, Daemon Primarch', 2),
('Be''lakor, the Dark Master', 2),
('Brigid, Clachan''s Heart', 2),
('Captain N''ghathrod', 2),
('Anrakyr the Traveller', 2),
('Kadena, Slinking Sorcerer', 2),
('Minwu, White Mage', 2),
('Marwyn, the Nurturer', 2),
('Marneus Calgar', 2),
('Karlach, Fury of Avernus', 2),
('Sin, Spira''s Punishment', 2),
('Slinza, the Spiked Stampede', 2),
('The Red Terror', 2),
('Thelon of Havenwood', 2),
('Zaxara, the Exemplary', 3),
('Betor, Ancestor''s Voice', 3),
('Obuun, Mul Daya Ancestor', 3),
('Katara, the Fearless', 3),
('Lorehold, the Historian', 3),
('Brimaz, Blight of Oreskos', 3),
('Y''shtola, Night''s Blessed', 3),
('The Ur-Dragon', 3),
('Hearthhull, the Worldseed', 3),
('Kellan, the Kid', 3),
('Eriette of the Charmed Apple', 3),
('Ashling, the Limitless', 3),
('Sovereign Okinec Ahau', 3),
('Otrimi, the Ever-Playful', 3),
('Mendicant Core, Guidelight', 3),
('Golbez, Crystal Collector', 3),
('Ardbert, Warrior of Darkness', 3),
('Jarad, Golgari Lich Lord', 3),
('The Emperor of Palamecia', 3),
('Adrix and Nev, Twincasters', 3),
('Okaun + Zndrsplt', 3),
('Kresh the Bloodbraided', 3),
('Muldrotha, the Gravetide', 3),
('Omo, Queen of Vesuva', 3),
('Henzie "Toolbox" Torre', 3),
('Myrkul, Lord of Bones', 3),
('Blue + Owen', 3),
('Killian, Decisive Mentor', 3),
('Obeka, Splitter of Seconds', 3),
('Sidisi, Brood Tyrant', 3),
('Terra, Magical Adept (Kellen)', 3),
('The Lord of Pain', 3),
('Zimone, Infinite Analyst', 3),
('Vial Smasher + Kydele', 4),
('Optimus Prime, Hero', 4),
('Dr. Eggman', 4),
('Clive, Ifrit''s Dominant', 4),
('The Reaper, King No More', 4),
('Terra, Magical Adept (Alex)', 4),
('Grimlock, Dinobot Leader', 4),
('Quintorius, History Chaser (Alex)', 4),
('Amazing Spider-Man', 4),
('Black Cat, Cunning Thief', 4),
('Zoraline, Cosmos Caller', 4),
('Tifa, Martial Artist', 4),
('Yarok, the Desecrated', 4),
('Tura Kennerud', 4),
('Dina, Essence Brewer (Alex)', 4),
('Anti-Venom, Horrifying Healer', 4),
('Liliana, Heretical Healer', 4),
('Gev, Scaled Scorch', 4),
('Shadrix Silverquill', 4),
('Prosper, Tome-Bound', 4),
('Karador, Ghost Chieftain', 4),
('Inspirit, Flagship Vessel', 4),
('Thantis, the Warweaver', 4),
('Cloud, Ex-SOLDIER', 4),
('Ashnod the Uncaring', 4),
('Chulane, Teller of Tales', 4),
('Eirdu, Carrier of Dawn', 4),
('Reaper King', 4),
('Kuja, Genome Sorcerer', 4),
('Nicol Bolas, the Ravager', 4),
('Hakbal of the Surging Soul', 4),
('Felix Five Boots', 4),
('Iroh, Grand Lotus', 4),
('Kasla, the Broken Halo', 4),
('Rendmaw, Creaking Nest', 4),
('Teval, the Balanced Scale', 4),
('Sefris of the Hidden Ways', 4),
('Syr Gwyn, Hero of Ashvale', 4),
('The Swarmweaver', 4),
('Toph, Hardheaded Teacher', 4),
('Ulalek, Fused Atrocity', 4),
('Uro, Titan of Nature''s Wrath', 4),
('High Perfect Morcant', 4),
('Evra, Halcyon Witness', 4),
('Sorin of House Markov', 5),
('Dina, Essence Brewer (Rohan)', 6),
('Quintorius, History Chaser (Rohan)', 6),
('Wilson, Refined Grizzly', 7),
('Chatterfang, Squirrel General', 7),
('Elenda, the Dusk Rose', 8),
('Isshin, Two Heavens as One', 8),
('Xenagos, God of Revels', 8);

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