Telegram Auth sahifasi uchun backendning to‘liq arxitektura tuzilmasini faqat tuzilma va vazifalar shaklida keltiraman
📦 1. Telegram Auth (Backend tuzilmasi)
🔹 Asosiy maqsad:
Foydalanuvchini Telegram orqali tizimga autentifikatsiya qilish, so‘ngra unga JWT token berish va foydalanuvchi ma’lumotlarini bazaga saqlash.
🧩 Asosiy komponentlar
1️⃣ Route layer (auth_routes)
URL: /api/auth/telegram
Metod: POST
Vazifa: 
Frontenddan Telegram login widget orqali yuborilgan ma’lumotni (auth_data) qabul qiladi.
Uni tekshirish uchun controllerga uzatadi.
Javob sifatida foydalanuvchi JWT tokenini va profil ma’lumotlarini qaytaradi.
2️⃣ Controller layer (auth_controller)
Vazifa: 
Telegramdan kelgan ma’lumotni (id, username, first_name, photo_url, auth_date, hash) qabul qiladi.
telegram_auth servisi orqali imzo (hash) to‘g‘riligini tekshiradi.
Agar foydalanuvchi mavjud bo‘lsa → ma’lumotlarni yangilaydi.
Aks holda → yangi foydalanuvchi yaratadi.
So‘ngra JWT token yaratadi va foydalanuvchiga qaytaradi.
3️⃣ Service layer (telegram_auth)
Vazifa: 
Telegram login imzosini (hash) tekshiradi.
BOT_TOKEN orqali secret_key hosil qiladi.
Telegramning rasmiy algoritmi bo‘yicha ma’lumotni tasdiqlaydi.
Faqat to‘g‘ri bo‘lsa controllerga “auth success” statusini yuboradi.
4️⃣ Database layer (user_model, connection)
Jadval: users
Maydonlar: 
id — Auto increment
telegram_id — Unique Telegram foydalanuvchi ID
username
first_name
photo_url — Telegram rasmi
auth_date — Oxirgi login vaqti
jwt_token — Mavjud aktiv token
balance_usd — Hisobdagi mablag‘
sent_mb — Yuborilgan trafik
used_mb — Sotilgan trafik
5️⃣ JWT Manager (utils/jwt_manager)
Vazifa: 
JWT token yaratish va tekshirish.
Token ichiga telegram_id, username, exp_time kiritiladi.
Token muddati tugaganda qayta login talab qilinadi.
6️⃣ Config layer
.env dan quyidagi ma’lumotlarni oladi: 
TELEGRAM_BOT_USERNAME
TELEGRAM_BOT_TOKEN
JWT_SECRET
DATABASE_URL
7️⃣ Response format
Muvaffaqiyatli login uchun:
{ "status": "success", "user": { "telegram_id": "123456789", "username": "john_doe", "first_name": "John", "photo_url": "https://t.me/i/userpic.jpg", "balance_usd": 0.00 }, "token": "eyJhbGciOiJIUzI1NiIs..." } 
Xatolikda:
{ "status": "error", "message": "Invalid Telegram signature" } 
⚙️ Backend oqimi (jarayon)
Foydalanuvchi “Login with Telegram” bosadi.
Telegram widget foydalanuvchi ma’lumotlarini auth_data bilan backendga yuboradi.
Backend telegram_auth servisi orqali imzoni tekshiradi.
Foydalanuvchi bazada borligini tekshiradi: 
Yo‘q bo‘lsa → yangi yozuv yaratadi.
Bor bo‘lsa → mavjud ma’lumotlarni yangilaydi.
JWT token yaratiladi.
Frontendga foydalanuvchi ma’lumotlari + token qaytariladi.
Foydalanuvchi dashboard sahifasiga yo‘naltiriladi.

