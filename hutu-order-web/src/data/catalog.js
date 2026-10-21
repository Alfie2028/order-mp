export const CAMPUS = {
  name: '河南农业大学软件学院', campus: '许昌校区',
  address: '许昌市建安区劳动北路以东、农大路以南',
  latitude: 34.136151, longitude: 113.809055,
  osmLatitude: 34.137604, osmLongitude: 113.803046,
  sourceUrl: 'https://www.amap.com/place/B0FFF66XXR',
}

export const STORES = [
  {
    id: 'henau-canteen',
    name: '农大温馨家园', shortName: '农大温馨家园', tag: '校内',
    address: '许昌市建安区永宁街与劳动北路交叉口向北500米', distance: 160,
    hours: '07:30–21:30', status: 'open', waitMinutes: 8,
    services: ['到店自取', '档口堂食'],
    latitude: 34.136151, longitude: 113.809055,
    osmLatitude: 34.137604, osmLongitude: 113.803046,
    image: '/uploads/catalog/store/store-campus.png', imageCredit: 'Taha Samet Arslan / Pexels',
    sourceUrl: 'https://www.henau.edu.cn/info/1141/41350.htm',
  },
  {
    id: 'nongda-road',
    name: '农大路美食档口', shortName: '农大路美食档口', tag: '校外',
    address: '许昌市建安区苏桥镇南村劳动路与农大路交叉口西侧', distance: 850,
    hours: '08:00–22:00', status: 'open', waitMinutes: 10,
    services: ['到店自取', '档口堂食'],
    latitude: 34.141490, longitude: 113.802449,
    osmLatitude: 34.142931, osmLongitude: 113.796422,
    image: '/uploads/catalog/store/store-street.png', imageCredit: 'Dynin / Pexels',
    sourceUrl: 'https://map.gaode.com/place/B0L1X7SB0L',
  },
  {
    id: 'suqiao-town',
    name: '苏桥老街档口', shortName: '苏桥老街档口', tag: '校外',
    address: '许昌市建安区苏桥镇中心生活区', distance: 1886,
    hours: '08:00–21:30', status: 'busy', waitMinutes: 15,
    services: ['到店自取', '档口堂食', '停车便利'],
    latitude: 34.129395, longitude: 113.790261,
    osmLatitude: 34.130821, osmLongitude: 113.784204,
    image: '/uploads/catalog/store/store-town.png', imageCredit: 'Amelia Hallsworth / Pexels',
    sourceUrl: 'https://ditu.amap.com/place/B01760MUCZ',
  },
]

export const STALLS = [
  { id: 'stir-fry', name: '现炒盖饭', shortName: '盖饭', description: '现点现炒，荤素搭配' },
  { id: 'noodles', name: '粉面档口', shortName: '粉面', description: '汤面拌面，快捷出餐' },
  { id: 'henan', name: '河南风味', shortName: '豫味', description: '本地风味，传统餐食' },
  { id: 'dumplings', name: '饺子馄饨', shortName: '面点', description: '手作面点，热汤现煮' },
  { id: 'light-food', name: '轻食烘焙', shortName: '轻食', description: '轻负担搭配与每日烘焙' },
  { id: 'drinks', name: '饮品甜品', shortName: '饮品', description: '果茶、乳茶与茶饮' },
]

