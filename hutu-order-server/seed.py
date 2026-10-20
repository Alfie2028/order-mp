"""预置数据：测试账号 + 餐厅/档口/餐品（含完整规格，作为前端唯一数据源）"""
import json

from database import Base, engine, SessionLocal
import models  # noqa
from security import hash_password

STORES = [
    {"id": "henau-canteen", "name": "河南农业大学许昌校区学生餐厅", "short_name": "许昌校区餐厅",
     "address": "许昌市建安区永宁街与劳动北路交叉口向北500米", "distance": 160,
     "hours": "07:30–21:30", "status": "open", "wait_minutes": 8,
     "latitude": 34.136151, "longitude": 113.809055, "image": "/uploads/catalog/store/store-campus.png"},
    {"id": "nongda-road", "name": "农大路学生生活区餐厅", "short_name": "农大路餐厅",
     "address": "许昌市建安区苏桥镇南村劳动路与农大路交叉口西侧", "distance": 850,
     "hours": "08:00–22:00", "status": "open", "wait_minutes": 10,
     "latitude": 34.141490, "longitude": 113.802449, "image": "/uploads/catalog/store/store-street.png"},
    {"id": "suqiao-town", "name": "苏桥镇中心生活区餐厅", "short_name": "苏桥生活区餐厅",
     "address": "许昌市建安区苏桥镇中心生活区", "distance": 1886,
     "hours": "08:00–21:30", "status": "busy", "wait_minutes": 15,
     "latitude": 34.129395, "longitude": 113.790261, "image": "/uploads/catalog/store/store-town.png"},
]

STALLS = [
    {"id": "stir-fry", "store_id": "henau-canteen", "name": "现炒盖饭", "short_name": "盖饭", "description": "现点现炒，荤素搭配", "code": 1},
    {"id": "noodles", "store_id": "henau-canteen", "name": "粉面档口", "short_name": "粉面", "description": "汤面拌面，快捷出餐", "code": 2},
    {"id": "henan", "store_id": "henau-canteen", "name": "河南风味", "short_name": "豫味", "description": "本地风味，传统餐食", "code": 3},
    {"id": "dumplings", "store_id": "henau-canteen", "name": "饺子馄饨", "short_name": "面点", "description": "手作面点，热汤现煮", "code": 4},
    {"id": "light-food", "store_id": "henau-canteen", "name": "轻食烘焙", "short_name": "轻食", "description": "轻负担搭配与每日烘焙", "code": 5},
    {"id": "drinks", "store_id": "henau-canteen", "name": "饮品甜品", "short_name": "饮品", "description": "果茶、乳茶与茶饮", "code": 6},
]

# ---- 规格定义（与前端 catalog 一致） ----
PORTION = {"id": "portion", "name": "份量", "required": True, "multiple": False,
           "options": [{"id": "regular", "name": "标准份", "extraCents": 0}, {"id": "large", "name": "加量份", "extraCents": 300}]}
SPICE = {"id": "spice", "name": "辣度", "required": True, "multiple": False,
         "options": [{"id": "none", "name": "不辣", "extraCents": 0}, {"id": "mild", "name": "微辣", "extraCents": 0}, {"id": "regular", "name": "标准辣", "extraCents": 0}]}
MEAL_EXTRAS = {"id": "extras", "name": "加料", "required": False, "multiple": True,
               "options": [{"id": "egg", "name": "加煎蛋", "extraCents": 200}, {"id": "rice", "name": "加米饭", "extraCents": 200}]}
NOODLE_EXTRAS = {"id": "extras", "name": "加料", "required": False, "multiple": True,
                 "options": [{"id": "egg", "name": "加卤蛋", "extraCents": 200}, {"id": "beef", "name": "加牛肉", "extraCents": 600}]}
DUMPLING = [
    {"id": "portion", "name": "份量", "required": True, "multiple": False,
     "options": [{"id": "12", "name": "12 个", "extraCents": 0}, {"id": "18", "name": "18 个", "extraCents": 500}]},
    {"id": "sauce", "name": "蘸料", "required": True, "multiple": False,
     "options": [{"id": "vinegar", "name": "陈醋", "extraCents": 0}, {"id": "garlic", "name": "蒜泥", "extraCents": 0}, {"id": "chili", "name": "红油", "extraCents": 0}]},
]
DRINK = [
    {"id": "size", "name": "杯型", "required": True, "multiple": False,
     "options": [{"id": "regular", "name": "中杯", "extraCents": 0}, {"id": "large", "name": "大杯", "extraCents": 300}]},
    {"id": "temperature", "name": "温度", "required": True, "multiple": False,
     "options": [{"id": "iced", "name": "冰", "extraCents": 0}, {"id": "hot", "name": "热", "extraCents": 0}]},
    {"id": "sweetness", "name": "甜度", "required": True, "multiple": False,
     "options": [{"id": "none", "name": "不另加糖", "extraCents": 0}, {"id": "half", "name": "半糖", "extraCents": 0}, {"id": "full", "name": "标准糖", "extraCents": 0}]},
]

