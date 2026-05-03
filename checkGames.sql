SELECT 
    g.game_id AS "ID",
    g.game_date AS "Date",
    p.player_name AS "Player",
    d.deck_name AS "Deck",
    part.turn_order AS "Turn",
    CASE 
        WHEN part.is_winner = 1 THEN '★ WINNER' 
        ELSE 'Loss' 
    END AS "Result",
    g.win_condition AS "Win Con",
    g.first_blood_turn AS "First Blood",
    g.end_turn AS "Ended On"
FROM games g
JOIN participants part ON g.game_id = part.game_id
JOIN players p ON part.player_id = p.player_id
JOIN decks d ON part.deck_id = d.deck_id
ORDER BY g.game_id ASC, part.turn_order ASC;