Dashboard sahifasi uchun foydalanuvchi oqimi (UX Flow) va unga mos backend jarayon tuzilmasi (arxitekturani)
🧭 🏠 Dashboard — UX Flow & Backend tuzilmasi
🎯 Umumiy maqsad
Dashboard foydalanuvchining profil ma’lumotlari, balans, trafik faoliyati va real vaqt statistikasini bir joyda ko‘rsatadi.
Backend esa bu ma’lumotlarni rejalashtirilgan va real-vaqt yangilanish orqali taqdim etadi.
⚙️ Asosiy API endpointlar
API manzilMaqsadTavsif/api/dashboard/<telegram_id>Dashboard ma’lumotlarini olishProfil, balans, trafik, narx, mini-statistika/api/traffic/startTrafik almashishni boshlashAgent ishga tushadi, real vaqt hisob boshlanadi/api/traffic/stopTrafik jarayonini to‘xtatishAgentni to‘xtatadi, MB log bazaga yoziladi/api/user/balanceBalansni tekshirishJoriy balansni qaytaradi/api/pricing/todayBugungi narxni olishAdmin paneldagi narx API dan olinadi/api/notifications/liveWebSocket real-time yangilanishlarTrafik hajmi, balans o‘zgarishi va status yangiliklari 
🧩 Dashboard Backend komponentlari
1️⃣ dashboard_controller
Foydalanuvchi so‘rovini qabul qiladi (telegram_id bo‘yicha).
dashboard_service orqali barcha ma’lumotlarni yig‘adi.
Javobni bitta strukturali JSON’da qaytaradi: 
Profil
Balans
Trafik
Narx
Mini statistik ma’lumot
2️⃣ dashboard_service
Manbalar: 
user_model (foydalanuvchi ma’lumotlari)
traffic_log_model (kunlik trafik va daromad)
pricing_service (bugungi narx)
Hisoblaydi: 
Qolgan trafik (sent_mb - used_mb)
So‘nggi 7 kunlik o‘rtacha daromad
Real vaqt progress foizi (trafik ishlatilish ulushi)
3️⃣ traffic_service
START / STOP tugmalarini boshqaradi.
START → tarmoq monitoringini ishga tushiradi.
STOP → seansni to‘xtatadi va traffic_log_modelga yozadi.
Yuborilgan va ishlatilgan trafiklarni real vaqt API (WebSocket) orqali uzatadi.
4️⃣ pricing_service
Admin tomonidan belgilangan yoki tashqi API’dan olingan “Bugungi trafik narxi ($/GB)” ni qaytaradi.
Kesh mexanizmi orqali har 24 soatda yangilanadi.
5️⃣ websocket_manager
Trafik oqimini real vaqtda kuzatish uchun ishlatiladi.
START bosilganda WebSocket kanal ochiladi: 
Har 3 sekundda: 
used_mb
current_speed
balance_usd o‘zgarishlari yuboriladi.
STOP bosilganda kanal yopiladi.
6️⃣ traffic_log_model
Har bir sessiya uchun trafik ma’lumotlarini saqlaydi: 
session_id
telegram_id
start_time
end_time
sent_mb
used_mb
earned_usd
🧠 Dashboard yuklanish oqimi (UX Flow)
🔹 1. Sahifaga kirish
Foydalanuvchi login holatida sahifaga kiradi.
Frontend GET /api/dashboard/<telegram_id> so‘rovini yuboradi.
🔹 2. Backend javobi
Backend quyidagi ma’lumotlarni qaytaradi:
profil: rasm, ism, username, oxirgi login
balance_usd: joriy mablag‘
price_per_gb: bugungi narx
traffic: sent_mb, used_mb, qolgan hajm
mini_stats: kunlik va haftalik daromad
🔹 3. Real vaqt monitoring
Foydalanuvchi START bosganda:
/api/traffic/start → sessiya boshlanadi
WebSocket ochiladi → trafik hisoblash real vaqtda ketadi
Har 3s da balans va trafik yangilanadi
STOP bosilganda:
/api/traffic/stop → seans to‘xtaydi
Oxirgi qiymatlar bazaga yoziladi
WebSocket yopiladi
🔹 4. Balans yangilanishi
Balans har 10 soniyada avtomatik balance_usd yangilanadi.
Yangi daromad tushsa → frontendda “+$0.02” animatsiyasi chiqadi.
🔹 5. Tugmalar holati
Faqat bitta holat aktiv bo‘ladi: 
Agar “START” ishga tushgan bo‘lsa → faqat “STOP” ko‘rinadi.
Agar to‘xtatilgan bo‘lsa → faqat “START” aktiv bo‘ladi.
🧩 Response formati (umumiy tuzilma)
{ "user": { "telegram_id": "12345", "first_name": "Dilshod", "username": "@dilshod_uz", "photo_url": "https://t.me/i/userpic.jpg", "auth_date": "2025-11-02T10:14:00" }, "balance": { "usd": 5.70, "converted_usdt": 5.70, "converted_uzs": 72000 }, "traffic": { "sent_mb": 4000, "used_mb": 3300, "remaining_mb": 700 }, "pricing": {

“📢 Kunlik Narx E’loni (Daily Price Announcement)” yoki moduli uchun backend tuzilma arxitekturasini quyidagicha belgilaymiz. Bu tuzilma butun backend tizim bilan to‘liq moslashgan
🗂 1️⃣ Model: models/daily_price_model.py
Ma’lumotlar bazasi jadvali: daily_price
Ustun nomiTipiTavsifidINT (PK, AutoIncrement)Unikal IDdateDATENarx amal qiladigan sanaprice_per_gbFLOAT(5,2)1 GB uchun narx (USD)messageTEXTAdmin izohiupdated_atDATETIMESo‘nggi o‘zgarish vaqti 

🔸 Jadval har kuni bitta satr saqlaydi (unique date constraint bilan).

⚙️ 2️⃣ Service Layer: services/daily_price_service.py
Vazifasi:
So‘nggi narxni DB’dan olish
Admin kiritgan yangi narxni saqlash
O‘zgarish aniqlansa — price_update_notifier chaqirish
Avvalgi narx bilan solishtirish (dashboard uchun)
🌐 3️⃣ API Layer: routes/daily_price_api.py
🔹 GET /api/daily_pric
e
Dashboard sahifasi shu endpointni har 5 daqiqada chaqiradi
.
Response:
{ "date": "2025-11-02", "price_per_gb": 1.65, "message": "Bugungi narx: $1.65/GB (haftalik aksiyada!)", "change": "+0.15" } 
🔹 POST /api/admin/daily_pr
ice
Admin tomonidan yangi narx kiritish uch
un.
Auth token talab qiladi.
Yangi narx kiritilganda price_update_notifier ishga tushadi.
🧰 4️⃣ Notification tizimi: tasks/price_update_notifier.py
Integratsiyalar:
🔔 Firebase Cloud Messaging (mobil ilovalar uchun)
🤖 Telegram Admin bot (masalan, admin kanaliga: “Bugungi narx yangilandi!”)
📨 Email orqali xabarnoma (ixtiyoriy)
📊 5️⃣ Admin Panel qismi: admin/daily_price_admin.py
Funksiyalar:
Joriy narxni ko‘rish
Yangi narx qo‘shish (sana, qiymat, xabar)
Avvalgi narxlar tarixini ko‘rish
Xabar jo‘natishni faollashtirish (checkbox orqali: "Push yuborilsin ✅")
📅 6️⃣ Frontend bilan aloqa
Dashboard banner har safar /api/daily_price ni chaqiradi.
API chaqiriqlari:
Har 5 daqiqada avtomatik (background polling)
Yoki foydalanuvchi “Pull to refresh” qilganda
🧩 7️⃣ Kelajak kengaytirish imkoniyatlari
Qo‘shimcha modulTavsifiprice_history_api.pySo‘nggi 7/30 kunlik narxlar grafigi uchun APIprice_prediction.pyAI model orqali narx trendi prognoziprice_alerts.pyFoydalanuvchi narx chegarasi o‘rnatganda ogohlantirish yuborish 
🪶 8️⃣ Ma’lumot oqimi diagrammasi (simplified)
Admin → POST /api/admin/daily_price ↓ DB (daily_price) ↓ price_update_notifier.py → (Firebase / Telegram) ↓ Frontend (Dashboard) ↓ GET /api/daily_price 
Agar xohlasangiz, men shu tuzilma asosida to‘liq backend kodlarini (model, route, service, notifier) ishlab chiqaman (Flask yoki FastAPI formatida) — sizga faqat framework tanlash kerak bo‘ladi.

Push Notification Tool (FCM) moduli uchun backend arxitektura tuzilmasi Quyidagi tuzilma avvalgi “Daily Price Announcement” moduli bilan integratsiyalashgan, lekin mustaqil ishlay oladi.
🧱 BACKEND TUZILMA — push_notification MODULI


🗂 1️⃣ Model: models/user_model.py
users jadvaliga qo‘shimcha ustunlar:
Ustun nomiTipiTavsifdevice_tokenVARCHAR(255)Firebase token (unikal)notifications_enabledBOOLEANFoydalanuvchi push’ni yoqqanmi (1/0)last_seenDATETIMEOxirgi kirish vaqti (segmentlash uchun) 

Tokenlar har 30 kunda avtomatik yangilanadi.
last_seen segmentlashda ishlatiladi (“so‘nggi 3 kunda aktiv foydalanuvchilar”).

🌐 2️⃣ API Layer: routes/notification_api.py
🔹 POST /api/register_device
Foydalanuvchi ilovaga kirganda device_token yuboradi.
Request:
{ "telegram_id": 523414231, "device_token": "fcm_eb3a8ef9as3f2...", "notifications_enabled": true } 
Response:
{ "status": "success", "message": "Device token registered successfully" } 
🔹 POST /api/push/send
Admin yoki tizim (masalan, daily_price moduli) orqali chaqiriladi.
Request:
{ "title": "📢 Kunlik narx yangilandi!", "body": "Bugungi narx: $1.65 / GB — 10% oshdi!", "type": "daily_price" } 
Response:
{ "sent": 1245, "failed": 3 } 
⚙️ 3️⃣ Service Layer: services/notification_service.py
Vazifalari:
Foydalanuvchilarning device_tokenlarini DB’dan olish
notifications_enabled = 1 bo‘lganlarga push yuborish
FCM REST API orqali POST https://fcm.googleapis.com/fcm/send yuborish
Xato tokenlarni tozalash
Yuborish jarayonini log faylga yozish
Qo‘shimcha imkoniyatlar:
Segmentlash: “so‘nggi 7 kunda aktiv bo‘lganlar”
Silent push (ma’lumotni yangilaydi, lekin banner chiqmaydi)
🔁 4️⃣ Worker Layer: tasks/notification_worker.py
Fon jarayon (background task):
Admin yangi narx kiritsa yoki balans o‘zgarsa, bu worker ishga tushadi.
notification_service dan foydalanib, 1000 tadan tokenni bo‘lib yuboradi.
Har batch uchun FCM send so‘rov yuboriladi (async queue orqali).
Fayl nomlari:
notification_queue.json — yuboriladigan push’lar ro‘yxati
notification_log.json — yuborilganlar statistikasi
🧩 5️⃣ Device Registration Service: services/device_registration.py
Vazifasi:
Tokenni DB’da saqlash yoki yangilash
Foydalanuvchi notifications_enabled qiymatini o‘zgartirsa, uni qayd etish
Eski tokenlarni 30 kundan so‘ng o‘chirish
🧠 6️⃣ Integration Flow
(1) Foydalanuvchi ilovaga kiradi ↓ register_device() → token saqlanadi ↓ (2) Admin narxni yangilaydi (POST /api/admin/set_price) ↓ daily_price_service → notification_service ↓ notification_worker → FCM ↓ (3) Foydalanuvchiga push yetib boradi 
🔒 7️⃣ Xavfsizlik va boshqaruv
ElementTavsifFCM_SERVER_KEYcore/config.py ichida saqlanadiToken yangilanishiHar 30 kunda avtomatikAPI authetifikatsiyaAdmin uchun Bearer TokenLoggingHar yuborilgan push log faylga yoziladiRate limitSekundiga 1000 token yuborish chegarasi 
📈 8️⃣ Kelajak kengaytirish imkoniyatlari
Qo‘shimcha modulTavsifnotification_history.pyHar foydalanuvchiga yuborilgan push tarixini saqlaydinotification_template.pyOldindan tayyor push shablonlarianalytics_push.pyQabul qilingan/ochilgan push statistikasi (CTR)unsubscribe_watcher.pyPush o‘chirgan foydalanuvchilarni kuzatuvchi skript 
🗺️ 9️⃣ Push Notification tizimi oqimi
Admin → POST /api/admin/set_price ↓ daily_price_service ↓ notification_service.send_push_to_all() ↓ Firebase Cloud Messaging ↓ Mobil ilova (Android) ↓ Dashboard sahifasi yangilanadi

Zo‘r — hozir sizga to‘liq, production-ready “Traffic Start Filter & Admin Bypass” tool arxitekturasini kodsiz, lekin texnik jihatdan aniq va bajariladigan shaklda taqdim etaman.
Bu hujjat orqali backend jamoasi funksiyani to‘liq amalga oshira oladi: komponentlar, endpointlar, DB o‘zgartirishlari, ketma-ketliklar, konfiguratsiya, monitoring, test scenariylari va admin override oqimi.
📚 Nomi: Traffic Start Filter & Admin Bypass Tool
Maqsad:
Foydalanuvchi START bosganda sessiyani faqat ruxsat etilgan shartlar (VPN/proxy yo‘qligi, IP mintaqasi — faqat US/EU, mobile yoki home Wi-Fi) bajarilganda ochish. Adminlar esa bu cheklovlardan mustasno (bypass).
🧩 Umumiy komponentlar (high-level)
API Gateway / Auth
JWT tekshiruvi → foydalanuvchi identifikatsiyasi (telegram_id, role).
Traffic Filter Service (filter_service)
Orkestrator: barcha tekshiruvlarni ketma-ket boshqaradi va yakuniy qarorni qaytaradi.
IP Reputation Adapter (ip_reputation)
3rd-party integratsiyalar uchun wrapper (MaxMind, IPQualityScore, ipinfo, AbuseIPDB).
GeoIP Service (geo_service)
IP → country, region, ASN, ISP ma’lumotlarini beradi (MaxMind/DB yoki API).
Network Detector (network_detector)
Clientdan kelgan network_type (mobile/wifi) va ASN/ISP asosida tekshiradi.
Session Policy Engine (session_policy)
Qoidalar to‘plami (vpn_score_threshold, allowed_regions, allowed_network_types). Qaror qabul qiladi.
Audit & Logging (filter_audit)
Har tekshiruv natijasi saqlanadi (forensics & support).
Admin Override / Manual Review
pending_admin_approval holati va admin dashboard for review/approve.
Cache (Redis)
IP tekshiruv natijalarini kesh qilish (TTL konfiguratsiya).
Edge / Tunnel Controller
Backenddan OK olgachgina tunnel/edge node boshqaruvi.
Notifier (optional)
Fail haqida foydalanuvchiga aniq sababli xabar yuboradi.
🗂 Fayl / modul tuzilmasi (sug‘urta)
modules/ └── traffic_filter/ ├── api/ # endpointlar (traffic/start) │ └── start_controller ├── services/ │ ├── filter_service.py # orchestrator (checks sequence) │ ├── ip_reputation.py # third-party wrapper │ ├── geo_service.py # MaxMind/ip-api wrapper │ ├── network_detector.py # network type inference │ └── session_policy.py # rules engine ├── models/ │ ├── traffic_sessions.sql # session table DDL │ └── filter_audit.sql # audit table DDL ├── cache/ │ └── ip_cache_adapter.py # redis caching logic ├── admin/ │ └── manual_review.py # admin override flows └── utils/ └── validators.py 

(fayl nomlari tushunchaviy — kod yozish bosqichida konkret nomlanadi)

🗄 Ma’lumotlar bazasi (DDL qo‘shimchalar)
1) traffic_sessions — (mavjudga qo‘shimchalar)
Qo‘shimcha ustunlar: 
user_role VARCHAR(16) DEFAULT 'user' — 'user' yoki 'admin'
filter_status VARCHAR(32) DEFAULT 'pending' — 'pending'|'passed'|'failed'|'skipped'
filter_reasons JSON DEFAULT NULL — misol: ["vpn_detected","region_not_allowed"]
ip_country CHAR(2) — ISO code
ip_asn VARCHAR(64)
is_proxy BOOLEAN
vpn_score FLOAT
network_type_client VARCHAR(16) — 'mobile'|'wifi'|'unknown'
network_type_asn VARCHAR(32)
validated_at TIMESTAMP
2) filter_audit — yangi jadval (har tekshiruv uchun)
Columns:
id PK
session_id FK -> traffic_sessions.id (nullable until session created)
telegram_id
device_id
client_ip (public)
asn, country, isp
is_proxy, vpn_score
network_type_client, network_type_asn
check_sequence JSON (ketma-ket natijalar)
final_decision ENUM('allow','deny','pending_admin')
reasons JSON
admin_override_by (nullable)
created_at
🔗 API Endpointlar (contract / OpenAPI-style, kodsiz)
POST /api/traffic/start
Auth: Bearer JWT required.
Body (JSON):
{ "device_id": "string", "client_local_ip": "192.168.1.10", "network_type": "mobile", // mobile | wifi | unknown "app_version": "1.2.0", "os": "Android", "battery_level": 78 } 
Process:
Identify user from JWT (telegram_id, role).
If admin → skip filters, mark filter_status='skipped', create session, return 200 OK {session_id, bypass:true}.
If user → run filter_service checks. Success response:
{ "status":"ok", "session_id":"sess_123", "message":"Tunnel opened" } 
Fail response:
{ "status":"blocked", "reasons":["vpn_detected","region_not_allowed"], "message":"Tunnel could not be opened." } 
Pending admin response (rare):
{ "status":"pending_admin", "ticket_id":"ra_456", "message":"Awaiting admin approval." } 
GET /api/filter/audit/{session_id} (admin-only)
Returns audit trail for a session.
POST /api/admin/filter/override/{ticket_id} (admin-only)
Manual approve/reject with note.
✅ Tekshiruvlar ketma-ketligi (filter_service)
Auth & Role check
From JWT: get telegram_id, role.
Log user_role in session row.
IP resolution
Determine public IP (from X-Forwarded-For or edge control header).
If missing → reject with ip_unknown.
Cache lookup (Redis)
If ip_cache.exists(public_ip) → use cached {country,asn,is_proxy,vpn_score}.
GeoIP lookup (geo_service)
country, region, asn, isp.
IP Reputation (ip_reputation)
is_proxy, is_datacenter, vpn_score, tor_flag.
Network detector
Compare client network_type header with ASN-inferred network type.
If mismatch → suspicious_network.
Policy evaluation (session_policy)
Apply rules: 
Allow if country in ALLOWED_REGIONS (US + EU list).
Deny if is_proxy=true or vpn_score > threshold (configurable).
Deny if network_type_client not in allowed types (mobile,wifi).
If borderline (vpn_score between warn_threshold and block_threshold) → mark pending_admin (configurable).
Admin whitelist exceptions allowed here.
Logging/Audit
Save detailed filter_audit entry with all checks and raw third-party responses.
Decision
allow → create traffic_session with filter_status=passed.
deny → return error with reasons.
pending_admin → create session with filter_status='pending' and create admin ticket.
Edge interaction
If allow → reply OK; Edge/Tunnel controller starts.
If deny → send message to client UI with human-readable reason.
⚙️ Konfiguratsiya / Policy (session_policy) — administrator sozlamalari
Yuqori darajadagi sozlamalar (admin paneldan o‘zgartiriladi):
ALLOWED_REGIONS = ["US"] + EU_COUNTRIES_LIST
VPN_SCORE_BLOCK_THRESHOLD = 70 (0..100)
VPN_SCORE_WARN_THRESHOLD = 50
BLOCK_IF_PROXY = true
ALLOWED_NETWORK_TYPES = ["mobile", "wifi"]
CACHE_TTL_IP = 86400 (redis seconds)
ADMIN_WHITELIST_ASNS = [list] (datacenter/isp lar uchun exceptions)
FAILURE_ACTION = "deny" (deny | pending_admin)
ADMIN_BYPASS = true (always true)
MAX_START_ATTEMPTS_BEFORE_LOCK = 5 per user per day
🔐 Admin bypass behaviour (anig‘lash)
is_admin(user) returns true if any of identifiers match admin list.
For admin users: 
Skip all checks.
filter_status = 'skipped', filter_reasons = ['admin_bypass'].
Session created and logged.
Admin actions still audited (admin_id recorded).
🧪 Test & QA scenariylari (majburiy)
Happy path (user from US mobile, no proxy)
Expect: allow, session created, filter_status=passed.
VPN detected (user)
Expect: deny with reason vpn_detected.
Proxy detected (user)
Expect: deny with is_proxy=true.
Non-US/EU country (user)
Expect: deny region_not_allowed.
Network mismatch (client says mobile, ASN is datacenter)
Expect: deny or suspicious_network.
Borderline vpn_score between warn & block
According to config: pending_admin created.
Admin login from any IP
Expect: bypass, session created with filter_status=skipped.
Repeated attempts (rate limit)
After MAX_START_ATTEMPTS_BEFORE_LOCK → temporary block; admin alerted.
Cache correctness
Update IP reputation in third-party, ensure cache invalidation TTL honored.
📈 Monitoring & Alerting
Metrics to emit:
filter.requests_total
filter.requests_allowed
filter.requests_denied
filter.requests_pending_admin
filter.avg_latency_ms (3rd-party calls)
filter.top_block_reasons (labels)
Alerts:
Spike in requests_denied (> threshold) → page ops.
Many pending_admin tickets → examine thresholds.
Third-party API error rate increase → degrade gracefully using cache and fallback.
Dashboards:
Live chart: allow/deny counts per minute.
Map: blocked countries heatmap.
Table: top ASNs causing denies.
🔁 Fallbacks & Resiliency
If third-party IP reputation API fails:
Use cached result if present.
If no cache, apply conservative policy (deny or pending) depending on FAILURE_ACTION.
Emit alert about provider failure.
Rate-limiting 3rd-party calls:
Batch lookups for same ASN/IP.
Use Redis as queue and worker to async-check newly seen IPs, allow initial START with pending_async_check? (configurable — prefer synchronous deny to prevent abuse).
🧾 Error codes (client-friendly)
403_vpn_detected — VPN or proxy detected.
403_region_not_allowed — IP country not in allowed regions.
403_network_mismatch — Network type mismatch (client vs ASN).
403_datacenter_ip — Datacenter IP detected.
429_too_many_attempts — Rate limit / too many start attempts.
202_pending_admin — Waiting admin approval (include ticket_id).
Client UI should map these to human messages.
🛠 Admin tools & UX
Manual override UI
Show filter_audit details.
Buttons: Approve / Reject / Whitelist ASN / Add exception.
Whitelist management
Manage ADMIN_WHITELIST_ASNS, allowlisted_ips.
Review queue
Pending admin reviews table with search & filters.
Logs
Export filter_audit rows for legal / compliance.
🔐 Security & Privacy best practices
Store third-party API keys in secrets manager (Vault).
Mask IP in logs unless required; keep GDPR compliance (if applicable).
Limit retention of filter_audit (e.g., 30–90 days) per policy.
All admin actions logged with admin_id & timestamp.
✅ Implementation rollout plan (recommended phases)
Phase 1 — Basic checks & cache
Implement role detection & admin bypass.
Implement GeoIP check + allowed regions.
Implement Redis caching for IP lookups.
Implement simple deny on non-US/EU.
Phase 2 — IP reputation & network detection
Integrate MaxMind / IPQualityScore.
Add proxy/vpn detection and vpn_score thresholds.
Phase 3 — Admin override & UI
Create pending_admin queue & admin dashboard for manual approvals.
Phase 4 — Hardening
Monitoring, rate-limits, fallback behaviour tunings.
Phase 5 — Optimization
Batch lookups, edge-side prechecks, reduce latency.
📌 Yakuniy tavsiyalar
VPN_SCORE_BLOCK_THRESHOLD ni dastlab 70 qilib boshlang va 2 haftada real-dunyo ma’lumotiga qarab sozlang.
Qoida: bloklashdan oldin warn holatni (pending_admin) ko‘proq ishlatish ma’qul, keyin qat’iylashtiring.
Har qanday deny holati foydalanuvchiga aniq, oddiy sababi bilan ko‘rsatilishi kerak (masalan: “Tunnel ochilmadi — siz VPN yoki proxy orqali ulanayotgansiz.”).
“Real-vaqt sessiya UI + Periodic summary (silent push / local notif) + Telemetry & Reconciliation” uchun toʻliq backend tuzilmasi (kodsiz, amalga oshirishga tayyor) tayyorlab berdim. Hamma qism ilovangiz (Android) va oldingi modul(lar) bilan mos ishlashi uchun loyihalashtirildi.
Quyidagi hujjat: komponentlar, endpointlar, maʼlumot oqimi, kechikuv/interval tavsiyalari, xavfsizlik/privatlik qoidalari, monitoring va UX copy hamda default parametrlar toʻliq keltirilgan.
1 — Umumiy maqsad (summary)
Agar ilova ochiq boʻlsa → real-vaqt UI (top-of-screen / in-app) hisoblanadi (Android: ongoing notification + foreground service; iOS: in-app panel).
Agar ilova background yoki toʻliq yopiqligida → server silent push (data-only) yuboradi, ilova uygʻonib local notification orqali periodic summary ko‘rsatadi (1 yoki 5 daqiqalik interval).
Har sessiya davomidagi hajmni ilova mahalliy hisoblaydi (VpnService / packet tunnel). Server authoritative bo‘lib, ilovadan keladigan periodik heartbeat/report larni yigʻadi va reconciliation qiladi.
Push faqat muhim voqealar uchun (threshold, stop, balance change).
2 — Arxitektura (high-level)
Clients: - Mobile (Android: foreground service + FCM) - Mobile (iOS: in-app UI + silent push / local notif) - PWA (Service Worker + Web Push) Backend: - API Gateway (auth) - Telemetry Service (ingest reports, heartbeat) - Session Service (create/update/end sessions) - Notification Service (FCM adapter, APNs adapter, Web Push) - Reconciliation Worker (batch / streaming) - Metrics & Monitoring (Prometheus + Grafana) - Cache (Redis) - DB (Postgres / MySQL) - Queue (Redis Streams / Celery) 
3 — Maʼlumotlar bazasi (entiities, qisman)
sessions
id, telegram_id, device_id, start_time, end_time, is_active, local_counted_mb (client reported cumulative), server_counted_mb (aggregated), last_report_at, estimated_earnings, status
session_reports
id, session_id, timestamp, delta_mb, speed_mb_s, battery_level, network_type, ip, raw_meta
notifications_log
id, telegram_id, device_id, notif_type, title, body, sent_at, delivered, opened
device_registry
telegram_id, device_id, fcm_token, platform (android/ios/web), notifications_enabled, last_seen
4 — Asosiy endpointlar (conceptual)
POST /api/traffic/start — START (auth, create session)
POST /api/traffic/report — Periodic report / heartbeat (device → server)
Body: { session_id, device_id, cumulative_mb, delta_mb, speed, battery_level, network_type, timestamp }
POST /api/traffic/heartbeat — light ping if no data to keep alive
POST /api/traffic/stop — STOP (close session, final reconciliation)
GET /api/session/{session_id}/summary — server aggregate summary (frontend calls on resume or detail view)
POST /api/device/register — device token register (fcm/apns)
POST /api/notifications/ack — notification open/ack events (for analytics)
5 — Telemetry ingestion & reconciliation lojikasi
5.1 Lokal hisoblash (client authoritative for instant UI)
Ilova (VpnService / packet tunnel) har soniya/har X operasiyada local cumulative bajara boshlaydi.
Notification data (ongoing) ilovada toʻgʻridan-toʻgʻri shu local qiymatga asoslanadi — minimal kechikuv.
5.2 Serverga reporting (authoritative persistence)
Ilova POST /api/traffic/report yuboradi: har 10 s yoki har 100 MB (qaysi biri avval bo‘lsa).
Server bu reportlarni Redis stream yoki DB ga yozadi (session_reports).
Reconciliation worker: 
Har report qabul qilingach, server_counted_mb += delta_mb atomic tarzda yangilanadi.
Agar abs(local_count - server_count) > threshold (masalan 1% yoki 5 MB) → reconciliation procedure (log + eventual correction).
Session stop bo‘lganda final reconciliation va earned_usd hisoblanadi (price_per_gb ga asoslanadi).
5.3 Konflikt va idempotency
Har reportda sequence_number yoki cumulative_mb bo‘lsin — worker duplicate yoki out-of-order holatlarni aniqlaydi.
Reports idempotent: same sequence_number ikkinchi marta kelganda inkor qilinadi.
6 — Notification qancha va qachon yuboriladi (server taraf)
6.1 Real-time in-app updates:
Ilova ochiq bo‘lsa → serverga real-time push kerak emas; ilova o‘zdan local UI yangilaydi. Biroq admin/other clients uchun WebSocket → server → dashboard real-time metrics yuboriladi.
6.2 Ongoing notification (Android)
Ilova VpnService orqali local notificationni 1–3 s intervalda yangilaydi (device tarafida). Backendga bu changelar tezda kerak emas — lekin har 10 s report qilinadi.
6.3 Silent push → local summary (Background)
Agar ilova background bo‘lsa: 
Server Notification Service data-only push (FCM/APNs silent) yuboradi: payload ichida summary aggregate (last N reports aggregated on server).
Ilova uygʻonadi va local notification yaratadi (summary).
Interval: default 1 yoki 5 daqiqada (iOS chekloviga mos ravishda 5min tavsiya).
Apple: silent push kafolatlanmaydi — fallback: agar silent push yetmasa, keyingi pull on resume’da GET /api/session/{id}/summary chaqiradi.
6.4 Muvofiq voqealar (event-driven push)
Threshold reached (100 MB, 500 MB, yoki user-configured)
Balance updated (session earnings credited)
Session stopped / failure detected
Admin message (urgent)
7 — Notification payload & UX flow (server → client)
Data-only push payload (FCM example):
{ "data": { "type": "session_summary", "session_id": "sess_123", "delta_mb": "120", "total_mb": "1240", "estimated_earnings": "0.002", "timestamp": "2025-11-02T12:00:00Z" } } 
Ilova bu maʼlumotni qabul qilib local notification hosil qiladi yoki in-app panelni yangilaydi.
Local notification copy (oʻzbekcha, qisqa):
Title: 📡 Trafik ulashish: faol
Body: Yuborilgan: 1.24 GB • Tezlik: 0.45 MB/s
Summary (periodic): So‘nggi 5 daqiqada 120 MB yuborildi. Jami: 1.24 GB. Taxminiy daromad: $0.002.
Tugma harakati: notification tap → ilova ochiladi → GET /api/session/{id}/summary va real-time view ko‘rsatiladi.
8 — Platform-specific cheklovlar va strategy
Android
Foreground service + ongoing notification: live updates 1–3 s.
Permission: FOREGROUND_SERVICE va notification runtime perms.
Default realtime update: 3 s (battery_saver → 10–30 s).
iOS
In-app real-time panel (recommended) — local updates as app is foreground.
Silent pushes: data-only + local notification summary (interval 1 or 5 min; Apple may throttle).
Fallback: Background fetch / on resume GET /api/session/{id}/summary.
PWA / Web
Service Worker + Web Push for summary.
If tab closed → push only; cannot guarantee immediate UI update.
9 — Security & Privacy qoidalari
FCM / APNs keys faqat backendda saqlansin (Vault).
Device tokens DB da encrypted formatda saqlansin.
Reports da trafikka oid content saqlanmasin — faqat hajm, tezlik, IP metadata (anonymized) saqlansin.
User consent: notification content (balans yoki pul ko‘rsatkichlarini) ko‘rsatish uchun foydalanuvchidan ruxsat (toggle).
Rate limit: device → report bo‘yicha per-device per-minute limit (masalan, 6–12 reports/min).
Auth: har endpoint JWT bilan himoyalansin; reports HMAC signed (optional) for integrity.
10 — Reconciliation & earnings finalization
Server server_counted_mb ga asoslanadi earnings hisoblashda; lokal va server oʻrtasida ziddiyat bo‘lsa: 
Xatolik logsga yoziladi, userga notify qilinadi: “Hisoblashda tafovut aniqlandi — yakuniy balans session endida tasdiqlanadi.”
Final earn calculation: 
earned_usd = server_counted_mb / 1024 * price_per_gb (MB→GB conversion consistent)
Payment eligibility: balance >= min_withdraw va withdraw API mavjud.
11 — Monitoring & Observability
Emit metrics: 
reports_ingested_total, reports_latency_ms, reconciliation_errors_total, silent_push_sent, silent_push_failures.
Dashboards: 
Active sessions, reports per minute, average latency between client report and server ingestion, silent push success ratio (deliveries).
Alerts: 
Silent push failure rate high → investigate APNs/FCM keys or token expirations.
Reconciliation errors spike → possible client bug or network/time sync problems.
12 — Default parametrlar (recommended)
Local notification update interval (Android): 3 s
Server report interval: 10 s OR every 100 MB (whichever comes first)
Summary silent push interval (background): 1 min (if possible) or 5 min for iOS fallback
Reconciliation tolerance: max(1% , 5 MB)
Rate limit: <= 12 reports / min / device
Token refresh: device should reregister FCM token every 30 days (or on token change)
13 — UX snippets (oʻzbekcha, ilova foydalanishi uchun)
Ongoing notification (short):
📡 Trafik ulashish — Faol
Yuborilgan: 1.24 GB • Tezlik: 0.45 MB/s
Buttons: [STOP] [OPEN APP]
Periodic summary (local):
🧾 Sessiya yangiligi
So‘nggi 5 daqiqada: 120 MB. Jami: 1.24 GB. Taxminiy: $0.002.
On tap action: ilova ochiladi → Dashboard / Session view (server summary + realtime)
STOP confirmation:
To‘xtatish bilan hozirgi sessiya hisoblanadi. Davom etilsinmi? [Bekor qil] [To‘xtat]
14 — Amalga oshirish bosqichlari (qa-ish reja)
Device registration & basic report ingestion (POST /report)
Local ongoing notification wiring (client) + server report handling
Reconciliation worker & idempotency logic
Silent push pipeline (FCM/APNs) + local notification on device
iOS fallback tuning (5 min) and PWA support
Monitoring, alerts, and UX polish


“💳 BALANCE sahifasi uchun backendning toʻliq, ishlab chiqarishga tayyor tuzilmasini (kodsiz) taqdim etaman. Hamma narsa ilovadagi UI va oldingi modullar bilan toʻliq mos ishlashi uchun loyihalashtirilgan: endpointlar, DB strukturalari, xizmatlar, oqimlar, xavfsizlik va bildirishnomalar.
Quyida hamma jihatlarni bosqichma-bosqich keltirdim — siz yoki backend jamoangiz shu hujjat asosida barvaqt implementatsiya boshlay oladi.
🔎 Umumiy maqsad
Balance sahifasi foydalanuvchiga uning hisob holatini, yuborilgan/ishlatilgan trafikni, tranzaksiya tarixini va yechish opsiyasini ko‘rsatadi. Backend esa balansni hisoblash, yangilash, tranzaksiyalarni boshqarish va bildirishnomalarni yuborish uchun mas’ul. 
🗃️ Ma’lumotlar bazasi (DDL — zarur jadvallar va ustunlar)
1) users (mavjud)
Qo‘shimchalar (agar yo‘q bo‘lsa):
balance_usd NUMERIC(18,6) DEFAULT 0
sent_mb BIGINT DEFAULT 0
used_mb BIGINT DEFAULT 0
device_token TEXT (FCM), notifications_enabled BOOL
last_balance_refresh TIMESTAMP
2) transactions — tranzaktsiyalar (income / withdraw)
ustunturitavsifidBIGSERIAL PKtelegram_idBIGINTfoydalanuvchitypeVARCHAR'income' / 'withdraw' / 'refund'amount_usdNUMERIC(14,6)$ miqdoramount_usdtNUMERIC(14,6)USDT ekvivalent (agar kerak)currencyVARCHAR'USD' yoki 'USDT'statusVARCHAR'pending'/'processing'/'completed'/'failed'wallet_addressTEXT(withdraw uchun)provider_payout_idTEXTpayment provider idtx_hashTEXTblockchain tx hashnoteTEXTadmin yoki system notecreated_atTIMESTAMPTZupdated_atTIMESTAMPTZ 
Index: telegram_id, status, created_at.
3) balance_history — (optional) snapshotlar
(Ma'lumot: har bir balance yangilanish uchun snapshot)
user_id, previous_balance, new_balance, delta, reason, created_at
4) pending_chunks va usage_records (sizda mavjud)
Serverda ishlatilgan trafik uchun usage_records bo‘lishi va balance ga qo‘shilishi kerak (shu modul bilan integratsiya).
5) withdraw_requests (agar transactions bo‘lmasa alohida)
(Agar alohida jadval kerak bo‘lsa — transactionsga birlashtirish mumkin.)
🔗 API endpointlar (OpenAPI uslubida — request/response konseptual)
1) GET /api/user/balance/{telegram_id}
Tavsif: foydalanuvchi profil va balans summary qaytaradi.
Response:
{ "user": { "telegram_id": 5234, "first_name": "Dilshod", "username": "dilshod_uz", "photo_url": "...", "auth_date": "2025-11-02T10:14:00Z" }, "balance": { "usd": 12.54, "usdt_equivalent": 11.29, // agar kerak "sent_mb": 184.3, "used_mb": 139.8, "pending_usd": 0.00, "last_refreshed": "2025-11-02T11:00:00Z" }, "today_earn": 0.48, "month_earn": 8.32, "transactions": [ /* last 10 */ ] } 
Auth: JWT (required) — telegram_id must match token (or admin).
2) POST /api/user/refresh_balance
Tavsif: balansni server asosida real-vaqt yangilaydi. (Rate-limited)
Body: { "telegram_id": 5234 }
Process: 
Reconcile usage_records / pending_chunks -> hisoblab balances.balance_usd yangilanadi.
Create transactions entries for new income items (income type).
Response:
{ "status":"success", "new_balance_usd": 12.54, "delta": 0.20 } 
Qoida: throttling — foydalanuvchi 1 daqiqada 1 marta yoki 10s? (recommend: 1x/10s per user; default 1x/30s).
3) GET /api/transactions?limit=10&offset=0
Tavsif: foydalanuvchi tranzaksiya tarixi (paginated).
Response: list of transactions rows.
4) POST /api/withdraw
Tavsif: foydalanuvchi yechish so‘rovi yaratadi.
Body:
{ "telegram_id": 5234, "amount_usd": 5.00, "wallet_address": "0xAbc...123", "network": "BEP20" } 
Process (safety checks): 
Check balance_usd >= amount_usd
Check amount_usd >= MIN_WITHDRAW_USD (1.39)
Check daily_withdraw_limit (per user)
Create transactions row with status = pending
Push job to payout_worker queue
Response:
{ "status":"pending", "transaction_id": 987, "message":"Withdraw request created and queued." } 
5) Admin endpoints (admin-only)
GET /admin/withdraws — list pending withdraws
POST /admin/withdraws/{id}/retry — retry payout
PATCH /admin/users/{id}/adjust_balance — manual adjust (audit logged)
⚙️ Backend xizmatlar va ish oqimi
A) balance_service — vazifalari
get_balance(telegram_id) — snapshot retrieval + last reconciliation state
refresh_balance(telegram_id) — consume usage_records / pending_chunks and update balances table atomically
apply_income(user_id, used_mb, price_at_use) — create transactions(type=income) va balances.balance_usd += amount
reserve_for_withdraw(user_id, amount) — set a hold to prevent double-spend (transactional)
finalize_withdraw(transaction_id, success, tx_hash) — update transaction status, update balances, notify user
B) payout_service (worker)
Payout worker monitors transactions with status='pending'
For each: 
Validate idempotency (unique external id)
Call Payment Provider Adapter (NowPayments / CryptoCloud)
Update transactions with provider_payout_id and status='processing'
Poll webhook or provider status → on completed set status='completed', tx_hash and deduct balance (if not pre-deducted)
On failed set status='failed' and optionally rollback reserved funds
Retries with exponential backoff; admin alert after N failures.
C) reconciliation_service
Periodic job to confirm server_counted_mb vs device reports
At session end, compute earned_usd = SUM(used_mb_i * price_at_use) and create corresponding transactions (income).
Mark pending_chunks consumed.
🔒 Xavfsizlik va transaction qoidalari
Atomicity: balansni yangilash va transaction yaratish bitta DB tranzaksiyasida bo‘lishi kerak (ACID).
Reservation model: Withdraw so‘rovi paytida balance dan pulni reserved qiling (yoki balances.balance_usd -= amount va transactions.status='processing'), shu bilan ikki marta yechish oldini olasiz.
Idempotency: payout API chaqiruvlar uchun idempotency_key yarating (provider tarafida ham qo‘llanadi).
Auth: barcha endpointlar JWT bilan himoyalangan; admin endpointlar role-check bilan.
Rate limiting: POST /api/user/refresh_balance va POST /api/withdraw cheklansin (per user).
Validation: wallet_address format check, blacklist tekshiruvlari.
🔔 Bildirishnomalar (Notifications)
Triggerlar:
Income posted (new income transaction): push "Balans yangilandi: +$X"
Withdraw status change: 
Pending: "Sizning yechish so‘rovingiz qabul qilindi."
Processing: "To‘lov jarayoni boshlandi."
Completed: "Pul yechildi: -$X (USDT BEP20). Tx: <hash>"
Failed: "To‘lov bajarilmadi. Sabab: ..."
Low balance alerts (optional)
Tizim:
notifications modul yaratadi va notifications_log ga yozadi.
Notifier worker FCM orqali push yuboradi; agar device offline bo‘lsa push queuing va retry.
In-app notification center (GET /api/user/notifications) qaytaradi so‘nggi xabarlarni.
UX va UI integratsiyasi haqida backend talablar (client-backend kutishlari)
Refresh tugmasi
UI bosganda POST /api/user/refresh_balance chaqirsin; loading/progress bar toggling.
Backend boshqaradi va new_balance qaytaradi.
Withdraw button
UI POST /api/withdraw — so‘rov muvaffaqiyatli bo‘lsa transaction_id va statusni ko‘rsatsin.
Push notification yuboriladi status o‘zgarganda.
Transaction history
Paginated GET /api/transactions — server 10/20 item qaytarsin.
Client “Load more” tugmasi offsetni oshiradi.
Recent push list
GET /api/user/notifications?limit=3 — to‘g‘ridan-to‘g‘ri Balance sahifadagi mini-panelni to‘ldiradi.
Monitoring, audit va operatsion talablar
Audit trail: har bir balans o‘zgarishi uchun balance_history yoki transactions yozuvi bo‘lishi shart.
Metrics to collect: 
withdraws_requested_total, withdraws_successful_total, withdraws_failed_total
balance_refresh_requests, balance_refresh_errors
Alerts: 
Payout failure rate oshsa — adminga Telegram alert.
Orphaned pending payouts (status processing > 24h) — admin review.
Logs retention: tranzaksiyalar va withdrawal logs kamida 90 kun; audit logs 365 kun (yuridik talabga qarab).
Admin bilan integratsiyasi (pul yechish monitoring)
Admin panelda: 
Withdraws list (filter by status)
Retry / manual payout (override)
Manual balance adjust with mandatory note
Export CSV of transactions
Qo‘shimcha tavsiyalar va cheklovlar
MIN_WITHDRAW_USD constant — 1.39$
Currency conversion: agar siz USDT rate o‘zgartirsangiz (1$ = 0.9 USDT), server har payoutda conversion hesaplasin va amount_usdt saqlasin.
Payout provider fees: agar bor bo‘lsa, ko‘rsatilsin (net amount vs gross).
Fraud checks: withdraw so‘rovini yaratishda user risk score tekshirilsin (AI risk module), shubha bo‘lsa pending_manual_review.
Yakuniy tavsiyalar (amalga oshirish tartibi)
Implement transactions va balance_history jadvallarini yaratish.
Implement balance_service.get va balance_service.refresh (atomic).
Implement payout_worker va PaymentProvider adapteri (NowPayments esim bilan).
Build notifier pipeline (notifications_log + FCM worker).
Add admin endpoints va audit logging.
Test: unit tests + integration test (payout sandbox).
Monitoring + alerts + runbook.



