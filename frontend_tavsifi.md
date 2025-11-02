📱 1. Telegram Auth sahifasi

Maqsadi: foydalanuvchini Telegram orqali tizimga kiritish.
Elementlar:

“Login with Telegram” tugmasi (Telegram Login Widget)

ToS + Privacy Policy havolalari

Login muvaffaqiyatli bo‘lgach → Dashboard sahifasiga o‘tadi


Ko‘rinishi:

┌──────────────────────────────┐
│ 🔒 Telegram orqali kirish     │
│ [ Login with Telegram ]       │
│------------------------------│
│ ✅ Roziman (ToS & Privacy)   │
└──────────────────────────────┘


🏠 Dashboard sahifasi — umumiy tushuncha
🎯 Maqsad:
Foydalanuvchiga uning hisobi, balans holati, trafik faoliyati va real vaqt statistikasini ko‘rsatish.
Bu sahifadan foydalanuvchi:
trafikni yoqadi yoki to‘xtatadi
daromadini ko‘radi
bugungi narxni biladi
balansni yechish tugmasiga o‘tadi
⚙️ Dashboard komponentlari (bloklari)
1️⃣ Profil bloki
Manba: telegram_id, username, first_name, photo_url, auth_date
Ko‘rinish:
🖼️ [Profil rasmi] 👤 Dilshod (@dilshod_uz) 📅 Oxirgi kirish: 2-noyabr 10:14 
👉 Maqsad: foydalanuvchi o‘z Telegram profili orqali tizimda ekanini his qilishi.
Agar rasm mavjud bo‘lmasa, default avatar ishlatiladi.
2️⃣ Balans bloki
Manba: balance_usd (MySQL jadvalidan)
Ko‘rinish:
💰 Balans: $5.70 
Qo‘shimcha:
Daromad animatsiyasi: balans oshganda +$0.10 animatsion tarzda chiqadi.
Valyuta konvertatsiyasi: ($) → (USDT) → (UZS) uchun yon menyu.
3️⃣ Narx va tarmoq bloki
Manba: price_per_gb (admin panel yoki API orqali)
Ko‘rinish:
📊 Bugungi narx: $1.50 / GB 🌍 Region: Global (Auto) 📶 Tarmoq: WiFi / Mobil 
4️⃣ Trafik bloki
Manba: sent_mb va used_mb
Hisoblash:
Qolgan hajm = sent_mb - used_mb 
Ko‘rinish:
📤 Yuborilgan: 4000 MB (4.0 GB) 📥 Ishlatilgan: 3300 MB (3.3 GB) ⏳ Qolgan: 700 MB 
progress bar (foydalangan trafik ulushi)
5️⃣ Harakat tugmalari (Actions)
[ 🟢 START ] [ 🔴 STOP ] [ 💸 YECHISH ] 
START — foydalanuvchi trafik almashish agentini ishga tushiradi
STOP — jarayonni to‘xtatadi
YECHISH — balans $5 dan yuqori bo‘lsa → Withdraw sahifasiga o‘tadi
Xavfsizlik:
Tugmalar real vaqt holatiga qarab avtomatik o‘zgaradi
(masalan, ishlayotgan bo‘lsa, faqat “STOP” ko‘rinadi)
6️⃣ Mini statistik blok
Grafik ko‘rinishda:
📈 Bugungi: +$1.20 📅 O‘tgan 7 kun: $12.40 
Line chart yoki ring diagram orqali.
7️⃣ Quyi panel (nav bar)
🏠 Dashboard 📈 Statistika 💵 Yechish 👤 Profil 
Aktiv holatda “Dashboard” belgisi yoritilgan bo‘ladi.
🧠 Fon funksionallik (backend bilan bog‘liq)
MaqsadAPI endpointTavsifDashboard ma’lumotlarini olish/api/dashboard/<telegram_id>Foydalanuvchi uchun barcha statistik ma’lumotSTART tugmasi/api/traffic/startTrafik almashish jarayonini boshlaydiSTOP tugmasi/api/traffic/stopTrafikni to‘xtatadiBalansni tekshirish/api/user/balanceJoriy balansni qaytaradiTelegram profil rasmiTelegram OAuth dan photo_urlRasm URL dan olinadi 
🎨 UI dizayn konsepsiyasi (ko‘rinish bo‘yicha)
Fon rangi: qora yoki gradient (dark mode)
Balans bloki: neon sariq / yashil
Statistika: yumaloq kartalar (rounded-xl)
Tugmalar: katta, gradientli (green/red/blue)
Profil rasmi: doira shaklida, shadow bilan
Xohlasangiz, endi shu Dashboard sahifasi uchun foydalanuvchi oqimi (UX flow) — ya’ni:
foydalanuvchi sahifaga kirganda nimalar yuklanadi, qaysi API chaqiriladi, qachon yangilanadi


dashbord+ kunlik narx banneri

📢 Kunlik Narx E’lon Qilish (Daily Price Announcement)
🎯 Maqsad:
Har kuni yangi narx belgilanganida foydalanuvchiga real vaqt yoki kunlik e’lon ko‘rinishida ko‘rsatish.
Bu narx foydalanuvchi Dashboard sahifasining yuqorisida chiqadi va avtomatik yangilanadi.
🧩 1️⃣ Ma’lumot manbai
Backend jadvali: daily_price
Ustun nomiTavsifidAuto incrementdateSana (YYYY-MM-DD)price_per_gb1 GB uchun narx (USD)messageAdmin tomonidan yozilgan qisqa izoh (“Bugun trafik narxi pasaydi!”)updated_atO‘zgartirilgan vaqt 
⚙️ 2️⃣ API qismi
Endpoint:
GET /api/daily_price 
Response:
{ "date": "2025-11-02", "price_per_gb": 1.65, "message": "Bugungi narx: $1.65/GB (haftalik aksiyada!)" } 
Frontend (Dashboard) bu endpointni har 5 daqiqada tekshiradi yoki har safar sahifa ochilganda chaqiradi.
🎨 3️⃣ Dashboard sahifasidagi joylashuvi
🔹 Blokning ko‘rinishi:
📢 Kunlik narx e’loni ────────────────────────────── 📅 Sana: 2-noyabr 2025 💸 Narx: $1.65 / GB 📝 Izoh: Bugungi narx: $1.65/GB (haftalik aksiyada!) ────────────────────────────── 
Yoki mobil-friendly tarzda:
📢 Bugungi narx: $1.65 / GB 🗓️ 2-noyabr 2025 | 💬 Haftalik aksiyada! 
🔹 Dizayn:
Gradient fon: #ffd54f → #ffb300 (sariq/orange e’lon ranglari)
Matn: oq yoki qora, qalin (bold)
Har kuni yangilansa, "New!" belgisi animatsion tarzda chiqadi
Tap qilganda → “Narx Tarixi” sahifasiga o‘tadi
🕓 4️⃣ Avtomatik yangilanish mexanizmi
Dashboard ochilganda:
Ilova /api/daily_price ni chaqiradi
So‘nggi narx foydalanuvchi sessiyasida saqlanadi
Agar yangi sana bo‘lsa → bannerda “Yangi narx e’loni!” degan belgini chiqaradi
🔔 5️⃣ Eslatma / Notification tizimi
Agar siz backendda Firebase yoki Telegram notification tizimi qo‘shmoqchi bo‘lsangiz —
admin yangi narx e’lon qilganida barcha foydalanuvchilar push notification oladi:
Masalan:
📢 “Bugungi narx: $1.65/GB — kechasi 00:00 gacha amal qiladi!”

