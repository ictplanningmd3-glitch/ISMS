# تقسیم‌بندی حوزه‌های استاندارد و Annex A — نسخهٔ ۱۳

دو نگاشت ده‌گانه دقیقاً بر اساس تقسیم‌بندی کامل و صریح ارسالی کاربر تهیه شده‌اند: نام انگلیسی، ترتیب حوزه‌ها و عضویت هر بند و کنترل از همان فهرست گرفته می‌شوند. نام فارسی و برچسب کوتاه هر حوزه نیز در منبع واحد نگهداری می‌شود.

این حوزه‌ها دسته‌بندی مفهومی سامانه‌اند؛ شمارهٔ رسمی بندها و چهار گروه رسمی کنترل‌های Annex A از A.5 تا A.8 حفظ می‌شوند. هر یک از ۳۰ بند الزامات و هر یک از ۹۳ کنترل پیوست الف دقیقاً یک‌بار در نگاشت مربوط قرار گرفته‌اند. هیچ بند یا کنترل بین دو حوزهٔ یک نگاشت تکرار نمی‌شود.

منبع واحد: `src/taxonomy-v13.json`. رادارها، فیلترهای مفهومی، نمودارها، فرم پروژه‌های اصلاحی و عنوان حوزهٔ یافته‌های ممیزی از همین دسته‌بندی استفاده می‌کنند. فیلتر «بند مرجع استاندارد» فقط شماره‌های رسمی را برای ارجاع نگه می‌دارد.

## فایل‌های Excel و CSV

در پوشهٔ `assets` بسته:

- `Annex_A_Domains.xlsx` و `Annex_A_Domains.csv`: نگاشت ۹۳ کنترل به ده حوزهٔ پیوست الف.
- `Clause_Domains.xlsx` و `Clause_Domains.csv`: نگاشت ۳۰ بند به ده حوزهٔ الزامات.

هر Excel سه برگه دارد: Item mapping برای نگاشت کامل، Domain summary برای تعداد اقلام هر حوزه و Basis برای مبنای تهیهٔ فایل.

## ده حوزهٔ کنترل‌های Annex A

| ردیف | حوزه | Domain | تعداد کنترل |
|---:|---|---|---:|
| 1 | حاکمیت و مدیریت امنیت اطلاعات | Governance & Information Security Management | 15 |
| 2 | مدیریت دارایی‌ها و حفاظت از اطلاعات | Asset & Information Protection | 6 |
| 3 | هویت، احراز هویت و کنترل دسترسی | Identity & Access Management | 9 |
| 4 | امنیت منابع انسانی و آگاهی‌رسانی | Human Resources & Security Awareness | 8 |
| 5 | امنیت فیزیکی و محیطی | Physical & Environmental Security | 14 |
| 6 | امنیت زیرساخت و شبکه | Infrastructure & Network Security | 5 |
| 7 | عملیات، پایش و مدیریت آسیب‌پذیری | Security Operations & Monitoring | 8 |
| 8 | حفاظت از داده‌ها و تاب‌آوری اطلاعات | Data Protection & Resilience | 6 |
| 9 | توسعه امن و مدیریت تغییر | Secure Development & Change Management | 10 |
| 10 | طرف‌های ثالث، مدیریت رخداد و تداوم | Third Party, Incident & Continuity | 12 |
| | مجموع | Total | 93 |

## فهرست کامل کنترل‌ها

### حاکمیت و مدیریت امنیت اطلاعات — Governance & Information Security Management

`A.5.1`, `A.5.2`, `A.5.3`, `A.5.4`, `A.5.5`, `A.5.6`, `A.5.7`, `A.5.8`, `A.5.31`, `A.5.32`, `A.5.33`, `A.5.34`, `A.5.35`, `A.5.36`, `A.5.37`

### مدیریت دارایی‌ها و حفاظت از اطلاعات — Asset & Information Protection

`A.5.9`, `A.5.10`, `A.5.11`, `A.5.12`, `A.5.13`, `A.5.14`

### هویت، احراز هویت و کنترل دسترسی — Identity & Access Management

`A.5.15`, `A.5.16`, `A.5.17`, `A.5.18`, `A.8.2`, `A.8.3`, `A.8.4`, `A.8.5`, `A.8.18`