“Withdraw (Pul yechish) — USDT (BEP20)” sahifasi uchun to‘liq backend arxitekturasi, kodsiz lekin ishlab chiqishga tayyor, batafsil hujjatni taqdim etaman. Hamma narsa sizning ilovangiz (auth, balance, notifications, admin panel, buyer API) bilan mos ishlashi hisobga olingan.
Men buni quyidagi bo‘limlarga ajratdim: umumiy oqim, fayl/modul tuzilmasi, DB DDL, endpointlar (request/response), payment provider adapter, worker/monitoring, xavfsizlik va anti-fraud qoidalari, notiflar, admin funktsiyalar, error kodlari va test-senarilar.
1. Umumiy oqim (high-level)
Foydalanuvchi ilovadan POST /api/withdraw so‘rovini yuboradi (JWT bilan).
Backend tekshiradi: autentifikatsiya, balans ≥ MIN_WITHDRAW (1.39$), manzil formati to‘g‘ri, anti-spam limit.
Agar OK bo‘lsa — withdraw_requests jadvalida satr yaratiladi (status = pending).
payout_worker (fon) PaymentProvider.create_payout() orqali provayderga so‘rov yuboradi va status = processing qilib yangilaydi.
Provayderdan qaytgan payout_id DB ga yoziladi. Worker provayder webhook yoki pollling orqali holatni tekshiradi.
Agar completed bo‘lsa — withdraw_requests.status = completed, users.balance_usd dan yechib olinadi (agar hali olinmagan bo‘lsa) va foydalanuvchiga push yuboriladi.
Agar failed bo‘lsa — status = failed, sababi loglanadi, va (agar kerak) balans qaytariladi yoki adminga yo‘naltiriladi. 
3. Ma’lumotlar bazasi (DDL — zarur jadvallar)
withdraw_requests
ustunturitavsifidBIGSERIAL PKichki idtelegram_idBIGINTfoydalanuvchiamount_usdNUMERIC(14,6)so‘ragan $amount_usdtNUMERIC(14,6)konvert qilingan USDT (rate bilan)wallet_addressTEXTBEP20 addressnetworkVARCHAR'BEP20'statusVARCHARpending / processing / completed / failed / canceledpayout_idTEXTprovider idtx_hashTEXTblockchain tx hash (agar mavjud)provider_responseJSONBprovider’dan birinchi javob (forensics)idempotency_keyVARCHARclient yoki server generatsiyalanganreserved_balanceBOOLEANbalans oldindan rezerv qilinganmifee_usdNUMERICagar uchrashsa, provayder komissiyasinoteTEXTadmin yoki system notecreated_atTIMESTAMPTZprocessed_atTIMESTAMPTZtugash vaqtiIndexes: telegram_id, status, created_at, idempotency_key(unique). 
transactions (oldingi modul bilan integratsiya)
Har pul harakati uchun record (withdrawlarni ham shu jadvalga qo‘shing yoki alohida bo‘lsin).
payout_audit
Provider bilan bo‘lgan barcha API chaqiriqlari va webhooklar forensics uchun.
4. Muhim .env / konfiguratsiya parametrlar
MIN_WITHDRAW_USD=1.39 MAX_WITHDRAW_USD=100.00 PAYMENT_PROVIDER=nowpayments # yoki crypto_cloud, custom NOWPAYMENTS_API_KEY=xxxx NOWPAYMENTS_API_SECRET=yyyy PAYOUT_RETRY_MAX=5 PAYOUT_RETRY_BACKOFF=exponential IDEMPOTENCY_TTL=86400 # seconds WITHDRAW_RATE_LIMIT_PER_MIN=1 DAILY_WITHDRAW_LIMIT=3 # per user per day DEFAULT_USD_TO_USDT_RATE=0.90 # (1$ = 0.9 USDT) or dynamic via oracle 
5. Endpointlar (request/response — concept)
POST /api/withdraw
Auth: Bearer JWT
Body:
{ "telegram_id": 523643, "amount_usd": 5.00, "wallet_address": "0x1234abcd... (0x + 40 hex)", "network": "BEP20", "idempotency_key": "client-generated-uuid-v4" // optional but recommended } 
Server-side protsedura:
Verify token matches telegram_id
Validate address regex ^0x[a-fA-F0-9]{40}$
Check amount_usd >= MIN_WITHDRAW_USD and <= MAX_WITHDRAW_USD
Check daily & per-minute rate limits
Check balances.balance_usd >= amount_usd (or reserve mechanism)
Create withdraw_requests row (status pending)
Push job to payout queue (celery/redis) Response (202 Accepted):
{ "status": "pending", "withdraw_id": 987, "message": "Withdraw request queued and will be processed shortly." } 
If duplicate idempotency_key used -> return existing withdraw record instead of creating new.
GET /api/withdraws (user)
List last 5 withdraws for user (paginated)
GET /admin/withdraws (admin)
Pending / failed list, filters, retry action.
POST /admin/withdraws/{id}/retry (admin)
Retry processing a failed payout (admin-only).
POST /webhook/payouts/{provider}
Provider -> backend webhook for payout status updates. Must verify signature.
6. Payment Provider Adapter (payout_service)
Konseptual interfeys (adapter pattern):
create_payout(address, amount_usdt, idempotency_key, metadata) -> { payout_id, status, provider_payload }
get_payout_status(payout_id) -> { status, tx_hash, provider_payload }
cancel_payout(payout_id) (agar provider qo‘llasa)
Adapter implementatsiyasi: NowPayments, CryptoCloud, yoki universal REST wrapper.
Idempotency:
Har create_payout chaqiruvi idempotency_key bilan yuborilsin.
DB da idempotency_key unikalligi saqlansin — agar takror bo‘lsa, avvalgi payout_id qaytarilsin.
Provider tarafida ham idempotency qo‘llanilsa ideal.
Error handling:
Synchronous create_payout qaytarishi processing bo‘lsa, worker status poll qilishni boshlaydi.
Provider xatoliklari — transient bo‘lsa retry (exponential), permanent bo‘lsa failed.
7. Payout Worker (fon jarayon)
Vazifalari:
Job queue’dan withdraw_request_id oling.
DB tranzaksiyasida reserved_balance = true (yoki balansdan oldindan yechib qo‘ying) — bu double spendni oldini oladi.
Call payout_service.create_payout(...) (idempotency_key bilan).
Yozish: payout_id, provider_response, status=processing.
Agar create_payout muvaffaqiyatsiz (permanent fail) → mark failed, rollback reservations yoki ayirishni bekor qilish; notify user + admin.
Agar processing yoki pending → enqueue poll job (polling interval: 1, 5, 15, 60 min progressive).
Poller get_payout_status(payout_id) chaqiradi; agar completed → set status=completed, tx_hash, processed_at va finalize: balance already reserved -> confirm deduction persisted.
On failed → set failed, if reserved then release funds or handle as policy dictates.
Retry policy: exponential backoff, max tries PAYOUT_RETRY_MAX.
Idempotency & concurrency: worker must check DB row status before acting — only process if status in (pending, processing) and locked via SELECT ... FOR UPDATE.
8. Balans dan pul yechish logikasi (atomicity)
Two options:
A) Reserve-first (recommended)
When request accepted, set reserved_amount = amount_usd in withdraw_requests and mark balances.balance_usd -= amount_usd atomically OR set reserved_balance = true and create a reserve transaction.
This prevents double withdraw.
Only finalize when payout completed.
B) Finalize-after-provider-confirmation
Do not deduct balance until provider confirms payout — risk of double-spend in time window; not recommended.
Recommend A: reserve and deduct immediately when yw request accepted (so balance shown is updated). If payout fails, refund by creating transaction.
All balance mutation must be inside DB transaction and create transactions rows for audit.
9. Webhook handling (provider -> backend)
Provider will send webhook on payout status changes. Implement: 
POST /webhook/payouts/{provider} — verify signature header (HMAC or provider signature).
Match payout_id -> update withdraw_requests status accordingly.
On completed -> call finalize flow: set tx_hash, processed_at, ensure balance already deducted earlier.
On failed -> change status=failed, refund user if deducted, notify.
Store raw webhook body in payout_audit.
10. Notifications (user feedback)
Push events (via notifications module):
on create: "Pul yechish so‘rovingiz qabul qilindi."
on processing: "To‘lov BEP20 tarmog‘ida amalga oshirilmoqda."
on completed: "To‘lov muvaffaqiyatli yakunlandi. Tx: <hash>"
on failed: "To‘lov amalga oshmadi. Sabab: <reason>. Agar summa yechildi bo‘lsa balans qaytarildi."
Also in-app notifications and email optional.
11. Security & Fraud controls
Rate limit: WITHDRAW_RATE_LIMIT_PER_MIN per user (e.g., 1 per min) and DAILY_WITHDRAW_LIMIT (e.g., 3).
Address whitelist/blacklist: check against known scam addresses.
KYC / Risk Score: integrate risk_service — high-risk users require manual review (status = pending_manual_review).
IP/Device checks: if withdraw request comes from different device/IP than usual, increase risk score.
Anti-spam: block repeated requests within seconds.
Admin approvals: if risk_service flags, set status = pending_manual and create admin ticket.
Logs & audit: every action logged with admin/user id.
12. Admin panel funksiyalari
List pending / processing withdraws.
Details: request info, user profile, risk score, provider response, raw webhook logs.
Actions: 
Approve (force payout),
Reject (cancel and refund),
Retry (re-queue payout),
Manual payout (record manual tx hash and mark completed).
Whitelist addresses or ASNs.
13. Error codes (clients must handle)
400_invalid_address — address format invalid
400_insufficient_balance — balance < amount
400_below_minimum — amount < MIN_WITHDRAW_USD
429_rate_limit — too many withdraw attempts
403_kyc_required — KYC needed / manual review
500_provider_error — provider returned error (transient)
409_duplicate_idempotency — duplicate idempotency key (returns existing resource)
202_pending — accepted and queued
14. Testing scenariylari (majburi)
Normal flow: user balance 10$, withdraw 5$ → payout success -> balance decreased, tx hash recorded.
Insufficient balance: request rejected.
Invalid address: rejected.
Duplicate idempotency: second request returns original.
Provider transient fail: worker retries then success.
Provider permanent fail: request marked failed, balance refunded, admin alerted.
Risk flagged user: status pending_manual, admin approves -> payout proceeds.
Webhook signature spoof attempt: rejected and logged.
15. Observability & monitoring
Metrics: withdraw_requests_total, withdraws_completed_total, withdraws_failed_total, withdraws_processing_latency, payout_provider_errors.
Logs: structured JSON to Loki/Sentry.
Alerts: payout failure rate > threshold, long processing queue, provider unreachable.
Dashboard: average processing time, pending queue size.
16. UX & client-side expectations
Client should generate and send idempotency_key (UUIDv4) to avoid duplicates.
Show loader after submit; poll GET /api/withdraws/{id} for status or rely on push notifications.
Display last 5 withdraws on page and show status and tx hash when available.
Show precise error messages for reasons like insufficient funds, invalid address, rate limit.
17. Extra considerations
Fee handling: if provider charges fee, show fee_usd and net amount to user (or deduct fee from user). Policy must be clear.
Currency conversion: use reliable USD→USDT rate (oracle) or fixed policy from config; store amount_usdt.
Idempotency across restarts: store idempotency_key with TTL and unique constraint.
Legal / AML: consider KYC/AML rules if large withdrawals; enforce thresholds.
Backup & disaster recovery: ensure DB backups and payout job durability.
18. Tavsiya qadamlar (implementatsiya tartibi)
DB jadvallarini yaratish (withdraw_requests, payout_audit).
withdraw_service + controller: validation, reservation logic, idempotency.
Payment provider adapter skeleton + sandbox testing.
payout_worker implementatsiya va polling/webhook handler.
Notifications pipeline integration.
Admin UI va manual override.
Monitoring & alerts.
Security audit & penetration test.