Bu tizim price_update_notifier.py nomli modul orqali amalga oshiriladi (agar xohlasangiz, uni keyin yozamiz).
📊 6️⃣ Qo‘shimcha interfeys g‘oyasi:
Dashboard’ning yuqori qismida slayder-banner sifatida:
Chapda foydalanuvchi ismi
O‘rtada “bugungi narx”
O‘ngda “avvalgi narx bilan solishtirish”
Masalan:
🔹 Dilshod, bugun narx: $1.65/GB ⬆️ +0.15 taqqoslaganda kechagiga nisbatan 
Xullas, kunlik narx e’loni Dashboard’da doimiy ko‘rinib turadi va foydalanuvchiga bugungi daromad sharoitini anglatadi.
push notifications tool

Foydalanuvchi sahifani ochmagan bo‘lsa ham, “Bugungi narx e’loni” yoki “Balansingiz oshdi” kabi xabarni oladi 📲
🚀 1️⃣ Umumiy maqsad
Push Notification — foydalanuvchining qurilmasiga to‘g‘ridan-to‘g‘ri yuboriladigan xabar.
Bu tizim mobil ilova (Flutter, React Native, PWA) yoki web browser uchun ishlaydi.
Sizning ilovada u quyidagi holatlarda yuboriladi:
🕒 Har kuni yangi narx e’lon qilinganda
💰 Balans yangilanganda
⚠️ Tarmoq to‘xtatilganda yoki qayta yoqilganda
🧩 2️⃣ Texnologiya tanlovi
Eng barqaror va universal yechimlar:
VariantPlatformaAfzalliklariFirebase Cloud Messaging (FCM)Android, iOS, WebEng mashhur, bepul, real-timeOneSignalAndroid, iOS, WebJuda oson integratsiya, analitika mavjudWeb Push API (native)Chrome, Firefox, SafariServerdan bevosita brauzerga yuborish 
👉 Tavsiya: sizda Google Cloud ishlatilgani uchun Firebase Cloud Messaging (FCM) ideal tanlov.
🔧 3️⃣ Foydalanuvchi tomoni (frontend) oqimi
1. Foydalanuvchi login qilganda
Telegram orqali kiradi
Ilova FCM SDK orqali device_token oladi
Shu tokenni backendga yuboradi
Yuboriladigan ma’lumot:
{ "telegram_id": 523414231, "device_token": "fcm_eb3a8ef9as3f2..." } 
🗄️ 4️⃣ Backenddagi saqlash (MySQL jadval)
users jadvaliga yangi ustunlar qo‘shamiz:
UstunTavsifdevice_tokenFCM push tokennotifications_enabledbool (foydalanuvchi ruxsat berganmi) 
⚙️ 5️⃣ Backend — Push yuborish logikasi
Admin narx yangilaganda (POST /api/admin/set_price) →
backend Notifier Service ga signal yuboradi →
u barcha device_token larni olib, FCM orqali yuboradi.
Server logikasi (oddiy tushuncha):
1. Admin yangi narxni kiritadi 2. Bazaga yoziladi 3. Notifier barcha device_token larni oladi 4. Firebase API orqali push yuboradi 
📨 6️⃣ FCM Notification yuborish namunasi
HTTP POST → https://fcm.googleapis.com/fcm/send
Headers:
Content-Type: application/json Authorization: key=AAAAxxxxxxxx:APA91bH... 
Body:
{ "to": "fcm_eb3a8ef9as3f2...", "notification": { "title": "📢 Kunlik narx yangilandi!", "body": "Bugungi narx: $1.65 / GB — 10% oshdi!", "icon": "https://yourapp.com/logo.png" }, "data": { "type": "daily_price", "price": 1.65 } } 
🔁 7️⃣ Foydalanuvchi tomoni — xabarni qabul qilish
Frontend (masalan Flutter yoki React):
Foydalanuvchi ilova ochiq bo‘lsa → banner ko‘rsatadi
Ilova yopiq bo‘lsa → tizim tray’da (Android bildirishnoma oynasi) chiqadi
Xabar ustiga bosilganda: ilova Dashboard sahifasini ochadi va /api/daily_price dan yangilangan narxni ko‘rsatadi.
🧠 8️⃣ Qo‘shimcha xususiyatlar
FunksiyaTavsifSegmentlashFaqat aktiv foydalanuvchilarga yuborish (masalan: oxirgi 3 kun ichida kirganlar)Silent PushIlova fon rejimida yangilanadi, lekin bildirishnoma chiqmaydiQo‘lda o‘chirishFoydalanuvchi bildirishnomani o‘chirsa, notifications_enabled = 0 qilinadi 
💬 9️⃣ UX ko‘rinishi
📢 Kunlik narx yangilandi!
Bugungi narx: $1.65 / GB — 10% oshdi!
[Ilovani ochish]

Bosilganda ilova ochiladi va Dashboard sahifasida sariq banner animatsiya bilan chiqadi:

🔥 “Yangi narx e’loni!”
🔒 10️⃣ Xavfsizlik
FCM Server Key faqat backendda saqlanadi
Tokenlar har 30 kunda yangilanadi
unsubscribe holatlari kuzatilib turadi