const portionOptions = {
  id: 'portion', name: '份量', required: true, multiple: false,
  options: [{ id: 'regular', name: '标准份', extraCents: 0 }, { id: 'large', name: '加量份', extraCents: 300 }],
}
const spiceOptions = {
  id: 'spice', name: '辣度', required: true, multiple: false,
  options: [{ id: 'none', name: '不辣', extraCents: 0 }, { id: 'mild', name: '微辣', extraCents: 0 }, { id: 'regular', name: '标准辣', extraCents: 0 }],
}
const mealExtras = {
  id: 'extras', name: '加料', required: false, multiple: true,
  options: [{ id: 'egg', name: '加煎蛋', extraCents: 200 }, { id: 'rice', name: '加米饭', extraCents: 200 }],
}
const noodleExtras = {
  id: 'extras', name: '加料', required: false, multiple: true,
  options: [{ id: 'egg', name: '加卤蛋', extraCents: 200 }, { id: 'beef', name: '加牛肉', extraCents: 600 }],
}
const dumplingOptions = [
  { id: 'portion', name: '份量', required: true, multiple: false, options: [{ id: '12', name: '12 个', extraCents: 0 }, { id: '18', name: '18 个', extraCents: 500 }] },
  { id: 'sauce', name: '蘸料', required: true, multiple: false, options: [{ id: 'vinegar', name: '陈醋', extraCents: 0 }, { id: 'garlic', name: '蒜泥', extraCents: 0 }, { id: 'chili', name: '红油', extraCents: 0 }] },
]
const drinkOptions = [
  { id: 'size', name: '杯型', required: true, multiple: false, options: [{ id: 'regular', name: '中杯', extraCents: 0 }, { id: 'large', name: '大杯', extraCents: 300 }] },
  { id: 'temperature', name: '温度', required: true, multiple: false, options: [{ id: 'iced', name: '冰', extraCents: 0 }, { id: 'hot', name: '热', extraCents: 0 }] },
  { id: 'sweetness', name: '甜度', required: true, multiple: false, options: [{ id: 'none', name: '不另加糖', extraCents: 0 }, { id: 'half', name: '半糖', extraCents: 0 }, { id: 'full', name: '标准糖', extraCents: 0 }] },
]

