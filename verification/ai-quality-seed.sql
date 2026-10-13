-- Apply ONLY to a fresh disposable liyu_ai_quality_* database after server migrations.
-- Fictional rows exercise IDs beyond the first page and unavailable coffee traps.
INSERT INTO catalog(id,name,category,price_cents,physical,brand,kind,spec,description,stock)
SELECT n, '质量测试日用品 ' || n, 'home', 6000, true, '测试品牌', '日用品',
       '虚构测试商品', '仅用于质量评测，不销售。', 100
FROM generate_series(100,159) n;
INSERT INTO catalog(id,name,category,price_cents,physical,brand,kind,spec,description,stock,is_active)
VALUES
 (200,'太极测试品牌咖啡电子券','coffee',4500,false,'太极测试品牌','咖啡','30天有效 · 仅测试','虚构测试咖啡券；未提供成分、糖量或咖啡因保证。',10,true),
 (900,'缺货咖啡电子券','coffee',3000,false,'测试品牌','咖啡','仅测试','预算内但库存为零，不能推荐。',0,true),
 (901,'下架咖啡电子券','coffee',3000,false,'测试品牌','咖啡','仅测试','预算内但已下架，不能推荐。',100,false);