# (id, stall_id, name, subtitle, price_cents, original_price_cents, badge, sales, image, options)
PRODUCTS = [
    ("yuxiang-pork-rice", "stir-fry", "鱼香肉丝盖饭", "猪里脊、木耳与时蔬现炒，酸甜微辣", 1680, 0, "招牌盖饭", 1268, "dish-yuxiang-pork-rice.png", [PORTION, SPICE, MEAL_EXTRAS]),
    ("black-pepper-chicken-rice", "stir-fry", "黑椒鸡腿饭", "去骨鸡腿配黑椒汁，搭配米饭与时蔬", 1880, 2080, "人气单品", 1186, "dish-black-pepper-chicken-rice.png", [PORTION, MEAL_EXTRAS]),
    ("tomato-egg-rice", "stir-fry", "番茄炒蛋饭", "新鲜番茄与鸡蛋现炒，家常清爽", 1280, 0, "家常风味", 886, "dish-tomato-egg-rice.png", [PORTION, MEAL_EXTRAS]),
    ("twice-cooked-pork-rice", "stir-fry", "回锅肉盖饭", "五花肉片配青椒蒜苗，酱香下饭", 1780, 0, "川味推荐", 742, "dish-twice-cooked-pork-rice.png", [PORTION, SPICE, MEAL_EXTRAS]),
    ("braised-beef-noodles", "noodles", "红烧牛肉面", "慢炖牛肉与宽面，汤底醇厚", 1980, 0, "牛肉足量", 1086, "dish-braised-beef-noodles.png", [PORTION, SPICE, NOODLE_EXTRAS]),
    ("tomato-egg-noodles", "noodles", "番茄鸡蛋面", "番茄鸡蛋汤底，清爽暖胃", 1380, 0, "清爽汤面", 653, "dish-tomato-egg-noodles.png", [PORTION, NOODLE_EXTRAS]),
    ("wuhan-hot-dry-noodles", "noodles", "武汉热干面", "碱水面拌芝麻酱，搭配萝卜丁与葱花", 1280, 0, "经典拌面", 728, "dish-wuhan-hot-dry-noodles.png", [PORTION, SPICE, NOODLE_EXTRAS]),
    ("pork-wonton-soup", "noodles", "鲜肉小馄饨", "鲜肉小馄饨配紫菜蛋皮清汤", 1380, 0, "清汤现煮", 592, "dish-pork-wonton-soup.png", [PORTION]),
    ("henan-huimian", "henan", "河南烩面", "宽面配肉片、豆腐皮与海带，汤鲜面筋", 1880, 0, "河南特色", 1134, "dish-henan-huimian.png", [PORTION, SPICE, NOODLE_EXTRAS]),
    ("hulatang-youtiao", "henan", "胡辣汤配油条", "胡椒香汤搭配现炸油条，早餐经典组合", 980, 0, "早餐推荐", 932, "dish-hulatang-youtiao.png", [SPICE]),
    ("beef-pan-fried-buns", "henan", "牛肉水煎包", "牛肉馅水煎包，底部焦脆、内馅鲜香", 1280, 0, "现煎出餐", 715, "dish-beef-pan-fried-buns.png", []),
    ("xuchang-fried-liangfen", "henan", "许昌炒凉粉", "凉粉配蒜香豆酱热炒，软糯入味", 1180, 0, "许昌风味", 684, "dish-xuchang-fried-liangfen.png", [SPICE]),
    ("pork-cabbage-dumplings", "dumplings", "猪肉白菜水饺", "猪肉白菜馅手工水饺，现点现煮", 1680, 0, "手工水饺", 846, "dish-pork-cabbage-dumplings.png", DUMPLING),
    ("chive-egg-dumplings", "dumplings", "韭菜鸡蛋水饺", "韭菜鸡蛋素馅水饺，鲜香清爽", 1480, 0, "素馅推荐", 603, "dish-chive-egg-dumplings.png", DUMPLING),
    ("chili-oil-wontons", "dumplings", "红油抄手", "鲜肉抄手配香辣红油与芝麻", 1580, 0, "香辣风味", 712, "dish-chili-oil-wontons.png", [PORTION, SPICE]),
    ("shrimp-wonton-noodles", "dumplings", "鲜虾云吞面", "整虾云吞配细面与清汤，鲜味突出", 1980, 0, "鲜虾云吞", 576, "dish-shrimp-wonton-noodles.png", [PORTION, NOODLE_EXTRAS]),
    ("chicken-bagel", "light-food", "烟熏鸡肉贝果", "烟熏鸡肉、蔬菜与贝果组合", 1880, 0, "轻食搭配", 462, "product-chicken-bagel.png", []),
    ("butter-croissant", "light-food", "法式黄油可颂", "黄油香气与层层酥脆口感", 1200, 0, "每日烘焙", 410, "product-croissant.png", []),
    ("grilled-chicken-salad", "light-food", "香煎鸡胸沙拉", "鸡胸肉、时蔬与鸡蛋的均衡搭配", 2280, 0, "高蛋白", 388, "dish-grilled-chicken-salad.png", []),
    ("blueberry-muffin", "light-food", "蓝莓酸奶麦芬", "蓝莓果粒与细腻酸奶蛋糕体", 1300, 0, "每日烘焙", 304, "product-blueberry-muffin.png", []),
    ("lemon-tea", "drinks", "鸭屎香柠檬茶", "现捣黄柠檬搭配凤凰单丛茶汤", 1400, 0, "现捣柠檬", 892, "product-lemon-tea.png", DRINK),
    ("grape-tea", "drinks", "青提茉莉冰茶", "青提果肉与茉莉茶汤组合", 1600, 0, "鲜果茶饮", 772, "product-grape-tea.png", DRINK),
    ("matcha-milk", "drinks", "青岚抹茶鲜奶", "抹茶与鲜奶融合，茶香浓郁", 1900, 0, "茶香乳饮", 588, "product-matcha.png", DRINK),
    ("osmanthus-milk-tea", "drinks", "桂花轻乳茶", "桂花蜜香与轻盈乳茶自然融合", 1800, 0, "东方风味", 547, "product-osmanthus-milk-tea.png", DRINK),
]