export const PRODUCTS = [
  { id: 'yuxiang-pork-rice', stallId: 'stir-fry', stallName: '现炒盖饭档口', name: '鱼香肉丝盖饭', subtitle: '猪里脊、木耳与时蔬现炒，酸甜微辣', priceCents: 1680, badge: '招牌盖饭', sales: 1268, image: '/uploads/catalog/product/dish-yuxiang-pork-rice.png', fallback: '盖饭', options: [portionOptions, spiceOptions, mealExtras], featured: true },
  { id: 'black-pepper-chicken-rice', stallId: 'stir-fry', stallName: '现炒盖饭档口', name: '黑椒鸡腿饭', subtitle: '去骨鸡腿配黑椒汁，搭配米饭与时蔬', priceCents: 1880, originalPriceCents: 2080, badge: '人气单品', sales: 1186, image: '/uploads/catalog/product/dish-black-pepper-chicken-rice.png', fallback: '盖饭', options: [portionOptions, mealExtras], featured: true },
  { id: 'tomato-egg-rice', stallId: 'stir-fry', stallName: '现炒盖饭档口', name: '番茄炒蛋饭', subtitle: '新鲜番茄与鸡蛋现炒，家常清爽', priceCents: 1280, badge: '家常风味', sales: 886, image: '/uploads/catalog/product/dish-tomato-egg-rice.png', fallback: '盖饭', options: [portionOptions, mealExtras] },
  { id: 'twice-cooked-pork-rice', stallId: 'stir-fry', stallName: '现炒盖饭档口', name: '回锅肉盖饭', subtitle: '五花肉片配青椒蒜苗，酱香下饭', priceCents: 1780, badge: '川味推荐', sales: 742, image: '/uploads/catalog/product/dish-twice-cooked-pork-rice.png', fallback: '盖饭', options: [portionOptions, spiceOptions, mealExtras] },

  { id: 'braised-beef-noodles', stallId: 'noodles', stallName: '粉面档口', name: '红烧牛肉面', subtitle: '慢炖牛肉与宽面，汤底醇厚', priceCents: 1980, badge: '牛肉足量', sales: 1086, image: '/uploads/catalog/product/dish-braised-beef-noodles.png', fallback: '汤面', options: [portionOptions, spiceOptions, noodleExtras], featured: true },
  { id: 'tomato-egg-noodles', stallId: 'noodles', stallName: '粉面档口', name: '番茄鸡蛋面', subtitle: '番茄鸡蛋汤底，清爽暖胃', priceCents: 1380, badge: '清爽汤面', sales: 653, image: '/uploads/catalog/product/dish-tomato-egg-noodles.png', fallback: '汤面', options: [portionOptions, noodleExtras] },
  { id: 'wuhan-hot-dry-noodles', stallId: 'noodles', stallName: '粉面档口', name: '武汉热干面', subtitle: '碱水面拌芝麻酱，搭配萝卜丁与葱花', priceCents: 1280, badge: '经典拌面', sales: 728, image: '/uploads/catalog/product/dish-wuhan-hot-dry-noodles.png', fallback: '拌面', options: [portionOptions, spiceOptions, noodleExtras] },
  { id: 'pork-wonton-soup', stallId: 'noodles', stallName: '粉面档口', name: '鲜肉小馄饨', subtitle: '鲜肉小馄饨配紫菜蛋皮清汤', priceCents: 1380, badge: '清汤现煮', sales: 592, image: '/uploads/catalog/product/dish-pork-wonton-soup.png', fallback: '馄饨', options: [portionOptions] },

  { id: 'henan-huimian', stallId: 'henan', stallName: '河南风味档口', name: '河南烩面', subtitle: '宽面配肉片、豆腐皮与海带，汤鲜面筋', priceCents: 1880, badge: '河南特色', sales: 1134, image: '/uploads/catalog/product/dish-henan-huimian.png', fallback: '烩面', options: [portionOptions, spiceOptions, noodleExtras], featured: true },
  { id: 'hulatang-youtiao', stallId: 'henan', stallName: '河南风味档口', name: '胡辣汤配油条', subtitle: '胡椒香汤搭配现炸油条，早餐经典组合', priceCents: 980, badge: '早餐推荐', sales: 932, image: '/uploads/catalog/product/dish-hulatang-youtiao.png', fallback: '早餐', options: [spiceOptions] },
  { id: 'beef-pan-fried-buns', stallId: 'henan', stallName: '河南风味档口', name: '牛肉水煎包', subtitle: '牛肉馅水煎包，底部焦脆、内馅鲜香', priceCents: 1280, badge: '现煎出餐', sales: 715, image: '/uploads/catalog/product/dish-beef-pan-fried-buns.png', fallback: '面点', options: [] },
  { id: 'xuchang-fried-liangfen', stallId: 'henan', stallName: '河南风味档口', name: '许昌炒凉粉', subtitle: '凉粉配蒜香豆酱热炒，软糯入味', priceCents: 1180, badge: '许昌风味', sales: 684, image: '/uploads/catalog/product/dish-xuchang-fried-liangfen.png', fallback: '小吃', options: [spiceOptions] },

  { id: 'pork-cabbage-dumplings', stallId: 'dumplings', stallName: '饺子馄饨档口', name: '猪肉白菜水饺', subtitle: '猪肉白菜馅手工水饺，现点现煮', priceCents: 1680, badge: '手工水饺', sales: 846, image: '/uploads/catalog/product/dish-pork-cabbage-dumplings.png', fallback: '水饺', options: dumplingOptions, featured: true },
  { id: 'chive-egg-dumplings', stallId: 'dumplings', stallName: '饺子馄饨档口', name: '韭菜鸡蛋水饺', subtitle: '韭菜鸡蛋素馅水饺，鲜香清爽', priceCents: 1480, badge: '素馅推荐', sales: 603, image: '/uploads/catalog/product/dish-chive-egg-dumplings.png', fallback: '水饺', options: dumplingOptions },
  { id: 'chili-oil-wontons', stallId: 'dumplings', stallName: '饺子馄饨档口', name: '红油抄手', subtitle: '鲜肉抄手配香辣红油与芝麻', priceCents: 1580, badge: '香辣风味', sales: 712, image: '/uploads/catalog/product/dish-chili-oil-wontons.png', fallback: '抄手', options: [portionOptions, spiceOptions] },
  { id: 'shrimp-wonton-noodles', stallId: 'dumplings', stallName: '饺子馄饨档口', name: '鲜虾云吞面', subtitle: '整虾云吞配细面与清汤，鲜味突出', priceCents: 1980, badge: '鲜虾云吞', sales: 576, image: '/uploads/catalog/product/dish-shrimp-wonton-noodles.png', fallback: '云吞面', options: [portionOptions, noodleExtras] },

  { id: 'chicken-bagel', stallId: 'light-food', stallName: '轻食烘焙档口', name: '烟熏鸡肉贝果', subtitle: '烟熏鸡肉、蔬菜与贝果组合', priceCents: 1880, badge: '轻食搭配', sales: 462, image: '/uploads/catalog/product/product-chicken-bagel.png', fallback: '轻食', options: [], featured: true },
  { id: 'butter-croissant', stallId: 'light-food', stallName: '轻食烘焙档口', name: '法式黄油可颂', subtitle: '黄油香气与层层酥脆口感', priceCents: 1200, badge: '每日烘焙', sales: 410, image: '/uploads/catalog/product/product-croissant.png', fallback: '烘焙', options: [] },
  { id: 'grilled-chicken-salad', stallId: 'light-food', stallName: '轻食烘焙档口', name: '香煎鸡胸沙拉', subtitle: '鸡胸肉、时蔬与鸡蛋的均衡搭配', priceCents: 2280, badge: '高蛋白', sales: 388, image: '/uploads/catalog/product/dish-grilled-chicken-salad.png', fallback: '沙拉', options: [] },
  { id: 'blueberry-muffin', stallId: 'light-food', stallName: '轻食烘焙档口', name: '蓝莓酸奶麦芬', subtitle: '蓝莓果粒与细腻酸奶蛋糕体', priceCents: 1300, badge: '每日烘焙', sales: 304, image: '/uploads/catalog/product/product-blueberry-muffin.png', fallback: '烘焙', options: [] },

  { id: 'lemon-tea', stallId: 'drinks', stallName: '饮品甜品档口', name: '鸭屎香柠檬茶', subtitle: '现捣黄柠檬搭配凤凰单丛茶汤', priceCents: 1400, badge: '现捣柠檬', sales: 892, image: '/uploads/catalog/product/product-lemon-tea.png', fallback: '茶饮', options: drinkOptions, featured: true },
  { id: 'grape-tea', stallId: 'drinks', stallName: '饮品甜品档口', name: '青提茉莉冰茶', subtitle: '青提果肉与茉莉茶汤组合', priceCents: 1600, badge: '鲜果茶饮', sales: 772, image: '/uploads/catalog/product/product-grape-tea.png', fallback: '茶饮', options: drinkOptions },
  { id: 'matcha-milk', stallId: 'drinks', stallName: '饮品甜品档口', name: '青岚抹茶鲜奶', subtitle: '抹茶与鲜奶融合，茶香浓郁', priceCents: 1900, badge: '茶香乳饮', sales: 588, image: '/uploads/catalog/product/product-matcha.png', fallback: '乳饮', options: drinkOptions },
  { id: 'osmanthus-milk-tea', stallId: 'drinks', stallName: '饮品甜品档口', name: '桂花轻乳茶', subtitle: '桂花蜜香与轻盈乳茶自然融合', priceCents: 1800, badge: '东方风味', sales: 547, image: '/uploads/catalog/product/product-osmanthus-milk-tea.png', fallback: '乳茶', options: drinkOptions },
]

export const COUPONS = [
  { id: 'new-user', name: '新人立减券', thresholdCents: 2000, discountCents: 500, expires: '2026-12-31' },
  { id: 'campus', name: '农大校园券', thresholdCents: 3000, discountCents: 600, expires: '2026-12-31' },
]

export const USER_PROFILE = { id: 'campus-member', name: '会员用户', title: '标准会员', avatar: '/uploads/catalog/avatar/default.png', points: 860, level: 3, nextLevelPoints: 1200 }