Quyida START bosilganda telefon bildirishnomalar panelida (notification area) trafik hajmini va real-vaqt hisob-kitobini qanday chiroyli, xavfsiz va amaliy ko‘rsatish kerakligini kodsiz, lekin texnik jihatdan aniq va bajariladigan qadamlar bilan yozib berdim.
Umumiy g‘oya (xulosa)
Android: real-vaqt va doimiy yangilanadigan “ongoing” (foreground) bildirishnoma orqali foydalanuvchiga hozirgi yuborilayotgan trafik hajmi, tezligi va sessiya davomiyligi ko‘rsatiladi. Bu eng ishonchli va tezkor yechim.
iOS: tizim cheklovlari sababli Android kabi doimiy notifikatsiya (continuous live update in notification drawer) cheklangan. iOS uchun ilova ichida real-vaqt panel (foreground) va vaqtinchalik push/local notifications (masalan har 1–5 daqiqada summary) tavsiya qilinadi.
Server/Backend: ilova doimiy ravishda serverga “heartbeat” / report/sent yuboradi (masalan har 5–30 soniya yoki har 100 MB) — bu statistikani serverda saqlash va balansni yangilash uchun kerak. Lekin telefon panelidagi real-vaqt hisoblash asosiy ravishda telefon tomonidan olinadi (tizim darajasida VpnService/Packet tunnel ilovada bytes counterni hisoblaydi).
Batafsil ish rejasi (qadam-baqadam, kodsiz)
1) START bosilganda tekshiruvlar
Foydalanuvchi START bosadi.
Ilova backendga so‘rov yuboradi: /api/traffic/start — token, device id, geo/IP tekshiruvi, region (US/EU) va ToS tasdiqlanganligini tekshiradi.
Backend hammasi OK deb qaytsa → ilovaga ok qaytaradi.
Ilova localda tunnel (VpnService/NEPacketTunnelProvider) ishga tushuradi va foreground service boshlaydi (Android).
Foreground service ishga tushganda telefon panelida ongoing notification paydo bo‘ladi.
2) Android: real-vaqt notification dizayni va yangilanish mexanizmi
A) Notification turi
Ongoing / Foreground notification (foydalanuvchi o‘chirib bo‘lmaydigan emas, lekin odatda STOP bosilganda yoki appdan action orqali o‘chiriladi).
Notification ichida: 
Sarlavha (title): Trafik ulanishi faol yoki Sharing traffic — On
Asosiy qator (big): Yuborilgan: 1.24 GB
Ikkinchi qator: Tezlik: 0.45 MB/s • Vaqt: 00:12:23
Progress bar: progress = used_mb_of_session / quota_mb yoki millisec-based indicator
Action tugmalari: [STOP] (to‘g‘ridan-to‘g‘ri notification ichidan), [Dashboard] (ilovani ochish)
B) Yangilanish chastotasi (recommendation)
Realtime feel: yangilanish har 1–5 soniyada: agar foydalanuvchi juda tez tarmoqqa ulangan bo‘lsa, 1–2s; normal holat uchun 3–5s.
Server reporting: ilova har 5–30 soniyada yoki har 100 MB yuborilganda /report/sent endpointiga yuboradi. (Bu serverga ortiqcha yuk solmaslik uchun sozlanadi.)
C) Ko‘rsatiladigan maydonlar (notification fields)
session_sent_mb — ushbu sessiyada yuborilgan jami MB (masalan: 1240 MB yoki 1.24 GB)
session_rate — joriy tezlik (MB/s yoki KB/s)
session_duration — sessiya davomiyligi (hh:mm:ss)
today_price — bugungi narx (masalan 1.65 $/GB) — optional, agar kerak bo‘lsa
estimated_earnings — hozirgacha ishlatilgan MB ga ko‘ra taxminiy daromad: ≈ $0.002 (agar foydalanuvchi qiziqsangiz ko‘rsatilsin)
Misol ko‘rinishi:
[Trafik ulashishi — Faol] Yuborilgan: 1.24 GB Tezlik: 0.45 MB/s • Vaqt: 00:12:23 [||||||||----] 62% [STOP] [OPEN APP] 
D) Qoida va cheklovlar
Battery: juda qisqa intervallar bilan yangilash batareyani tez tug‘diradi — ilovada battery_saver_mode bo‘lsa 5–15s yoki 30s ga oshirish tavsiya etiladi.
Permission: Androidda FOREGROUND_SERVICE ruxsat talab qilinadi; foydalanuvchidan explanation ko‘rsating.
Privacy: notification ichida shaxsiy moliyaviy tafsilotlarni (to‘liq balans) ko‘rsatishdan oldin foydalanuvchi roziligini oling (sensitive info toggle).
3) iOS: cheklovlar va tavsiya etilgan yechimlar
Cheklov
iOS notification center da Android kabi doimiy progress yangilashni amalga oshirish qiyin (va ko‘plab fon operatsiyalar cheklangan). UNNotification yangilanishlar faqat push orqali yoki local notification orqali amalga oshiriladi va tez-tez yangilash OS tomonidan bloklanishi mumkin.
Tavsiya
Ilova ichida: sessiya boshida ilova ochiq bo‘lsa — real-vaqt UI (top of screen) orqali batafsil statistikani ko‘rsating (bu iOS foydalanuvchilari uchun asosiy route).
Periodic summary push/local: ilova background holatda bo‘lsa, server tomonidan silent push (data-only push) yuborib, ilovani uyg‘otish va so‘ngra local notification orqali summary chiqarish (har 1–5 daqiqa emas, balki 1 yoki 5 minutlik summary). Lekin Apple silent pushes bilan cheklaydi — barchasi kafolatlanmaydi.
Handoff to app: notification ustiga bosilganda ilova ochilsin va sessiya yangilanib real-vaqt ko‘rsatiladi.
4) Web (PWA) — browser notification
Service Worker yordamida Push API orqali xabar yuborish mumkin. Ammo browser-ning ochiq sessiya bo‘lmasa real-vaqt yangilanish cheklangan. Tegishli UX: ilova ochilganda ichki grafik + periodic push summary.
5) Server-side va telemetry integratsiyasi
A) Lokal hisoblash + server hisobi
Local (ilova): VpnService/Network stack orqali to‘g‘ridan-to‘g‘ri byte counting — shu qiymat asosida notification yangilanadi (eng aniq va kam kechikuvli).
Server (authoritative): ilova belgilangan intervallar bilan (report/sent) serverga yuboradi va serverda pending_chunks ga qo‘shadi. Server bilan tenglashtirish (reconciliation) sessiya yakunida yoki ma’lum vaqtlarda amalga oshiriladi.
B) Endpoint’lar (conceptual, kodsiz)
POST /api/traffic/heartbeat — device → server (device_id, session_id, sent_mb, timestamp).
GET /api/session/<session_id>/summary — server → frontend (yig‘ilgan ma’lumotlar).
Serverdan push yuborish faqat muhim voqealar uchun: threshold reached (masalan qo‘shimcha 100 MB yuborildi), balance updated, session stopped va hokazo.
6) UX & Notification copy (o‘zbekcha misollar)
Title: 📡 Trafik ulashish: faol
Body (short): Yuborilgan: 1.24 GB • Tezlik: 0.45 MB/s
Tapping action: Ilovani ochish → Dashboard (session view)
STOP action: To‘xtatish (confirmation dialog: “To‘xtatish bilan hozirgi sessiya hisoblanadi. Davom etilsinmi?”)
Qo‘shimcha summary notification (masalan har 10 daqiqa):
🧾 Sessiya yangiligi
So‘nggi 10 daqiqada 120 MB yuborildi. Jami: 1.24 GB. Taxminiy daromad: $0.002.
7) Battery, privacy va security maslahatlari
Yangilanish intervallarini foydalanuvchi sozlamalaridan boshqarish: realtime / balanced / battery_saver.
Local notification uchun hech qanday server credential kerak emas; FCM server key faqat serverda saqlansin.
Trafik monitoring faqat hajmni hisoblasin — foydalanuvchi trafik mazmunini yozmang (privacy).
Foydalanuvchidan “notification content” (balans va daromadni) bildirishnomada ko‘rsatishni ruxsat qilib qo‘yish.
8) Amalga oshirish bo‘yicha tavsiya etilgan parametrlar (default)
Notification update interval (Android local): 3 s
Server report interval: 10 s yoki har 100 MB (qaysi biri avval bo‘lsa)
Summary push (agar ilova background): har 1 yoki 5 daqiqa (iOS chekloviga qarab sozlash)
Progress bar: ko‘rsatish uchun sessiya quota yoki mobilning oo limitiga qarab (masalan: foydalanuvchi kundalik limitini belgilasa)

