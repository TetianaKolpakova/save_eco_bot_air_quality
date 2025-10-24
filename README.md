# SaveEcoBot sensor for Home Assistant

[SaveEcoBot](https://www.saveecobot.com/en) — це український екологічний проєкт, який надає дані про якість повітря, температуру, вологість і тиск з тисяч станцій по всій країні.

Ця інтеграція додає підтримку SaveEcoBot у [Home Assistant](https://www.home-assistant.io/), дозволяючи створювати сенсори на основі даних конкретних станцій.

---

## 🔧 Встановлення

### Варіант 1. Через HACS (рекомендовано)

1. Відкрийте **HACS → Integrations → три крапки (⋮) → Custom repositories**.  

2. У полі **Repository** вставте:
https://github.com/TetianaKolpakova/hass_save_eco_bot_sensor . У полі **Category** виберіть **Integration** і натисніть **Add**.

3. Після цього інтеграція з’явиться в HACS. Знайдіть **SaveEcoBot UI** і натисніть **Install**.

4. Перезапустіть Home Assistant.

5. Після рестарту перейдіть у **Settings → Devices & Services → Add Integration** і додайте **SaveEcoBot UI**.

### Варіант 2. Ручна установка

1. Скопіюйте вміст цього репозиторію в:
<config>/custom_components/save_eco_bot

2. Перезапустіть Home Assistant.

---

## ⚙️ Налаштування через UI

1. Відкрийте **Settings → Devices & Services → Integrations → Add Integration**.
2. Знайдіть **SaveEcoBot**.
3. Далі відкриється майстер налаштування:
- **Крок 1:** Оберіть місто зі списку.
  > Щоб знайти потрібну станцію, відкрийте [мапу SaveEcoBot](https://www.saveecobot.com/maps), клацніть по точці на мапі та подивіться на кінець URL — там буде `device_xxxxx`.
- **Крок 2:** Оберіть одну або кілька станцій.
  - Можна натиснути **Select all**, щоб додати всі станції міста.
  - За замовчуванням жодна станція не вибрана.

4. Після збереження інтеграція створить окремі сенсори для кожного параметра:
- `PM2.5`, `PM10`
- `Temperature`, `Humidity`, `Pressure`
- `Air Quality Index`

---

## 📈 Результат

Після встановлення з’являться сенсори типу:

- `sensor.pm25_andriivka_main_street`
- `sensor.temperature_andriivka_main_street`
- `sensor.aqi_andriivka_main_street`

Дані оновлюються автоматично через офіційний API SaveEcoBot.

---

## 🧩 Можливості

- Підтримка Config Flow (UI-налаштування без YAML).
- Dropdown-вибір міст та станцій із підтримкою “Select all”.
- Підказка з посиланням на мапу SaveEcoBot.
- Автоматичне оновлення даних з API кожні 30 секунд.
- Повна сумісність з HACS.

---

## 🗺️ Підказка

Визначити ID станції можна за посиланням:
👉 [https://www.saveecobot.com/maps](https://www.saveecobot.com/maps)

Натисніть на точку на мапі — в URL побачите `device_xxxxx`. Числа після 'device_' і є ідентифікатор станції.

---

## 🤝 Автори

- **Оригінальна версія:** [@kuzin2006](https://github.com/kuzin2006)
- **Оновлена підтримка Config Flow, UI-інтерфейс і HACS:** [@TetianaKolpakova](https://github.com/TetianaKolpakova)

---

## 📄 Ліцензія

Цей проєкт поширюється за ліцензією MIT.