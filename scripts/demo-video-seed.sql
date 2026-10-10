BEGIN;
DO $$ BEGIN IF current_database() <> 'liyu_video_20261010' THEN RAISE EXCEPTION 'Only recording fixture DB allowed'; END IF; END $$;
INSERT INTO users(id,identifier,display_name,password_hash) VALUES
(90001,'demo-video@liyu.test','安禾（演示）','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
(90002,'linzhou-video@liyu.test','林舟（演示）','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
(90003,'chenxiao-video@liyu.test','陈晓（演示）','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'),
(90004,'zhou-video@liyu.test','周知夏（演示）','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92') ON CONFLICT(id) DO NOTHING;
INSERT INTO user_profiles(user_id,email) SELECT id,identifier FROM users WHERE id BETWEEN 90001 AND 90004 ON CONFLICT DO NOTHING;
INSERT INTO friendships(user_low_id,user_high_id,requested_by_user_id,status,accepted_at) VALUES (90001,90002,90001,'accepted',now()),(90001,90003,90001,'accepted',now()),(90001,90004,90001,'accepted',now()) ON CONFLICT DO NOTHING;
INSERT INTO friend_details(owner_id,friend_id,nickname,relationship,birthday,note) VALUES
(90001,90002,'林舟','老友','1995-10-17','演示资料：喜欢咖啡和电影，不喜欢太甜的食物。'),
(90001,90003,'陈晓','同学','1996-12-12','演示资料：喜欢手帐和文具。'),
(90001,90004,'周知夏','朋友','1994-11-03','演示资料：刚搬新家，喜欢花与香薰。') ON CONFLICT DO NOTHING;
INSERT INTO gifts(id,sender_id,recipient_id,product_id,state,price_cents,unlock_kind,clue,answer_hash,message,contract_text,puzzle_configured,expires_at,opened_at,revealed_at,settled_at) VALUES
(91001,90002,90001,1,'sealed',3500,'free','','','演示礼盒：忙碌时也记得休息。','',true,now()+interval '30 days',NULL,NULL,NULL),
(91002,90003,90001,9,'sealed',3900,'question','我们大学时一起参加的社团？','d18d2d314ffb45a5eaf12d62e0aeb94f48de11a50a53bcbec15b94041cd151fd','演示礼盒：为你的新手帐添一点色彩。','',true,now()+interval '30 days',NULL,NULL,NULL),
(91003,90004,90001,3,'accepted',4900,'free','','','演示礼物：一起去看电影。','一起看一场电影',true,now()+interval '30 days',now(),now(),now()),
(91004,90001,90003,9,'sealed',3900,'free','','','演示送出：愿你的每一天都有灵感。','',true,now()+interval '30 days',NULL,NULL,NULL),
(91005,90001,90002,6,'accepted',8800,'free','','','演示送出：周末一起放松一下。','一起喝咖啡',true,now()+interval '30 days',now(),now(),now()) ON CONFLICT DO NOTHING;
INSERT INTO gift_contracts(gift_id,status) VALUES(91003,'pending'),(91005,'pending') ON CONFLICT DO NOTHING;
INSERT INTO gift_contract_marks(gift_id,user_id,status) VALUES(91003,90001,'pending'),(91003,90004,'pending'),(91005,90001,'pending'),(91005,90002,'fulfilled') ON CONFLICT DO NOTHING;
INSERT INTO gift_contract_schedules(gift_id,proposed_on,proposer_id,revision) VALUES(91003,current_date+7,90004,1) ON CONFLICT DO NOTHING;
INSERT INTO wishlists(id,owner_id,title,note,occasion,event_on) VALUES(92001,90002,'生日小心愿（演示）','咖啡或电影就很开心','birthday',current_date+7),(92002,90003,'手帐灵感（演示）','不需要贵，喜欢文具','other',current_date+30) ON CONFLICT DO NOTHING;
INSERT INTO wishlist_items(wishlist_id,ordinal,product_id) SELECT 92001,0,1 WHERE NOT EXISTS(SELECT 1 FROM wishlist_items WHERE wishlist_id=92001);
INSERT INTO wishlist_items(wishlist_id,ordinal,product_id) SELECT 92002,0,9 WHERE NOT EXISTS(SELECT 1 FROM wishlist_items WHERE wishlist_id=92002);
SELECT setval(pg_get_serial_sequence('users','id'),(SELECT max(id) FROM users));
SELECT setval(pg_get_serial_sequence('gifts','id'),(SELECT max(id) FROM gifts));
SELECT setval(pg_get_serial_sequence('wishlists','id'),(SELECT max(id) FROM wishlists));
COMMIT;