💳 BALANCE SAHIFASI – to‘liq ko‘rinish
🧭 Navigatsiya
➡️ Home → Dashboard → Balance
➡️ Yon menyuda:
Balance, Withdraw, Statistics, Settings, Support
📱 BALANCE (Hisob) sahifasining UI dizayni
🔹 Asosiy qism:
👤 Profil bloki
ElementMa’lumotProfil rasmiTelegram rasm (photo_url)Ismfirst_nameUsername@usernameTelegram IDtelegram_idOxirgi faol vaqtauth_date 
💰 Balans ma’lumotlari
📦 Umumiy hisob:
Balans: $12.54
Yuborilgan trafik: 184.3 MB
Sotilgan trafik: 139.8 MB
Daromad kunlik: $0.48
Daromad oy boshidan: $8.32
🟢 Tugmalar:
🔁 Yangilash (Refresh)
💸 Pul yechish (Withdraw) → alohida sahifaga yo‘naltiradi
📊 Tranzaksiya tarixi (faqat balans bilan bog‘liq)
SanaAmal turiMiqdorHolat2025-10-30Daromad+$0.48✅2025-10-29Daromad+$0.52✅2025-10-28To‘lov-$1.40✅2025-10-25To‘lov-$2.75⏳ Kutilmoqda 
⬇️ Tugma: Ko‘proq ko‘rsatish (Load more)
🔔 Bildirishnomalar (mini-panel)
So‘nggi 3 ta push:
💸 “$1.4 USDT to‘lovingiz amalga oshirildi.”
🕓 “To‘lov so‘rovingiz BEP20 tarmog‘ida kutilmoqda.”
🔐 “Hisobingiz muvaffaqiyatli yangilandi.”
⚙️ BACKEND – API aloqalari
Endpointlar
MetodURLTavsifGET/api/user/balance/<telegram_id>Foydalanuvchi balans, trafik, va so‘nggi tranzaksiyalarni olib keladiPOST/api/user/refresh_balanceBalansni real-vaqt yangilaydi (tizimdagi trafik asosida)GET/api/transactions?limit=10Tranzaksiya tarixini qaytaradiGET/api/user/notificationsSo‘nggi push bildirishnomalar ro‘yxati 
💾 Database jadval strukturasi
users
ustunma’noidAuto incrementtelegram_idUnikal foydalanuvchi IDusernameTelegram usernamefirst_nameIsmphoto_urlTelegram rasmi URLauth_dateOxirgi loginjwt_tokenToken (auth uchun)balance_usdJoriy balanssent_mbYuborilgan trafikused_mbSotilgan trafik 
transactions
ustunma’noidAuto incrementtelegram_idFoydalanuvchi IDtype“income” yoki “withdraw”amountUSD miqdorstatuscompleted / pending / failedcreated_atSana 
🧩 Interaktiv logika
“Refresh” bosilganda: 
/api/user/refresh_balance chaqiriladi
tizim real vaqt trafikni hisoblab, balansni yangilaydi
UI’da progress bar chiqadi (Balansing…)
“Pul yechish” bosilganda: 
/withdraw sahifasiga yo‘naltiriladi
U yerda alohida Withdraw sahifa (2-qism) ochiladi
🔔 Push Notification
Har bir tranzaksiya tugagach, foydalanuvchiga:
“Balans yangilandi: +$0.45”
“Pul yechildi: -$1.40 (USDT BEP20)”
“To‘lov muvaffaqiyatli yakunlandi”
ko‘rinishidagi push xabarnoma yuboriladi.

Withdraw (yechish) qismi alohida sahifa bo‘ladi.

Withdraw (Pul yechish) sahifasini to‘liq ishlab chiqamiz 💸
Bu sahifa foydalanuvchiga o‘z balansidagi mablag‘ni USDT (BEP20) orqali avtomatik tarzda yechib olish imkonini beradi, siz aytganidek, universal payment API bilan ishlaydi.
💸 WITHDRAW SAHIFASI – to‘liq dizayn va arxitektura
🧭 Navigatsiya
➡️ Home → Balance → Withdraw
📱 UI (foydalanuvchi interfeysi)
🔹 Sarlavha:
Pul yechish (USDT – BEP20)
Hisobingizdagi mablag‘ni avtomatik tarzda yechib olishingiz mumkin.

🔹 Balans bloki:
Joriy balans: $12.54
Minimal yechish: $1.39
Maksimal bir martalik yechish: $100.00
Progress bar:
🟩 $12.54 / $100.00
🔹 Yechish formasi:
MaydonTavsif💳 Manzil (wallet)BEP20 USDT manzilini kiriting (0x...)💰 Miqdor (USD)Yechmoqchi bo‘lgan summani kiriting (masalan, 5.00) 
🔘 Checkbox:

[✓] Men BEP20 manzilini to‘g‘ri kiritganimni tasdiqlayman.
🔹 Tugma:
[ Pulni yechish ]
(Bosilganda loader chiqadi: “To‘lov so‘rovi yuborilmoqda…”)
🔹 Natija paneli:
✅ Agar muvaffaqiyatli bo‘lsa
:
“To‘lov so‘rovingiz qabul qilindi! Sizga yaqin daqiqalarda USDT (BEP20) tarzida yuboriladi.
”
⚠️ Agar xatolik bo‘l
sa:
“Mablag‘ yetarli emas yoki BEP20 manzili noto‘g‘r
i.”
⚙️ BACKEND – ishlash jarayoni
1️⃣ So‘rov yuborish
Foydalanuvchi formani to‘ldiradi → API ga POST yuboradi:
POST /api/withdraw { "telegram_id": 523643, "amount_usd": 5.00, "wallet_address": "0x1234abcd...", "token": "<jwt_token>" } 
2️⃣ Server tekshiruvi
Backend:
Foydalanuvchi mavjudligini tekshiradi
Balans ≥ 1.39 ekanligini tasdiqlaydi
withdraw_requests jadvaliga yozadi: status = 'pending' created_at = now() 
3️⃣ Avtomatik to‘lov (Payment Provider API orqali)
Backend PaymentProvider.create_payout() funksiyasini chaqiradi:
provider.create_payout(address="0x...", amount_usd=5.00) 
API qaytaradi:
{ "payout_id": "TXN12345", "status": "processing" } 
So‘rov DB ga quyidagicha yoziladi:
UstunQiymattelegram_id523643amount_usd5.00wallet_address0x1234abcdpayout_idTXN12345statusprocessing 
4️⃣ Holat monitoringi
Background task (cron / scheduler) har 10 daqiqada:
get_status(payout_id) funksiyasini chaqiradi
Agar status = completed bo‘lsa: 
withdraw_requests.status = 'completed'
users.balance_usd dan ayiriladi
Push yuboriladi: “💸 To‘lov muvaffaqiyatli yakunlandi!”
🧾 Database struktura
withdraw_requests
UstunMa’nosiidAuto incrementtelegram_idFoydalanuvchi IDamount_usdMiqdorwallet_addressUSDT BEP20 manzilpayout_idAPI dan qaytgan IDstatuspending / processing / completed / failedcreated_atSanaprocessed_atYakunlangan vaqt 
🔔 Push xabarlar
HolatXabarpending“Pul yechish so‘rovingiz qabul qilindi.”processing“To‘lov BEP20 tarmog‘ida amalga oshirilmoqda.”completed“To‘lov muvaffaqiyatli yakunlandi.”failed“To‘lov amalga oshmadi. BEP20 manzilingizni tekshiring.” 
🧠 Qo‘shimcha himoya
Agar foydalanuvchi 1 daqiqada 1 martadan ko‘p so‘rov yuborsa → “Anti-spam” xatosi.
Yechilayotgan miqdor 1.39$ dan kichik bo‘lsa, so‘rov qabul qilinmaydi.
Manzil formati 0x[a-fA-F0-9]{40} ga mos kelmasa, invalid address deb chiqadi.
Har bir foydalanuvchi uchun so‘nggi 5 ta yechish tarixi ko‘rsatiladi.
📊 WITHDRAW TARIXI (shu sahifada pastda)
SanaMiqdorHolatPayout ID2025-10-30$5.00✅ YakunlandiTXN32142025-10-25$2.75⏳ KutilmoqdaTXN31992025-10-21$1.40❌ Rad etildiTXN3187 
📱 Umumiy foydalanuvchi oqimi (User Flow)

📈 Statistika (Analytics) sahifasi.

Bu sahifa foydalanuvchiga trafik, daromad va narx o‘zgarishlarini vaqt bo‘yicha tahlil qilish imkonini beradi — ya’ni, ilovaning yuragi bo‘lgan real-time analitika markazi bo‘ladi.
📈 STATISTIKA (Analytics) sahifasi – to‘liq dizayn va arxitektura
🧭 Navigatsiya
➡️ Home → Dashboard → Analytics
📱 UI (foydalanuvchi interfeysi)
🔹 Sarlavha:
Trafik va daromad statistikasi