# ---- 优惠券（商家后台可增删/停用） ----
# (id, name, threshold_cents, discount_cents, expires)
COUPONS = [
    ("newbie", "新人立减券", 0, 500, "2026-12-31"),
    ("henau-300", "满30减5", 3000, 500, "2026-12-31"),
    ("henau-500", "满50减10", 5000, 1000, "2026-12-31"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 测试账号：test / merchant，密码均 123456，邮箱登录
        for username, email, role, points in [("test", "test@example.com", "user", 860), ("merchant", "merchant@example.com", "merchant", 0)]:
            if not db.query(models.User).filter(models.User.username == username).first():
                db.add(models.User(username=username, email=email, password_hash=hash_password("123456"), role=role, points=points))

        for s in STORES:
            existing = db.get(models.Store, s["id"])
            if existing:
                for k, v in s.items():
                    setattr(existing, k, v)
            else:
                db.add(models.Store(**s))
        for s in STALLS:
            existing = db.get(models.Stall, s["id"])
            if existing:
                for k, v in s.items():
                    setattr(existing, k, v)
            else:
                db.add(models.Stall(**s))
        for pid, stall_id, name, subtitle, price, original, badge, sales, image, options in PRODUCTS:
            data = dict(id=pid, stall_id=stall_id, name=name, subtitle=subtitle, price_cents=price,
                        original_price_cents=original, badge=badge, sales=sales,
                        image=f"/uploads/catalog/product/{image}", options=json.dumps(options, ensure_ascii=False))
            existing = db.get(models.Product, pid)
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
            else:
                db.add(models.Product(**data))
        for cid, name, threshold, discount, expires in COUPONS:
            existing = db.get(models.Coupon, cid)
            if existing:
                existing.name, existing.threshold_cents = name, threshold
                existing.discount_cents, existing.expires = discount, expires
            else:
                db.add(models.Coupon(id=cid, name=name, threshold_cents=threshold,
                                     discount_cents=discount, expires=expires))

        db.commit()
        print("seed 完成：2 账号 / 3 餐厅 / 6 档口 / 24 餐品（含规格）/ 3 优惠券")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