### امنیت منابع انسانی و آگاهی‌رسانی — Human Resources & Security Awareness

`A.6.1`, `A.6.2`, `A.6.3`, `A.6.4`, `A.6.5`, `A.6.6`, `A.6.7`, `A.6.8`

### امنیت فیزیکی و محیطی — Physical & Environmental Security

`A.7.1`, `A.7.2`, `A.7.3`, `A.7.4`, `A.7.5`, `A.7.6`, `A.7.7`, `A.7.8`, `A.7.9`, `A.7.10`, `A.7.11`, `A.7.12`, `A.7.13`, `A.7.14`

### امنیت زیرساخت و شبکه — Infrastructure & Network Security

`A.8.1`, `A.8.20`, `A.8.21`, `A.8.22`, `A.8.23`

### عملیات، پایش و مدیریت آسیب‌پذیری — Security Operations & Monitoring

`A.8.6`, `A.8.7`, `A.8.8`, `A.8.9`, `A.8.15`, `A.8.16`, `A.8.17`, `A.8.19`

### حفاظت از داده‌ها و تاب‌آوری اطلاعات — Data Protection & Resilience

`A.8.10`, `A.8.11`, `A.8.12`, `A.8.13`, `A.8.14`, `A.8.24`

### توسعه امن و مدیریت تغییر — Secure Development & Change Management

`A.8.25`, `A.8.26`, `A.8.27`, `A.8.28`, `A.8.29`, `A.8.30`, `A.8.31`, `A.8.32`, `A.8.33`, `A.8.34`

### طرف‌های ثالث، مدیریت رخداد و تداوم — Third Party, Incident & Continuity

`A.5.19`, `A.5.20`, `A.5.21`, `A.5.22`, `A.5.23`, `A.5.24`, `A.5.25`, `A.5.26`, `A.5.27`, `A.5.28`, `A.5.29`, `A.5.30`

## ده حوزهٔ الزامات استاندارد

| ردیف | حوزه | English | تعداد بند |
|---:|---|---|---:|
| 1 | شناخت سازمان و شرایط آن | Organizational Context | 1 |
| 2 | ذی‌نفعان و دامنه سیستم مدیریت امنیت اطلاعات | Interested Parties & ISMS Scope | 3 |
| 3 | رهبری و حاکمیت | Leadership & Governance | 3 |
| 4 | مدیریت ریسک و فرصت‌ها | Risk & Opportunity Management | 1 |
| 5 | مدیریت ریسک امنیت اطلاعات | Information Security Risk Management | 2 |
| 6 | اهداف و طرح‌ریزی تغییرات | Objectives & Change Planning | 2 |
| 7 | منابع، شایستگی و آگاهی | Resources, Competence & Awareness | 3 |
| 8 | ارتباطات و اطلاعات مدون | Communication & Documented Information | 4 |
| 9 | کنترل عملیات | Operational Control | 3 |
| 10 | ارزیابی عملکرد و بهبود | Performance Evaluation & Improvement | 8 |
| | مجموع | Total | 30 |

## فهرست کامل بندها

### شناخت سازمان و شرایط آن — Organizational Context

`4.1`

### ذی‌نفعان و دامنه سیستم مدیریت امنیت اطلاعات — Interested Parties & ISMS Scope

`4.2`, `4.3`, `4.4`

### رهبری و حاکمیت — Leadership & Governance

`5.1`, `5.2`, `5.3`

### مدیریت ریسک و فرصت‌ها — Risk & Opportunity Management

`6.1.1`

### مدیریت ریسک امنیت اطلاعات — Information Security Risk Management

`6.1.2`, `6.1.3`

### اهداف و طرح‌ریزی تغییرات — Objectives & Change Planning

`6.2`, `6.3`

### منابع، شایستگی و آگاهی — Resources, Competence & Awareness

`7.1`, `7.2`, `7.3`

### ارتباطات و اطلاعات مدون — Communication & Documented Information

`7.4`, `7.5.1`, `7.5.2`, `7.5.3`

### کنترل عملیات — Operational Control

`8.1`, `8.2`, `8.3`

### ارزیابی عملکرد و بهبود — Performance Evaluation & Improvement

`9.1`, `9.2.1`, `9.2.2`, `9.3.1`, `9.3.2`, `9.3.3`, `10.1`, `10.2`