🔹 Foydalanuvchi ma’lumot bloki (tepada)
ElementTavsif👤 Profil rasmiTelegram rasmi (photo_url)🧾 Ismfirst_name💰 Balans$12.54📆 Oxirgi yangilanish2025-11-02 14:10 
🔹 1️⃣ Kunlik grafika
📊 Bugungi faoliyat:
Trafik yuborilgan: 128 MB
Trafik sotilgan: 97 MB
Daromad: $0.43
Narx: $0.0042 / MB
📈 Grafik turi: Line chart (kun davomida vaqt bo‘yicha o‘zgarish)
X o‘qi — soatlar (00:00 → 23:00)
Y o‘qi — MB yoki $ qiymatlar
👉 Grafiklar switch (tabs) orqali almashtiriladi:
Trafik yuborilgan
Trafik sotilgan
Daromad
Narx
🔹 2️⃣ Haftalik umumiy ko‘rsatkich
📊 So‘nggi 7 kun:
SanaYuborilgan (MB)Sotilgan (MB)Daromad ($)Narx ($/MB)10/272101680.840.004010/281951700.810.004110/292502130.930.004410/302702240.980.004510/312301900.880.004211/011851560.760.004111/02128970.430.0042 
📈 Grafik turi: Bar chart (haftalik)
X o‘qi — kunlar
Y o‘qi — MB yoki $
🔹 3️⃣ Oylik tahlil (Month Summary)
🗓️ Noyabr 2025
Umumiy trafik yuborilgan: 4.13 GB
Umumiy trafik sotilgan: 3.26 GB
Jami daromad: $13.88
O‘rtacha kunlik narx: $0.0043 / MB
📈 Grafik turi: Area chart — oylik o‘sish dinamikasi
Har kuni o‘sib boruvchi daromad ko‘rinadi (cumulative profit line).
🔹 4️⃣ Filtrlash / So‘rov paneli
Foydalanuvchi quyidagilarni tanlay oladi:
🔘 “Kunlik” | 🔘 “Haftalik” | 🔘 “Oylik”
📆 Sana oralig‘i (date_from / date_to)
🔄 “Yangilash” tugmasi
⚙️ BACKEND – API va hisoblash
Endpointlar:
MetodURLTavsifGET/api/stats/daily/<telegram_id>Kunlik trafik va daromadGET/api/stats/weekly/<telegram_id>Haftalik statistikaGET/api/stats/monthly/<telegram_id>Oylik tahlilGET/api/stats/ratesHar kuni narxlar o‘zgarishi (market API orqali) 
Jadval: traffic_logs
UstunMa’nosiidAuto incrementtelegram_idFoydalanuvchi IDsent_mbYuborilgan trafiksold_mbSotilgan trafikprofit_usdShu davrda topilgan daromadprice_per_mbMB narxi ($)perioddaily / weekly / monthlycreated_atSana va vaqt 
🔄 Hisoblash logikasi (algoritm)
Kunlik yangilanish: 1️⃣ Har 1 soatda foydalanuvchining sent_mb va used_mb qiymatlari yig‘iladi
2️⃣ profit_usd = sold_mb × price_per_mb
3️⃣ Yangi satr traffic_logs ga yoziladi (period=daily)
4️⃣ Haftalik va oylik qiymatlar avtomatik ravishda agregatsiya qilinadi (SUM, AVG orqali)
5️⃣ Natija API orqali Analytics sahifasiga yuboriladi.
🔔 Push notification (Analytics bilan bog‘liq)
VaqtXabarHar kuni soat 00:00“📊 Bugungi hisobot tayyor! Siz $0.43 topdingiz.”Haftada bir marta“Sizning haftalik daromadingiz: $5.12 (↑ +12%).”Oy tugaganda“🎉 Oy yakuni: $13.88 USDT foyda bilan!”

Sozlamalar (Settings) sahifasi 

— To‘liq tuzilma
🎯 Maqsad:
Foydalanuvchi o‘z ilova tajribasini moslashtira oladi: til, bildirishnoma, xavfsizlik va energiya sarfini boshqaradi.
🧩 UI tuzilishi (bo‘limlar bo‘yicha)
1️⃣ Tizim tili (Language)
Variantlar: 🇺🇿 O‘zbek, 🇷🇺 Rus, 🇬🇧 English
Tanlangandan so‘ng butun interfeys shu tilda yangilanadi (dynamic locale reload).
Ma’lumotlar lokal SharedPreferences yoki localStorageda saqlanadi.
Backendga PATCH /user/settings orqali language parametri yuboriladi.
2️⃣ Bildirishnomalar (Notifications)
🔘 Push notification → On/Off
🔘 Session info notification → On/Off
🔘 System update → On/Off
Har bir o‘zgarish API orqali real vaqtda saqlanadi: PATCH /user/settings { "push_notifications": true, "session_updates": false, "system_updates": true } 
3️⃣ Xavfsizlik (Security)
🔐 2FA yoqish (Google Authenticator yoki SMS Telegram orqali)
🧱 Logout all sessions → barcha aktiv sessiyalarni tugatadi
⚠️ “Sessiyani himoyalash” — faqat bitta qurilmadan kirish cheklovi
Backend:
POST /user/security/2fa POST /user/logout_all PATCH /user/settings { "single_device_mode": true } 
4️⃣ Battery Saver (Quvvat tejash rejimi)
🔋 Rejim yoqilganda ilova fon jarayonlarini kamaytiradi
(masalan: session info refresh interval 1s → 10s)
Lokal sozlama sifatida saqlanadi (localStorage)
5️⃣ Qo‘shimcha (Optional)
🌗 Tema: Dark / Light
🧹 Cache tozalash
🧾 Versiya ma’lumotlari (App v1.0.0)
📞 Fikr bildirish (Redirect to Support)
🧠 Backend ma’lumot modeli
Jadval: user_settings
Ustun nomiTuriTavsifidintPrimary Keyuser_idintFoydalanuvchiga bog‘langanlanguagevarchar(10)“uz”, “en”, “ru”push_notificationsbooleantrue/falsesession_updatesbooleantrue/falsesystem_updatesbooleantrue/falsetwo_factor_enabledbooleantrue/falsesingle_device_modebooleantrue/falsebattery_saverbooleantrue/falsethemevarchar(10)“light” yoki “dark”last_updatedatetimeOxirgi sozlama o‘zgarishi 
🔄 Backend API endpointlar
EndpointMetodTavsif/user/settingsGETFoydalanuvchi sozlamalarini olish/user/settingsPATCHSozlamalarni yangilash/user/security/2faPOST2FA faollashtirish/user/security/disable_2faPOST2FA o‘chirish/user/logout_allPOSTBarcha sessiyalarni tugatish 
🖥️ UI Design g‘oya:
Har bir bo‘lim Card ko‘rinishida bo‘ladi.
Switch yoki Toggle butonlar ishlatiladi.
Pastda “Saqlash” tugmasi.
O‘zgartirilgandan so‘ng “✅ Sozlamalar yangilandi” bildirishnomasi chiqadi.
Xulosa qilib aytganda:
Settings sahifasi — foydalanuvchi uchun moslashuvchan boshqaruv paneli bo‘lib,
til, xavfsizlik, bildirishnoma, va energiya sarfini to‘liq boshqarish imkonini beradi.

Sessiyalar tarixi (Session History) sahifasi