“📈 Statistika (Analytics)” sahifasi uchun backend arxitekturasini batafsil tuzish bosqichi. Quyida bu sahifaning to‘liq backend tuzilmasi (API, jadval, hisoblash logikasi, integratsiya, cache va push mexanizmlari bilan) keltirilgan 👇
🧠 1. Maqsad
Analytics sahifasi foydalanuvchining trafik, daromad va MB narxi o‘zgarishlarini real vaqtda kuzatish uchun xizmat qiladi. Backend bu ma’lumotlarni yig‘ish, saqlash, agregatsiya qilish va push tarzida yetkazib berish uchun mo‘ljallangan.
⚙️ 2. Backend komponentlari (modules)
Modul nomiMaqsaditraffic_collector.pyTizimdagi trafik harakatlarini real vaqt rejimida yig‘ishanalytics_manager.pyKunlik, haftalik, oylik statistikani hisoblash va DB ga yozishpricing_manager.pyMB narxlarini olish (market API orqali)analytics_api.pyFrontend uchun REST API endpointlarini ta’minlashnotifications.pyStatistika bilan bog‘liq push xabarlarni yuborishcache_manager.pyRedis orqali so‘nggi statistika ma’lumotlarini tezkor olishscheduler.pyCron asosida periodik hisoblash va hisobot yuborishdb/models/traffic_logs.pyTraffic, profit, narx va vaqt bo‘yicha ma’lumotlar jadvalidb/models/pricing_logs.pyNarx o‘zgarishlarining tarixini saqlash 
🧾 3. Database strukturalari
traffic_logs (asosiy jadval)
UstunTipTavsifidINTEGER (AI)Unikal identifikatortelegram_idBIGINTFoydalanuvchi IDsent_mbFLOATYuborilgan trafik hajmisold_mbFLOATSotilgan trafik hajmiprofit_usdFLOATShu davrda topilgan daromadprice_per_mbFLOATMB uchun narx (USD)periodENUM(daily, weekly, monthly)Statistika turidateDATESana yoki hafta boshicreated_atTIMESTAMPYozilgan vaqt 
pricing_logs
UstunTipTavsifidINTEGER (AI)Unikal IDdateDATESanaprice_per_mbFLOAT1 MB narxi (USD)sourceVARCHAR(50)Narx manbai (API nomi)updated_atTIMESTAMPOxirgi yangilanish vaqti 
🔄 4. API endpointlar
MethodURLTavsifGET/api/stats/daily/<telegram_id>Bugungi kunlik statistikaGET/api/stats/weekly/<telegram_id>Haftalik tahlilGET/api/stats/monthly/<telegram_id>Oylik umumiy statistik ma’lumotlarGET/api/stats/ratesJoriy MB narxlariGET/api/stats/summary/<telegram_id>Foydalanuvchining umumiy sessiya hisobotlari 
🔢 5. Hisoblash logikasi (algoritm)
1️⃣ Kunlik hisob
Har 1 soatda traffic_collector foydalanuvchi yuborgan va sotilgan MB qiymatlarini yig‘adi.
Hisoblash: profit_usd = sold_mb × price_per_mb 
Yangi satr traffic_logs jadvaliga yoziladi (period='daily').
2️⃣ Haftalik hisob
Har yakshanba kechasi scheduler kunlik yozuvlarni yig‘ib: weekly_sent = SUM(sent_mb) weekly_sold = SUM(sold_mb) weekly_profit = SUM(profit_usd) weekly_price_avg = AVG(price_per_mb) 
Natija period='weekly' yozuv sifatida saqlanadi.
3️⃣ Oylik hisob
Har oy oxirida: monthly_sent = SUM(sent_mb) monthly_sold = SUM(sold_mb) monthly_profit = SUM(profit_usd) avg_price = AVG(price_per_mb) 
Yangi satr period='monthly' sifatida traffic_logs jadvaliga yoziladi.
💡 6. Real-time yangilanish
Redis yoki WebSocket orqali real vaqt statistikasi frontendga yuboriladi:
{ "telegram_id": 523643, "sent_mb": 184.3, "sold_mb": 139.8, "profit_usd": 0.48, "price_per_mb": 0.0042, "timestamp": "2025-11-02T14:10:00Z" } 
Foydalanuvchi UI’da Live Chart real vaqt yangilanadi.
🔔 7. Push xabar logikasi
VaqtXabarTriggerHar kuni 00:00“📊 Bugungi hisobot tayyor! Siz $0.43 topdingiz.”Kunlik hisob yakunidaHar haftada 1 marta“📅 Haftalik daromadingiz: $5.12 (↑ +12%).”Yakshanba kechasiOy tugaganda“🎉 Oy yakuni: $13.88 foyda bilan!”Oylik hisobot 
🔐 8. Qo‘shimcha himoya
Rate limit: /api/stats/* endpointlari uchun 30s da 1 so‘rovdan ortiq emas.
Auth: JWT token orqali foydalanuvchi identifikatsiyasi.
Admin bypass: Adminlar uchun filtrlash chegaralari (kun/oy) cheklanmagan.
Cache: So‘nggi 1 soatlik natijalar Redis’da saqlanadi (response tezlashadi).
⚡ 9. Integratsiya
ModulIntegratsiyapricing_managerMarket API (trafic price update)schedulerCelery / APSchedulernotificationsTelegram bot API yoki Firebase pushanalytics_apiFrontend (mobile app + web dashboard)cache_managerRedis / Memory cache


“Sozlamalar (Settings)” sahifasi uchun backend arxitektura va tuzilmasi to‘liq ko‘rinishda keltirilgan — bu struktura frontend bilan mukammal sinxron ishlaydi va xavfsizlik, moslashuvchanlik, real-time update tamoyillariga asoslanadi.
🧠 Backend — Settings moduli to‘liq tuzilmasi


🗄️ 2. Ma’lumotlar bazasi modeli (SQL)
Jadval: user_settings
Ustun nomiTuriTavsifidINT PK AIAsosiy kalituser_idINT FKFoydalanuvchi IDlanguageVARCHAR(10)“uz”, “ru”, “en”push_notificationsBOOLEANTrue/Falsesession_updatesBOOLEANTrue/Falsesystem_updatesBOOLEANTrue/Falsetwo_factor_enabledBOOLEANTrue/Falsesingle_device_modeBOOLEANTrue/Falsebattery_saverBOOLEANTrue/FalsethemeVARCHAR(10)“light” yoki “dark”last_updateDATETIMEOxirgi o‘zgarish vaqti 
🔄 3. API Endpointlar
EndpointMetodTavsifXavfsizlik/user/settingsGETFoydalanuvchi joriy sozlamalarini olishJWT Auth/user/settingsPATCHSozlamalarni yangilashJWT Auth/user/security/2faPOST2FA yoqish (Google Auth / Telegram)JWT Auth/user/security/disable_2faPOST2FA o‘chirishJWT Auth/user/logout_allPOSTBarcha sessiyalarni tugatishJWT Auth/user/settings/themePATCHDark/Light tema o‘zgartirishJWT Auth/user/settings/cache_clearDELETECache tozalashJWT Auth 
⚙️ 4. Logika bo‘linmalari
🧩 settings_service.py
DB bilan ishlaydi (CRUD)
Input validatsiya (settings_schema.py orqali)
Lokal o‘zgarishlarni cache_service orqali sinxronlashtiradi
Har bir PATCH o‘zgarish uchun audit log yozadi
🧱 security_service.py
2FA (OTP) kod generatsiyasi va tekshiruvi
logout_all() → userning barcha JWT tokenlarini revokatsiya qiladi
single_device_mode() → yangi loginlarni avtomatik bloklaydi
Telegram 2FA integratsiyasi uchun webhook qo‘llab-quvvatlovi
🔔 notification_service.py
Push, session va system notification sozlamalarini real-time yangilaydi
Firebase yoki Telegram notify API bilan sinxron
🌍 localization_service.py
Foydalanuvchi tili o‘zgarganda frontendga locale.json yuboradi
Multi-language cache (uz.json, ru.json, en.json)
🧠 5. Ishlash oqimi (Flow Diagram)
[User UI] ↓ (PATCH /user/settings) ↓ [settings_routes.py] ↓ [settings_service.py] ↓ [DB -> user_settings] ↓ ✅ Response: { "status": "updated", "language": "en" } 
🔐 6. Xavfsizlik elementlari
JWT token har bir so‘rov uchun tekshiriladi.
2FA yoqilgan foydalanuvchi uchun critical amallar OTP bilan tasdiqlanadi.
Admin foydalanuvchilarga (role=admin) cheklovlar qo‘llanilmaydi.
Request throttling (3 req/s) DDOSdan himoya qiladi.
Cache clear faqat token egasiga tegishli ma’lumotlarni tozalaydi.
🪄 7. Qo‘shimcha modullar
ModulTavsifactivity_log.pySozlamalar o‘zgarish tarixini saqlaydischeduler.pyBattery Saver rejimida auto-refresh intervalni pasaytiradisync_service.pyFoydalanuvchi sozlamalarini server va mobil o‘rtasida sinxronlashtiradi 
💬 8. Natija
Bu backend moduli:
foydalanuvchi uchun moslashuvchan (til, bildirishnoma, tema),
xavfsiz (2FA, single-device, logout_all),
va energiya tejovchi (Battery Saver rejimi) tuzilmani ta’minlaydi.
Frontenddagi har bir o‘zgarish backendda darhol aks etadi.



“Sessiyalar tarixi (Session History)” sahifasi backendda eng muhim modullardan biri hisoblanadi, chunki u trafik faoliyati, foydalanuvchi daromadi, va tarmoq monitoringini to‘liq nazorat qiladi. Quyida shu sahifaning to‘liq backend tuzilmasi (kodlarsiz, lekin professional arxitektura shaklida) keltirilgan 👇
🧠 Backend — Session History moduli to‘liq tuzilmasi

 
🗄️ 2. Ma’lumotlar bazasi modeli
Jadval: sessions
Ustun nomiTuriTavsifidINT PKSessiya IDuser_idINT FKFoydalanuvchi IDstart_timeDATETIMEBoshlanish vaqtiend_timeDATETIMETugash vaqtidurationVARCHAR(20)HH:MM:SS formatsent_mbDECIMAL(10,2)Trafik hajmi (MB)earned_usdDECIMAL(10,2)Sessiyadan topilgan daromadstatusENUM(‘active’,‘completed’,‘failed’,‘cancelled’)Sessiya holatiip_addressVARCHAR(64)Ulanuvchi IP manzililocationVARCHAR(64)Geo-joylashuvdeviceVARCHAR(64)Qurilma turi (Android/iOS)created_atDATETIMEYozuv yaratilgan vaqt 
🔄 3. API Endpointlar
EndpointMetodTavsifAuth/sessionsGETFoydalanuvchi barcha sessiyalarini olish (pagination bilan)JWT/sessions/{id}GETTanlangan sessiya tafsilotlariJWT/sessions/summaryGETBugun/hafta/oy statistikasiJWT/sessions/activeGETFaqat faol sessiyalarni olishJWT/sessions/filterPOSTSana va status bo‘yicha filtrlashJWT/sessions/exportGETSessiyalarni CSV fayl sifatida yuklashJWT/sessions/review/{id}POSTAI orqali sessiya sifatini baholashJWT/sessions/notify/weeklyPOSTHaftalik avtomatik xabar yuborish (cron yoki Celery task)Admin 
⚙️ 4. Xizmat logikasi (Services)
🔹 session_service.py
/sessions va /sessions/filter so‘rovlarini boshqaradi
Sana oralig‘ini (from → to) filtrlab, status bo‘yicha saralaydi
duration avtomatik hisoblanadi: end_time - start_time

Response builder orqali JSON formatda qaytaradi
🔹 analytics_service.py
Foydalanuvchi faoliyatini tahlil qiladi: 
bugun: sessiya soni, MB, $
hafta: jami MB, $
o‘rtacha foyda/sessiya
Natijani /sessions/summary endpointga yuboradi
Grafika uchun JSON (kunlik MB, daromad) tayyorlaydi
🔹 ai_analysis_service.py
Trafik sifatini baholaydi: 
uzilishlar soni
MB/vaqt nisbati
ping, latency tahlili
0–100 oralig‘ida “session quality score” beradi
AI review tugmasi bosilganda yoki cron orqali har kecha avtomatik ishga tushadi
🔹 csv_export_service.py
Foydalanuvchi sessiyalarini .csv faylga eksport qiladi
Har satrda: Sana, davomiylik, MB, daromad, IP, status
Fayl secure_temp/exports/{user_id}.csv joyida 24 soat saqlanadi
🔹 notification_service.py
Har haftada avtomatik summary hisoblaydi
Telegram yoki Email orqali yuboradi: 

“Siz bu hafta 2.4 GB trafik yubordingiz, $7.89 topdingiz!”

🧩 5. Schemalarning tuzilishi
session_schema.py
{ "id": int, "start_time": str, "end_time": str, "duration": str, "sent_mb": float, "earned_usd": float, "status": str, "ip_address": str, "location": str, "device": str } 
filter_schema.py
{ "from_date": str, "to_date": str, "status": str } 
analytics_schema.py
{ "today": {"sessions": int, "mb": float, "earnings": float}, "week": {"sessions": int, "mb": float, "earnings": float}, "average_per_session": float } 
🛠️ 6. Qo‘shimcha imkoniyatlar
FunksiyaTavsifAI ReviewTrafik sifati tahlili (AI)CSV ExportSessiya tarixini yuklab olishWeekly ReportHar haftalik xabarnomaGeo IP TrackingIP orqali joylashuv aniqlashInfinite ScrollFrontend uchun paginationAdmin PrivilegesAdmin barcha foydalanuvchilarning sessiyalarini ko‘ra oladi 
🔐 7. Xavfsizlik
Foydalanuvchining user_id JWT dan olinadi
Boshqa foydalanuvchining sessiyalariga kirish taqiqlanadi
Admin rolli foydalanuvchilarga filtr cheklovlari qo‘llanilmaydi
CSV eksport har doim foydalanuvchining o‘z ma’lumotlariga asoslanadi
SQL injection va datetime exploitlarga qarshi sanitarizatsiya
📊 8. Integratsiyalar
AI service (trafik sifatini tahlil qiladi)
GeoIP API (IP orqali joylashuv)
Task scheduler (Celery/CRON) (haftalik tahlillar)
Export module (CSV yoki PDF)
Telegram Bot Notify (xabar yuborish)
💬 9. Yakuniy natija
Session History backend moduli:
Foydalanuvchining trafik sessiyalarini to‘liq nazorat qiladi
Daromad va ishlash statistikasini hisoblab beradi
Admin monitoringi va foydalanuvchi hisobotlari uchun tayyor API beradi


Qo‘llab-quvvatlash (Support) sahifasi uchun to‘liq professional tuzilma keltirilgan — bunda UI, backend, API, va Telegram integratsiyasi bir tizim sifatida ishlaydi.

🎯 2. Maqsad
Foydalanuvchi yordam kerak bo‘lsa, ilovadan chiqmasdan to‘g‘ridan-to‘g‘ri admin yoki support jamoasiga yozishi mumkin.
Admin javobni panel orqali beradi — va foydalanuvchi “Support tarixi”da ko‘radi.
🖼️ 3. UI tuzilmasi
Sahifa nomi: “Qo‘llab-quvvatlash”
Tagline: “Savolingiz bormi? Biz sizga yordam beramiz 👩‍💻”
🔹 Form maydonlari:
MaydonTavsifHolat👤 IsmTelegram foydalanuvchi nomireadonly🆔 Telegram IDFoydalanuvchidan olinadireadonly✉️ Xabar mavzusiQisqa sarlavhainput🗒️ Xabar matniBatafsil xabartextarea📎 Rasm yoki faylIxtiyoriy qo‘shimchaupload🚀 Yuborish tugmasiAPIga POST yuboradibutton 
🔹 Xabar yuborilgandan so‘ng:
✅ Snackbar:
“Xabaringiz yuborildi! Admin tez orada siz bilan bog‘lanadi.”

🧠 4. Backend logikasi
Jadval: support_requests
UstunTuriTavsifidINTPrimary keyuser_idINTTelegram foydalanuvchi IDsubjectVARCHAR(255)MavzumessageTEXTXabar matniattachment_urlVARCHAR(255)Fayl URLstatusENUM('new','read','replied','closed')Holatcreated_atDATETIMEYuborilgan vaqtupdated_atDATETIMEYangilanish vaqti 
🔄 5. API endpointlar
EndpointMetodTavsif/support/sendPOSTYangi support xabarini yuborish/support/historyGETFoydalanuvchi yuborgan xabarlar ro‘yxati/support/{id}GETBitta murojaat tafsiloti/support/reply/{id}POSTAdmin tomonidan javob (panel orqali) 
📨 6. API misol
POST /support/send
{ "user_id": 105, "subject": "To‘lov kechikdi", "message": "Men 1.39$ yechdim, lekin USDT hali kelmadi.", "attachment_url": "https://cdn.app.com/uploads/screenshot_01.png" } 
🤖 7. Telegram integratsiyasi
Yuborilgan har bir xabar avtomatik ravishda admin botga yetkaziladi.
Telegram Bot API chaqirig‘i:
POST https://api.telegram.org/bot<ADMIN_BOT_TOKEN>/sendMessage 
Matn:
📩 Yangi support xabari: 👤 Foydalanuvchi: @username 🆔 ID: 105 📝 Mavzu: To‘lov kechikdi 💬 Matn: Men 1.39$ yechdim, lekin USDT hali kelmadi. 
Agar attachment_url mavjud bo‘lsa → sendPhoto yoki sendDocument yuboriladi.
🛡️ 8. Xavfsizlik va filtr
MexanizmTavsif🕒 Rate Limit1 xabar / 30 soniya🔐 CSRF himoyaToken orqali🔏 JWT AuthLogin foydalanuvchilarga ruxsat📁 Fayl chekloviMaksimal hajm 5 MB🧱 Anti-spamRedis yoki token count orqali🧍‍♂️ Admin FilterAdmin userlar uchun cheklovlar ishlamaydi 
🗃️ 9. Qo‘shimcha komponentlar
SupportHistory – foydalanuvchi o‘z yuborgan xabarlarini ko‘radi (status bilan)
Reply system (admin panel) – admin javob yuboradi → foydalanuvchi bot orqali xabar oladi
Push Notification – yangi javobda foydalanuvchiga bildirishnoma
🎨 10. UI dizayn g‘oyasi
Sokin fon (light blue yoki gradient)
Form elementlari rounded
Yuborish tugmasi: gradient #0dcaf0 → #007bff
Xabar statuslari ranglar bilan: 
🟡 Yangi
🟢 Javob berilgan
🔴 Yopilgan
✅ Yakuniy foydalanuvchi oqimi
Foydalanuvchi Support sahifasiga kiradi
Mavzu va xabar yozadi
Fayl qo‘shadi (agar kerak bo‘lsa)
“Yuborish” tugmasini bosadi
Server → Telegram admin botga xabar yuboradi
Admin javob beradi → foydalanuvchi “Support history”da ko‘radi


📢 “Yangiliklar / Promo” sahifasi uchun to‘liq professional tuzilma arxitekturasi (kodlarsiz, lekin ishlab chiqish uchun tayyor shaklda) berilgan. Bu strukturada frontend, backend, model, API, integratsiya va avtomatik push tizimi aniq ajratilgan.
 
🎯 2. Maqsad
Bu modul foydalanuvchilarga:
Rasmiy Telegram kanal va chat linklarini ko‘rsatadi
Admin e’lonlarini (news feed) yetkazadi
Promo-kodlarni faollashtirish imkonini beradi
Va push notification orqali yangiliklarni bildiradi
🗂️ 3. Ma’lumot bazasi modellari
Jadval: announcements
Ustun nomiTuriTavsifidINTPrimary keytitleVARCHAR(255)E’lon sarlavhasidescriptionTEXTE’lon matniimage_urlVARCHAR(255)E’lon rasmi (optional)linkVARCHAR(255)Batafsil havolacreated_atDATETIMEYaratilgan sana 
Jadval: promo_codes
Ustun nomiTuriTavsifidINTPrimary keycodeVARCHAR(64)Promo kodbonus_percentDECIMAL(5,2)Bonus foiziexpires_atDATETIMEAmal muddatiis_activeBOOLEANAktiv holat 
🔄 4. API endpointlar
EndpointMetodTavsif/announcementsGETE’lonlar ro‘yxatini olish/promo/listGETFaol promo-kodlar ro‘yxati/promo/activatePOSTPromo-kodni faollashtirish/telegram/linksGETKanal va chat linklarini olish 
📨 API misol:
GET /news_promo
{ "telegram_links": { "channel": "https://t.me/project_news", "chat": "https://t.me/project_chat" }, "announcements": [ { "title": "Kunlik narx yangilandi!", "description": "Bugun trafik narxi 0.0023 $/MB etib belgilandi.", "image_url": "https://cdn.app.com/news/price.png", "created_at": "2025-11-02T08:00:00Z" } ], "promo": [ { "code": "TRAFIC10", "bonus_percent": 10, "expires_at": "2025-11-15", "is_active": true } ] } 
⚙️ 5. Backend logikasi oqimi
Client → API so‘rov
/news_promo orqali barcha ma’lumotlar bitta javobda keladi
(keshlangan holatda, tez javob uchun)
Backend → DB / Redis 
E’lonlar va promo kodlarni oladi
Telegram linklarini config fayldan yuklaydi
Response → Frontend 
UI’da card sifatida chiqadi
“NEW 🔥” belgisi yangiliklar uchun qo‘shiladi
📱 6. UI sahifa tuzilishi
Yuqori qism (Header):
📢 So‘nggi yangiliklar “Loyihamizdagi e’lonlar va bonuslarni bu yerdan kuzating.” 
Asosiy bloklar:
1️⃣ Telegram havolalari
Telegram kanal kartasi
Chat kartasi
👉 Tugmalar: “Kanalga o‘tish”, “Chatga qo‘shilish”
2️⃣ E’lonlar (News Feed)
Sana
Sarlavha
Tavsif
Thumbnail (rasm bo‘lsa)
“Yangi 🔥” belgisi (oxirgi 24 soatlik e’lonlar uchun)
3️⃣ Promo-kodlar
PROMO nomi
Bonus foizi
Amal muddati
“Faollashtirish” tugmasi → POST /promo/activate
🎨 7. UI dizayn g‘oyasi
Foni: Gradient (white → light blue)
Har bir bo‘lim — card shaklida, yumaloq burchaklar bilan
E’lonlar: minimal shadow, thumbnail chapda
Promo-kodlar: gradient #FFD700 → #FFA500
“NEW 🔥” belgisi — animatsion yoki pulsatsiyali
Avtomatik yangilanish: har 30 daqiqada (AutoRefreshHook.js orqali)
🔔 8. Qo‘shimcha imkoniyatlar
FunksiyaTavsif🔔 Push notificationAdmin yangi e’lon joylasa — barcha foydalanuvchilarga push yuboriladi📎 Kanalga obuna eslatmasiAgar foydalanuvchi kanalga ulanmagan bo‘lsa — banner orqali eslatma🎉 Promo eventBelgilangan sanada avtomatik promo faollashtirish🗓️ Scheduler30 daqiqada avtomatik refresh uchun background task 
🧱 9. Xavfsizlik
JWT token bilan himoyalangan promo aktivatsiya (/promo/activate)
Redis caching → ortiqcha so‘rovlarni kamaytiradi
Anti-spam rate limit (max 5 so‘rov / 1 daqiqa)
Admin panelda e’lon qo‘shish uchun ruxsat filtri (role=admin)
✅ 10. Yakuniy foydalanuvchi tajribasi
Foydalanuvchi “📢 Yangiliklar & Promo” sahifasiga kiradi
Rasmiy kanal/chat havolalarini ko‘radi
E’lonlarni o‘qiydi (yangi belgilar bilan)
Promo-kodni faollashtiradi — bonus balansiga tushadi
Yangi yangiliklar push orqali bildiriladi



“Profil & Xavfsizlik” sahifasining funktsional spetsifikatsiyasini tuzgansan. Quyida men bu tuzilmani to‘liq modulli tizim arxitekturasi shaklida jamlab, frontend (UI), backend (API) va xavfsizlik (security layer) qismlarini aniq qilib beraman — ya’ni loyiha ishlab chiqishda to‘g‘ridan-to‘g‘ri foydalanish mumkin bo‘lgan texnik blueprint bo‘ladi 👇
🧱 1. Umumiy tuzilma
Sahifa nomi: Profil & Xavfsizlik
Yo‘nalish: /profile
Ma’lumot manbai: GET /user/profile
Texnologiyalar:
Frontend: React + TailwindCSS + JWT Auth Context
Backend: FastAPI (Python) + PostgreSQL (users jadvali)
Auth: Telegram OAuth → JWT Token
Session Management: Redis (session cache)
🧩 2. UI komponent tuzilmasi
/profile ├── ProfileHeader (👤 profil rasmi, ism, username) ├── AccountDetails (🆔 Telegram ID, auth_date, device) ├── SecuritySection │ ├── TwoFactorCard │ ├── TokenCard (view + renew) │ ├── SessionControl (logout, logout_all) └── LoginHistoryCard (oxirgi 5 kirish logi) 
🔹 ProfileHeader
Profil rasmi (photo_url)
first_name (readonly)
@username (readonly)
Oxirgi kirish vaqti (auth_date)
🔹 SecuritySection
2FA holati (🔒 Faol / ❌ Faol emas)
JWT token (mask bilan ko‘rsatiladi, masalan eyJhbGci...fT0=)
🔄 “Tokenni yangilash” tugmasi
🚪 “Hisobdan chiqish” tugmasi
🚫 “Barcha sessiyalarni tugatish”
🔹 LoginHistoryCard
So‘nggi 5 ta login: Toshkent • Android Galaxy S8+ • 2025-10-31 21:00 Toshkent • Windows • 2025-10-29 10:22 ... 
⚙️ 3. Backend (API) tuzilmasi
🔸 Jadval: users
UstunTuriTavsiftelegram_idBIGINTUnikal Telegram IDusernameTEXT@usernamefirst_nameTEXTIsmphoto_urlTEXTTelegram rasmiauth_dateTIMESTAMPSo‘nggi kirishjwt_tokenTEXTJWT tokentwo_factor_enabledBOOLEAN2FA holatilast_login_ipTEXTOxirgi IPlast_login_deviceTEXTQurilma nomi 
🧠 4. API Endpointlar
EndpointMetodTavsif/user/profileGETProfil ma’lumotlarini olish/user/token/renewPOSTYangi JWT token olish/user/logoutPOSTLokal sessiyadan chiqish/user/logout_allPOSTBarcha sessiyalarni tugatish/user/login_historyGETOxirgi 5 kirish loglarini olish 
✅ GET /user/profile
Javob:
{ "telegram_id": 599382114, "username": "bunyoddev", "first_name": "Bunyod", "photo_url": "https://t.me/i/userpic/320/bunyod.jpg", "auth_date": "2025-11-02T12:45:00Z", "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "two_factor_enabled": true, "last_login_ip": "185.91.77.3", "last_login_device": "Android Galaxy S8+" } 
🔄 POST /user/token/renew
Tavsif: JWT tokenni yangilaydi
Request:
{ "telegram_id": 599382114 } 
Response:
{ "message": "Token successfully renewed", "jwt_token": "new.jwt.token..." } 
🚪 POST /user/logout
Redis va JWT tokenni o‘chiradi
Foydalanuvchini /auth sahifasiga yo‘naltiradi
Response:
{ "message": "Successfully logged out" } 
🚫 POST /user/logout_all
active_sessions jadvalidan barcha tokenlarni o‘chiradi
Bildirishnoma: “Barcha sessiyalar tugatildi”
📜 GET /user/login_history
Response:
{ "history": [ { "city": "Toshkent", "device": "Android Galaxy S8+", "time": "2025-10-31 21:00" }, { "city": "Toshkent", "device": "Windows", "time": "2025-10-29 10:22" } ] } 
🔐 5. Xavfsizlik qatlamlari
FunksiyaTavsifJWT Token expiry7 kunAuto logout2FA yoqilgan foydalanuvchi 3 marta token yangilasa — majburiy logoutIP & Device CheckAgar token boshqa IP’dan ishlatilsa → bildirishnoma yuboriladiRedis session storeTez session tekshirishAudit logHar bir login/logout yoziladi (user_logs jadvali) 
📩 6. Bildirishnoma (Notification) tizimi
Telegram bot orqali xavfsizlik ogohlantirishlari: 
🔔 “Yangi kirish Toshkent, Android”
🚨 “Token boshqa IP’dan ishlatildi”
Email ogohlantirish (agar foydalanuvchi email bog‘lagan bo‘lsa)
🎨 7. UI dizayn (React/Tailwind)
Ko‘rinish:
Yuqorida profil rasmi + ism
Pastda card-style bo‘limlar: 
Security Settings
Login History
Logout
Har card’da shadow-lg rounded-2xl p-4 dizayn.
Tugmalar: bg-blue-500 hover:bg-blue-600 text-white rounded-xl px-3 py-2.



Admin Panel spetsifikatsiyasi.

 Quyida men uni to‘liq arxitektura shaklida — ya’ni haqiqiy ishlab chiqishga tayyor frontend + backend + xavfsizlik + ma’lumot modeli + API tuzilmasida jamlab berdim. Bu tuzilma Traffic / API Management Platform darajasidagi boshqaruv paneliga mos keladi.
🧠 ADMIN PANEL – TO‘LIQ TUZILMA (FINAL BLUEPRINT)
🎯 Maqsad
Tizimni markazlashtirilgan boshqarish, foydalanuvchilar, API’lar, trafik, to‘lovlar va xavfsizlikni real vaqt rejimida kuzatish.

🔐 2. Kirish va identifikatsiya
Kirish usuli: Telegram OAuth (ID, username, phone orqali)
.env faylda ro‘yxatdagi ADMIN_IDS bilan tekshiriladi: ADMIN_IDS=599382114,605472971 
Agar foydalanuvchi .env dagi ID’ga mos kelsa — SuperAdmin, aks holda 403 Forbidden.
📊 3. Dashboard (Asosiy boshqaruv)
Ko‘rsatiladigan ma’lumotlar:
NomiTavsif👥 Foydalanuvchilar soniSELECT COUNT(*) FROM users💰 Umumiy balansSUM(users.balance)📡 Faol sessiyalarCOUNT(active_sessions)⚙️ Faol API’larCOUNT(apis WHERE status='active')💸 Bugungi to‘lovlarSUM(withdraw.amount WHERE date=today)📈 Bugungi daromadSUM(transactions.revenue) 
Grafiklar (Chart.js):
Yangi foydalanuvchilar (kunlik)
Trafik iste’moli (MB)
Daromad dinamikasi
API:
GET /admin/dashboard/summary
GET /admin/dashboard/charts
👥 4. Users Management
Funktsiyalar:
Foydalanuvchilar ro‘yxati: Telegram ID, username, balans, oxirgi login
Qidiruv: ?query=username|telegram_id
Amal bajarish: 
🔒 Ban user → PATCH /admin/users/{id}/ban
♻️ Reset token → POST /admin/users/{id}/reset_token
💸 Add balance → POST /admin/users/{id}/add_balance
👁 View sessions → GET /admin/users/{id}/sessions
Model:
users (telegram_id, username, first_name, balance, status, auth_date, last_login_device)
🔑 5. API Management
Funktsiyalar:
Yangi API yaratish (POST /admin/apis/create) 
Foydalanuvchi tanlash
Limit (MB/GB)
Amal muddati (kun)
API turi: traffic / rotation
Avtomatik api_key generatsiyasi (UUID4)
Ro‘yxat: foydalanuvchi, limit, holat, tugash muddati
Amal bajarishlar: 
🟢 Activate / 🔴 Deactivate
♻️ Limitni yangilash
⏰ Muddati uzaytirish
🗑 O‘chirish
Model:
apis (api_key, user_id, type, limit, used, expiry_date, status)
💰 6. Withdraws & Balances
Ko‘rsatkichlar:
So‘nggi yechilganlar (GET /admin/withdraws/recent)
USDT (BEP20) manzili, miqdor, holat
Funktsiyalar:
✅ “To‘lovni tasdiqlash” → PATCH /admin/withdraws/{id}/approve
🔄 “Qayta yuborish” → POST /admin/withdraws/{id}/retry
📜 “To‘lov tarixi” → GET /admin/withdraws/history
📡 7. Traffic Pool boshqaruvi
Ko‘rsatkichlar:
Joriy ishlatilayotgan IP’lar soni
Bo‘sh slotlar
Serverlar ro‘yxati (hostname, latency, bandwidth)
Funktsiyalar:
➕ Pool qo‘shish → POST /admin/traffic/pool/add
🔄 IP rotatsiyani tekshirish → GET /admin/traffic/pool/check
📊 MB/s va ping kuzatuv → real-time WebSocket monitoring
📈 8. Analitika & Reports
Grafiklar:
Kunlik foydalanuvchilar soni
Trafik ishlatilishi
Daromad o‘sishi
To‘lovlar statistikasi
Export funksiyasi:
GET /admin/reports/export?type=csv|xlsx|pdf
🗞 9. News & Promo
Funktsiyalar:
📝 Yangi yangilik qo‘shish (POST /admin/news/create) 
Sarlavha, tavsif, havola, rasm
“📢 Telegram push notification” yuborish
Ro‘yxat: GET /admin/news/list
Model:
news (title, description, link, image_url, created_at)
👤 10. Adminlar boshqaruvi
Model:
admins (telegram_id, username, phone, role, created_at)
Ruxsatlar:
SuperAdmin: hamma bo‘limga ruxsat
Moderator: Users, API, Withdraws bo‘limlari
API:
➕ Qo‘shish → POST /admin/admins/add
❌ O‘chirish → DELETE /admin/admins/{id}
🔄 Rollarni tahrirlash → PATCH /admin/admins/{id}
⚙️ 11. System Settings
Funksiyalar:
API konfiguratsiyasi (tokenlar, gateways)
Backup olish → POST /admin/settings/backup
Cron sozlash → POST /admin/settings/cron
Server holati → GET /admin/settings/status
JWT muddati sozlash → PATCH /admin/settings/security
Ma’lumotlar: system_settings (key, value, updated_at)
🔍 12. Logs & Monitoring
Funktsiyalar:
GET /admin/logs/auth → Kirish/chiqish loglari
GET /admin/logs/errors → Xatoliklar
GET /admin/logs/traffic → API chaqiruvlari
Real-vaqt kuzatuv: WebSocket (/ws/admin/monitor)
Model: logs (timestamp, type, message, user_id, ip, level)
🧠 13. Xavfsizlik qatlamlari
HimoyaTavsifJWT Validation24 soatlik token, refresh mexanizmiRole-based accessSuperAdmin / ModeratorIP TrackingAdmin kirish IP kuzatuviAudit TrailHar bir amal loglanadiWebSocket AuthToken bilan himoyalangan kanalTelegram VerifyTelegram ID orqali aniq admin identifikatsiyasi 
🧾 14. Yakuniy Menyu Ko‘rinishi (Frontend Sidebar)
IconBo‘limTavsif📊DashboardUmumiy statistika👥UsersFoydalanuvchilar ro‘yxati🔑API ManagerTrafik API boshqaruvi💰WithdrawsTo‘lovlar nazorati📡Traffic PoolTrafik manbalarini boshqarish📈ReportsKunlik / oylik hisobotlar🗞News & PromoYangiliklar👤AdminsAdminlar boshqaruvi⚙️SettingsTizim konfiguratsiyasi🧾Logs & MonitoringFaoliyat va xatolik loglari


