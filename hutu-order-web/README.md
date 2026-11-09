# 校园多档口点餐（uni-app 小程序 / H5）

校园餐饮聚合应用：前端 uni-app（Vue 3 + Vite）一套代码同时构建微信小程序与 H5，后端 FastAPI + SQLite 提供门店、档口、餐品、优惠券、购物车、订单、评价等接口，经 Cloudflare 隧道对公网提供服务。

当前版本 **v1.1.0**（对应标签 `v1.1.0-20261109`，提交见文末版本记录）。

## 目录结构

```
移动课设/
├─ hutu-order-web/          前端（uni-app）
│  ├─ src/pages/            页面：首页 / 点单 / 门店 / 我的 + 业务子页
│  ├─ src/component/        公共组件（ProductCard、EmptyState 等）
│  ├─ src/store/app.js      全局状态与接口编排
│  ├─ src/data/catalog.js   本地兜底目录（接口不可用时使用）
│  ├─ src/utils/request.js  请求封装与 BASE_URL
│  ├─ 答辩材料/             答辩讲稿、问答与排练清单
│  └─ docs/refactor-progress.md  设计文档与版本记录
├─ hutu-order-server/       后端（FastAPI + SQLAlchemy + SQLite）
└─ docs/                    设计过程稿（入口方案对比图）
```

## 页面与功能

| 入口 | 页面 | 内容 |
| --- | --- | --- |
| 首页 | `pages/home/index` | 轮播、搜索、十格金刚区、美食节 banner、券卡与秒杀卡、筛选、门店卡、人气餐品 |
| 点单 | `pages/order/index` | 左栏 6 个档口，右侧档口餐品列表、规格选择、购物车与结算入口 |
| 门店 | `pages/shop/index` | 3 家门店（农大温馨家园 160m / 农大路美食档口 850m / 苏桥老街档口 1886m） |
| 我的 | `pages/my/index` | 登录、统计、热量管家、签到、在线客服、我的常点 |
| 子页 | `item-detail`、`confirm-order`、`my-order`、`setting`、`login`、`settled`、`merchant/*` | 详情、结算、订单、设置、商家工作台 |

## 数据来源与兜底

- 启动后 `store/app.js` 的 `loadCatalog()` 并行请求 `/api/catalog/stores|stalls|products|coupons`，接口数据覆盖本地兜底数据。
- `src/data/catalog.js` 只在接口失败或离线时使用，结构（门店 / 档口 / 餐品 / 券）与后端一致；后端返回的 snake_case 字段由 `mapStore / mapStall / mapProduct / mapCoupon` 统一转换，并用本地目录补齐 `badge`、`featured`、图片占位字等展示字段。
- 图片：`/uploads/` 开头的走 `BASE_URL` 拼接，静态资源原样使用；加载失败有文字降级。
- 服务地址：`https://campus-order.learnshare.uk`（`src/utils/request.js`）。

## 关键业务规则（答辩可讲的口径）

- **三级结构**：门店 → 档口 → 餐品；6 个档口为现炒盖饭、粉面、河南风味、饺子馄饨、轻食烘焙、饮品甜品，线上 25 道餐品（本地兜底目录 24 条，各档 4 条）。
- **点单页分组**：每个档口先列本档口餐品（约 4 道），再按销量补 6 道「同店其他档口 · 也受欢迎」，单页 10 道；借来的餐品仍显示其真实档口名，下单落回原档口，不影响库存与订单。
- **在售全部来自后端**：档口隶属门店、餐品隶属档口的关系由数据库决定，前端只做展示与兜底，不靠前端硬造商品。
- **在线客服**：点卡片弹「校园餐厅客服中心」说明，热线 400-800-1234、受理时间 07:30–21:30（节假日正常）；点「拨打」调 `uni.makePhoneCall` 唤起系统拨号盘。
- **演示态**：支付、订单状态推进、签到等为本地演示逻辑，不发起真实交易。

## 运行与构建

```bash
cd hutu-order-web
npm install

npm run dev:h5            # 浏览器预览
npm run build:h5          # H5 产物 dist/build/h5
npm run build:mp-weixin   # 小程序产物 dist/build/mp-weixin，用微信开发者工具导入运行
```

后端（可选，未启动时前端自动走本地兜底数据）：

```bash
cd hutu-order-server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 推荐演示路径

1. 首页看轮播、金刚区、美食节 banner 与券卡，搜索「盖饭」验证检索。
2. 进入「点单」，左栏切换档口，观察「本档口 + 同店其他档口」两组共 10 道。
3. 选一份带规格的餐品（份量 / 辣度 / 加料）加入购物车。
4. 结算页选券、提交，订单页推进「制作中 → 待取餐 → 已完成」。
5. 「我的」体验签到、热量管家，点「在线客服」演示拨号弹窗。

## 答辩材料

统一放在 [`答辩材料/`](答辩材料/)，从 [材料索引](答辩材料/00-索引.md) 进入：

- [答辩讲解与演示](答辩材料/01-答辩讲解与演示.md)
- [常见问题与参考回答](答辩材料/02-常见问题与参考回答.md)
- [速记与排练清单](答辩材料/03-速记与排练清单.md)

## 版本记录

| 版本 / 标签 | 提交 | 主要内容 |
| --- | --- | --- |
| v1.1.0 / `v1.1.0-20261109` | `81371d6` | 点单页补同店其他档口推荐（每页 10 道）、客服改真实热线拨号、首页去定位文字、删券包并上移餐品列表、双模卡删除与搜索框独立成行、金刚区与美食节 banner 改版 |
| v1.0.0 / `pre-home-redesign-20261108` | `0158489` | 评价接口与评价卡、商家工作台入口方案 B、门店口径统一、首页与我的页排版重构 |

设计决策与阶段评估见 [`docs/refactor-progress.md`](docs/refactor-progress.md)。

## 已知边界

- 微信小程序产物需用微信开发者工具打开；H5 预览在本机曾出现白屏（TDZ），以小程序端为准。
- 地图使用平台原生组件，不提供真实路线导航；距离与出餐时间为配置值。
- 支付、订单流转、会员积分为演示实现，不接真实渠道。
- 客服热线为演示号码，仅用于展示拨打流程。