Bu sahifa foydalanuvchi uchun trafik faoliyatining shaffof nazorat markazi bo‘ladi.
🧾 8. Sessiyalar tarixi (Session History)
🎯 Maqsad:
Foydalanuvchi o‘zining avvalgi trafik sessiyalarini, ularning davomiyligi, ishlatilgan MB, topilgan daromadi, va statusini ko‘ra oladi.
🧩 UI tuzilishi
🔹 Sahifa nomi:
"Sessiyalar tarixi" yoki "Session History"
🔹 Yuqori qism:
🔍 Filter paneli: 
Sana oralig‘i (📅 from → to)
Holat: Faol, Tugallangan, Xato, Bekor qilingan
Tugma: “🔄 Yangilash”
🔹 Asosiy ro‘yxat (Session cards)
Har bir sessiya uchun Card (kartochka) quyidagi ma’lumotlarni ko‘rsatadi:
MaydonNamuna qiymatTavsif📅 Sana2025-10-25 14:31Sessiya boshlangan vaqt⏱️ Davomiylik02:13:45Ulanish muddati📊 Yuborilgan trafik184 MBFoydalanuvchi tarmoq orqali uzatgan hajm💵 Daromad$0.37Ushbu sessiyadan olingan foyda🟢 Holat“Tugallangan”Sessiya statusi🌐 IP / Location185.92.14.22 🇺🇸Tarmoq ma’lumotlari⚙️ Qurilma turiAndroid / iOSFoydalanuvchi ulanish manbai 
🔹 Pastki panel (Analytics qisqacha):
Bugun: 3 sessiya, 574 MB, $1.22
Hafta: 18 sessiya, 2.4 GB, $7.89
O‘rtacha foyda/sessiya: $0.43

🧠 Backend ma’lumot modeli
Jadval: sessions
Ustun nomiTuriTavsifidintPrimary keyuser_idintFoydalanuvchi IDstart_timedatetimeSessiya boshlanish vaqtiend_timedatetimeTugash vaqtidurationvarchar(20)Format: HH:MM:SSsent_mbdecimal(10,2)Yuborilgan trafik hajmiearned_usddecimal(10,2)Foydalanuvchi topgan summastatusenum(‘active’, ‘completed’, ‘failed’, ‘cancelled’)Sessiya holatiip_addressvarchar(64)Ulanuvchi IPlocationvarchar(64)Avtomatik geolokatsiyadevicevarchar(64)Qurilma nomicreated_atdatetimeYozuv yaratilgan vaqt 
🔄 Backend API endpointlar
EndpointMetodTavsif/sessionsGETBarcha sessiyalar ro‘yxati/sessions/{id}GETBitta sessiya tafsilotlari/sessions/summaryGETKunlik, haftalik va oylik statistikalar/sessions/activeGETFaol sessiyalar ro‘yxati/sessions/filterPOSTSana va holat bo‘yicha filtrlash 
⚙️ API javob namunasi:
[ { "id": 44, "start_time": "2025-10-25T14:31:00Z", "end_time": "2025-10-25T16:44:00Z", "duration": "02:13:00", "sent_mb": 184.5, "earned_usd": 0.37, "status": "completed", "ip_address": "185.92.14.22", "location": "New York, USA", "device": "Android", "created_at": "2025-10-25T14:31:00Z" } ] 
📱 UI dizayn g‘oyasi:
Har bir sessiya uchun rounded card (light shadow, gradient border).
Harakat paytida status ranglari: 
🟢 Active
🔵 Completed
🟠 Failed
🔴 Cancelled
“Yana yuklash” (load more) tugmasi infinite scroll bilan.
Grafik moduli bilan integratsiya (kunlik sessiya soni histogrammasi).
🔔 Qo‘shimcha imkoniyatlar:
🔁 Sessiyani qayta tahlil qilish (AI tomonidan sifat bahosi)
📤 CSV export: foydalanuvchi o‘z sessiyalarini yuklab olishi mumkin
📅 Haftalik avtomatik email/notification xabarnoma: “Siz 2.4 GB trafik yubordingiz, $7.89 topdingiz!”

Natija:
“Sessiyalar tarixi” foydalanuvchining har bir faoliyati bo‘yicha to‘liq shaffof hisobot beradi — qancha ishlaganini, qayerdan ulanganini va tizim barqarorligini kuzatish uchun asosiy modul bo‘ladi.

Qo‘llab-quvvatlash (Support) sahifasi.


Bu sahifa foydalanuvchi uchun to‘g‘ridan-to‘g‘ri aloqa kanali bo‘ladi, ya’ni u yordam kerak bo‘lsa, ilovadan chiqmasdan admin yoki support jamoasiga yozishi mumkin.
🗂️ 9. Qo‘llab-quvvatlash (Support) sahifasi — to‘liq tuzilma
🎯 Maqsad:
Foydalanuvchiga tez va bevosita yordam berish. U support jamoasiga xabar yuboradi, tizim esa uni ruxsat etilgan admin Telegram hisobiga (masalan, @adminsupport) yo‘naltiradi.
🧩 UI tuzilishi
🔹 Sahifa nomi:
“Qo‘llab-quvvatlash” yoki “Support”
🔹 Yuqori qism (Header)
Sarlavha: “Yordam markazi”
Tagline: “Savolingiz bormi? Biz sizga yordam beramiz 👩‍💻”
🔹 Asosiy forma
MaydonTavsif👤 IsmFoydalanuvchining Telegramdan kelgan ismi (readonly)🆔 Telegram IDAvtomatik aniqlanadi (readonly)✉️ Xabar mavzusi (Subject)Matn maydoni — foydalanuvchi mavzuni qisqacha yozadi🗒️ Xabar matni (Message)Keng textarea — foydalanuvchi muammo yoki savolini batafsil yozadi📎 Rasm yoki fayl qo‘shish (optional)Ekran tasviri yoki fayl yuklash imkoniyati🚀 Yuborish tugmasiBosilganda xabar serverga jo‘natiladi, va avtomatik tarzda Telegram’dagi @adminsupport hisobiga forward qilinadi 
🔹 Xabar yuborilgandan so‘ng:
✅ Snackbar / Toast:
“Xabaringiz yuborildi! Admin tez orada siz bilan bog‘lanadi.”

🧠 Backend logikasi
Jadval: support_requests
Ustun nomiTuriTavsifidintPrimary keyuser_idintFoydalanuvchi IDsubjectvarchar(255)MavzumessagetextXabar matniattachment_urlvarchar(255)Rasm yoki fayl URLstatusenum('new','read','replied','closed')Holatcreated_atdatetimeYuborilgan vaqtupdated_atdatetimeYangilanish vaqti 
🔄 API endpointlar
EndpointMetodTavsif/support/sendPOSTYangi support xabarini yuborish/support/historyGETFoydalanuvchining oldingi murojaatlari/support/{id}GETBitta murojaat tafsiloti/support/reply/{id}POSTAdmin tomonidan javob (faqat panelda) 
📨 POST /support/send namuna:
{ "user_id": 105, "subject": "To‘lov kechikdi", "message": "Men 1.39$ yechdim, lekin USDT hali kelmadi.", "attachment_url": "https://cdn.app.com/uploads/screenshot_01.png" } 
🔗 Telegram integratsiya:
Server xabar kelgach, avtomatik tarzda quyidagini bajaradi:
requests.post() orqali Telegram Bot API’ga yuboradi:
https://api.telegram.org/bot<ADMIN_BOT_TOKEN>/sendMessage 
va matn:
📩 Yangi support xabari: 👤 Foydalanuvchi: @username 🆔 ID: 105 📝 Mavzu: To‘lov kechikdi 💬 Matn: Men 1.39$ yechdim, lekin USDT hali kelmadi. 
Agar attachment mavjud bo‘lsa, sendPhoto yoki sendDocument orqali yuboriladi.
📱 UI dizayn g‘oyasi:
Oddiy, sokin fon (light gradient).
Form inputlar rounded.
“Yuborish” tugmasi ko‘k yoki yashil gradientda.
Har bir yuborilgan xabar “history” ichida ko‘rinadi (status bilan).
🔐 Xavfsizlik:
Spam oldini olish uchun rate-limit (1 xabar / 30 soniya).
CSRF va JWT auth himoyasi.
Fayl yuklash maksimal hajmi: 5 MB.
✅ Yakuniy foydalanuvchi tajribasi:

Foydalanuvchi “Qo‘llab-quvvatlash” sahifasiga kiradi, muammosini yozadi, rasm qo‘shadi, yuboradi —
va 10 soniya ichida u xabari Telegram’dagi @adminsupport ga yetkaziladi.

📢 Yangiliklar / Promo sahifasi


foydalanuvchi uchun yangiliklar markazi bo‘ladi.
Bu joyda foydalanuvchi loyihaning rasmiy Telegram kanali, muhokamalar chati, va admin e’lonlari / bonuslarni ko‘radi.
Keling, bu sahifani ham to‘liq tahlil qilamiz 👇
📢 10. Yangiliklar / Promo sahifasi — To‘liq tuzilma
🎯 Maqsad:
Foydalanuvchilarga loyiha bo‘yicha so‘nggi e’lonlar, bonuslar, narx o‘zgarishlari, va rasmiy Telegram manzillarini bir joyda ko‘rsatish.
🧩 UI tuzilishi
🔹 Sahifa nomi:
"Yangiliklar & Promo"
🔹 Yuqori qism (Header):
Sarlavha: 📢 So‘nggi yangiliklar
Tagline: “Loyihamizdagi e’lonlar va bonuslarni bu yerdan kuzating.”
🔹 Asosiy bloklar:
1️⃣ Rasmiy Telegram havolalari
Karta (Card) ko‘rinishida joylashtiriladi:
Bo‘limTavsifTugma📣 Telegram kanalLoyihaning yangiliklari va e’lonlari“👉 Kanalga o‘tish”💬 Muhokamalar chatiFoydalanuvchilar fikr almashadigan chat“💭 Chatga qo‘shilish” 
➡️ Tugmalar t.me/<kanal_nomi> va t.me/<chat_nomi> orqali bevosita ochiladi.
Masalan:
Kanal: https://t.me/project_news
Chat: https://t.me/project_chat
2️⃣ Admin e’lonlari (News Feed)
Har bir e’lon card sifatida ko‘rsatiladi: 🗓️ Sana: 2025-11-02 📌 Sarlavha: "Kunlik narx yangilandi!" 📄 Tavsif: "Bugun trafik narxi 0.0023 $/MB etib belgilandi." 🔗 Batafsil: (link mavjud bo‘lsa) 
Rasmli e’lonlar uchun mini-thumbnail ko‘rinadi.
Pastki burchakda "Yangi" belgisi (NEW 🔥).
3️⃣ Promo-kodlar bo‘limi
Har bir promo-code kartochka: 🎁 PROMO: TRAFIC10 💰 Bonus: +10% balansga ⏰ Amal qilish muddati: 2025-11-15 [ Faollashtirish tugmasi ] 
Tugma bosilganda: POST /promo/activate { "user_id": 104, "code": "TRAFIC10" } Javob: { "status": "success", "message": "Promo-kod muvaffaqiyatli faollashtirildi!" } 
🧠 Backend ma’lumot modeli
Jadval: announcements
Ustun nomiTuriTavsifidintPrimary keytitlevarchar(255)E’lon sarlavhasidescriptiontextE’lon matniimage_urlvarchar(255)Rasm (agar bo‘lsa)linkvarchar(255)Batafsil manzilcreated_atdatetimeYaratilgan vaqt 
Jadval: promo_codes
Ustun nomiTuriTavsifidintPrimary keycodevarchar(64)Promo kodbonus_percentdecimal(5,2)Bonus foiziexpires_atdatetimeAmal qilish muddatiis_activebooleanFaol yoki yo‘q 
🔄 API endpointlar
EndpointMetodTavsif/announcementsGETE’lonlar ro‘yxati/promo/listGETAktiv promo-kodlar/promo/activatePOSTPromo kodni faollashtirish/telegram/linksGETKanal va chat havolalarini olish 
API javob namunasi:
{ "telegram_links": { "channel": "https://t.me/project_news", "chat": "https://t.me/project_chat" }, "announcements": [ { "title": "Kunlik narx yangilandi!", "description": "Bugun trafik narxi 0.0023 $/MB etib belgilandi.", "image_url": "https://cdn.app.com/news/price.png", "created_at": "2025-11-02T08:00:00Z" } ], "promo": [ { "code": "TRAFIC10", "bonus_percent": 10, "expires_at": "2025-11-15", "is_active": true } ] } 
📱 UI dizayn g‘oyasi:
Yuqorida Telegram kanal va chat kartalari.
Pastda scrollable news feed (auto refresh bilan).
Promo-kodlar uchun gradient cardlar (yashil yoki oltin rangda).
“Yangi e’lon” belgisi animatsion 🔥.
Har 30 daqiqada avtomatik yangilanish.
🔔 Qo‘shimcha imkoniyatlar:
“📬 E’lonlarni push notification orqali yuborish” (admin panel orqali).
“📎 Kanalga obuna bo‘lmagan foydalanuvchini eslatish”.
“🎉 Maxsus promo event” — avtomatik bonus kampaniyalari.
Xulosa:
Bu sahifa foydalanuvchining yangiliklardan boxabar bo‘lishini, Telegram kanalga ulanib qolishini va promo bonuslarni ishlatishini ta’minlaydi.
Ya’ni — marketing va kommunikatsiyaning yagona markazi bo‘ladi.

🔐 Xavfsizlik / Profil tahriri sahifasi 


 to‘liq tuzilma
🎯 Maqsad:
Foydalanuvchiga o‘z profilini nazorat qilish, ma’lumotlarini ko‘rish, xavfsizlikni oshirish va sessiyani boshqarish imkonini berish.
🧩 UI tuzilishi
🔹 Sahifa nomi:
“Profil & Xavfsizlik”
🔹 1️⃣ Profil bo‘limi (Personal Info)
ElementTavsif🖼️ Profil rasmiTelegram’dan avtomatik olinadi (photo_url) — foydalanuvchi rasmni yangilay olmaydi, lekin ko‘ra oladi.👤 Ism (first_name)Telegram’dan olingan. (readonly)🆔 Telegram IDAvtomatik aniqlanadi.💬 Username@username shaklida ko‘rsatiladi.🕓 So‘nggi kirish (auth_date)“2025-11-02 12:45” formatida ko‘rsatiladi. 

Ushbu bo‘limda faqat ko‘rish mumkin. Tahrir qilishga ehtiyoj yo‘q, chunki Telegram orqali identifikatsiya avtomatik bo‘ladi.
🔹 2️⃣ Hisob xavfsizligi (Account Security)
FunksiyaTavsif🔒 2FA holati“Faol / Faol emas” ko‘rsatiladi (Settings bilan bog‘lanadi)🔑 JWT TokenAgar foydalanuvchi API ishlatsa, shu yerda token ko‘rsatiladi (faqat ko‘rish)🔄 Tokenni yangilash (Renew Token)“Yangilash” tugmasi orqali serverdan yangi JWT olish🚫 Logout from all devicesBarcha faol sessiyalarni tugatadi 
🔹 3️⃣ Chiqish (Logout)
Tugma: “🚪 Hisobdan chiqish”
Bosilganda: 
Lokal ma’lumotlar (session, jwt_token) tozalanadi
Backendga POST /user/logout so‘rovi yuboriladi
Auth sahifasiga qayta yo‘naltiriladi
🧠 Backend ma’lumot modeli
Jadval: users (ilgari mavjud)
faqat shu ustunlardan foydalaniladi:
UstunTavsiftelegram_idUnikal Telegram user IDusernameTelegram foydalanuvchi nomifirst_nameFoydalanuvchi ismiphoto_urlTelegram rasmiauth_dateOxirgi login vaqtijwt_tokenFaol tokentwo_factor_enabled2FA holatilast_login_ipOxirgi kirish IPlast_login_deviceQurilma ma’lumotlari 
🔄 API endpointlar
EndpointMetodTavsif/user/profileGETFoydalanuvchi profil ma’lumotlarini olish/user/profile/updatePATCHProfilni yangilash (agar ruxsat berilsa)/user/token/renewPOSTYangi JWT token olish/user/logoutPOSTHisobdan chiqish/user/logout_allPOSTBarcha sessiyalarni tugatish 
🔸 API javob namunasi:
{ "telegram_id": 599382114, "username": "bunyoddev", "first_name": "Bunyod", "photo_url": "https://t.me/i/userpic/320/bunyod.jpg", "auth_date": "2025-11-02T12:45:00Z", "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "two_factor_enabled": true, "last_login_ip": "185.91.77.3", "last_login_device": "Android Galaxy S8+" } 
📱 UI dizayn g‘oyasi:
Yuqorida profil rasmi + ism + username joylashadi.
Pastda Security settings cardlari (Token, 2FA, Logout).
Tugmalar: 
🔄 Tokenni yangilash
🚪 Logout
Foydalanuvchiga “✅ Hisobdan chiqdingiz” yoki “♻️ Token yangilandi” bildirishnomalari chiqariladi.
🔐 Xavfsizlik choralari:
Logout qilganda barcha active_sessions jadvalidan foydalanuvchi tokenlari o‘chiriladi.
JWT token muddati 7 kun.
2FA yoqilgan foydalanuvchi uchun auth_date 3 martadan ko‘p uzaytirilmaydi (avtomatik logout trigger).
💡 Qo‘shimcha imkoniyatlar:
📍 Oxirgi 5 kirish logi (“Toshkent, Android, 2025-10-31 21:00”)
🕵️ Token monitoring (agar token boshqa IP’dan ishlatilsa — bildirishnoma)
🔔 Foydalanuvchiga email / Telegram orqali xavfsizlik ogohlantirishlar
i
Natija:
“Xavfsizlik / Profil tahriri” sahifasi foydalanuvchiga o‘z Telegram profilini ko‘rish, xavfsizlikni boshqarish, tokenni yangilash va logout qilish imkonini beradi.
Ya’ni — bu tizimdagi identifikatsiya va himoya markazi hisoblanadi

adminlar uchun alohida maxsus panel


🧠 ADMIN PANEL – To‘liq Tuzilma
Ushbu sahifa faqat .env fayldagi ma’lumotlar orqali admin sifatida aniqlangan foydalanuvchilarga ochiladi.
Kirishda tizim Telegram orqali foydalanuvchini tanib oladi (telegram_id, username, phone).
📄 1. Asosiy boshqaruv (Admin Dashboard)
Ma’lumotlar paneli (summary):
🧑 Foydalanuvchilar soni
💰 Umumiy balans (barcha foydalanuvchilar balanslari yig‘indisi)
📡 Faol trafik sessiyalari soni
⚙️ Faol API-lar soni
💸 Bugungi to‘lovlar (withdraw summasi)
📊 Bugungi daromad (trafic sotuvlaridan)
Grafiklar (charts):
Kunlik yangi foydalanuvchilar
Trafik iste’moli (kunlik MB)
Daromad o‘sish dinamikasi
🧍‍♂️ 2. Foydalanuvchilar bo‘limi (Users Management)
Funksiyalar:
👁 Foydalanuvchi ro‘yxatini ko‘rish
🔍 Qidiruv (telegram_id, username, ism bo‘yicha)
🧾 Har bir foydalanuvchining tafsiloti: 
Balans
Trafik ishlatish statistikasi
API-lar soni
So‘nggi sessiya va auth_date
⚙️ Amal bajarish tugmalari: 
“Ban user”
“Reset token”
“Add balance”
“View session history”
🔐 3. API boshqaruvi (API Management)
📘 Yangi API yaratish
Buyer (foydalanuvchi) tanlash
Trafik limiti (MB yoki GB da)
Amal qilish muddati (kun)
API nomi (ixtiyoriy)
API turi: 
Traffic API – trafik olish uchun
Rotation API – IP yangilash uchun
Avtomatik API key generatsiyasi (masalan: api_2H7bA8x91T)
⚙️ Boshqaruv funksiyalari
API-lar ro‘yxati: 
Foydalanuvchi nomi
Yaralgan sana
Limit (foydalangan / umumiy)
Tugash muddati
Holat (faol / tugagan)
Amal bajarish: 
🟢 Faollashtirish / 🔴 To‘xtatish
♻️ Limitni yangilash
⏰ Muddati uzaytirish
🗑 O‘chirish
💰 4. To‘lovlar (Withdraws & Balances)
Ma’lumotlar:
So‘nggi yechilgan summalar
Foydalanuvchi nomi
USDT manzili (BEP20)
Summasi
Sana
Holati (✅ to‘langan / ⏳ kutilmoqda)
Funksiyalar:
✅ “To‘lovni tasdiqlash” (agar avtomatik bo‘lmasa)
🔄 “Qayta yuborish”
📜 “To‘lov tarixi”
📡 5. Traffic Pool boshqaruvi
Trafik resurslari haqida ma’lumotlar:
Joriy ishlatilayotgan IP-lar soni
Bo‘sh IP slotlari
Oxirgi yangilanish vaqti
Trafik serverlar ro‘yxati (hostname, latency, bandwidth)
Funksiyalar:
➕ Yangi pool ulash
🔄 IP rotatsiyani tekshirish
🧩 Trafik o‘lchovlarni (MB/s, ping) kuzatish
📈 6. Analitika va Hisobotlar (Reports)
Grafiklar:
Kunlik foydalanuvchilar soni
Trafik ishlatilishi (MB/kun)
Daromad grafigi
To‘lov statistikasi
Export funksiyasi:
📤 Excel / CSV / PDF ga eksport qilish
🗞 7. Yangiliklar va Promo boshqaruvi
Admin uchun:
📝 Yangi yangilik qo‘shish 
Sarlavha
Tavsif
Havola (masalan: Telegram kanali yoki promo sahifasi)
Rasm
📢 Push notification orqali yuborish
🧾 Yaratilgan yangiliklar ro‘yxati
👥 8. Adminlar boshqaruvi
.env fayldan tashqari admin qo‘shish imkoniyati:
Telegram ID
Username
Telefon raqami
Ruxsat darajasi: SuperAdmin / Moderator
⚙️ 9. Tizim sozlamalari (System Settings)
🧩 API konfiguratsiya (universal payment API tokenlari)
💾 Zaxira nusxa olish
🕒 Cron ishlarini belgilash (statistika yangilanishi, to‘lov tekshiruvi)
📡 Server status (trafik, RAM, disk holati)
🔐 JWT token muddati, xavfsizlik parametrlari
🔍 10. Monitoring / Logs
⚙️ Tizim loglari (auth, API ishlatish, to‘lovlar)
🚦 Xatoliklar (error monitoring)
⏱ Real-vaqt monitoring (WebSocket orqali)
🧩 Yakuniy Ko‘rinish (Admin Panel Menyusi)
Bo‘limTavsif📊 DashboardUmumiy statistikalar va holat👥 UsersFoydalanuvchilar ro‘yxati va tafsilotlari🔑 API ManagerTrafik API larini boshqarish💰 WithdrawsTo‘lovlar nazorati📡 Traffic PoolTrafik manbalarini boshqarish📈 ReportsKunlik/oylik hisobotlar🗞 News & PromoYangiliklar va bonuslar👤 AdminsAdminlarni boshqarish⚙️ SettingsTizim konfiguratsiyasi🧾 Logs & MonitoringFaoliyat va xatolik kuzatuvi

