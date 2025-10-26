# SaveEcoBot sensor for Home Assistant

---

## 🇺🇸 English version

[SaveEcoBot](https://www.saveecobot.com/en) is a Ukrainian environmental project that provides air quality, temperature, humidity, and pressure data from thousands of monitoring stations across the country.

This integration adds **SaveEcoBot** support to [Home Assistant](https://www.home-assistant.io/), allowing you to create sensors based on data from specific stations.

---

### 🔧 Installation

#### Option 1. Via HACS (recommended)

1. Open **HACS → Integrations → three dots (⋮) → Custom repositories**.  
2. In the **Repository** field, paste:  
   `https://github.com/TetianaKolpakova/hass_save_eco_bot_sensor`  
   In the **Category** field, choose **Integration** and click **Add**.  
3. After that, the integration will appear in HACS. Find **SaveEcoBot UI** and click **Install**.  
4. Restart Home Assistant.  
5. Go to **Settings → Devices & Services → Add Integration** and add **SaveEcoBot UI**.

#### Option 2. Manual installation

1. Copy the content of this repository into:  
   `<config>/custom_components/save_eco_bot`
2. Restart Home Assistant.

---

### ⚙️ Configuration (via UI)

1. Go to **Settings → Devices & Services → Integrations → Add Integration**.  
2. Search for **SaveEcoBot**.  
3. Follow the setup wizard:  
   - **Step 1:** Choose a city from the dropdown list.  
     > To find your station, open the [SaveEcoBot map](https://www.saveecobot.com/maps), click a point, and look at the end of the URL — it will contain `device_xxxxx`.
   - **Step 2:** Choose one or more stations.  
     - You can use **Select all** to add all city stations.  
     - Note: some stations might be inactive but still appear in the list.  
4. After saving, the integration will create sensors for each parameter:  
   - `PM2.5`, `PM10`  
   - `Temperature`, `Humidity`, `Pressure`  
   - `Air Quality Index`

---

### 📈 Example result

- `sensor.pm25_andriivka_main_street`  
- `sensor.temperature_andriivka_main_street`  
- `sensor.aqi_andriivka_main_street`

Data updates automatically through the official SaveEcoBot API.

---

### 🧩 Features

- Config Flow (UI setup, no YAML needed)  
- Dropdown city/station selection with **Select all**  
- Integrated link to the SaveEcoBot map  
- Auto-updates every 30 seconds  
- Full HACS compatibility

---

### 🤝 Authors

- **Original version:** [@kuzin2006](https://github.com/kuzin2006)  
- **Updated with Config Flow, UI, and HACS support:** [@TetianaKolpakova](https://github.com/TetianaKolpakova)

---

### 📄 License

Distributed under the MIT License.

---

## 🇺🇦 Українська версія

[SaveEcoBot](https://www.saveecobot.com/uk) — український екологічний проєкт, який надає дані про якість повітря, температуру, вологість і тиск з тисяч станцій по всій країні.

Ця інтеграція додає підтримку SaveEcoBot у [Home Assistant](https://www.home-assistant.io/), дозволяючи створювати сенсори на основі даних конкретних станцій.

---

### 🔧 Встановлення

#### Варіант 1. Через HACS (рекомендовано)

1. Відкрийте **HACS → Integrations → три крапки (⋮) → Custom repositories**.  
2. У полі **Repository** вставте:  
   `https://github.com/TetianaKolpakova/hass_save_eco_bot_sensor`  
   У полі **Category** виберіть **Integration** і натисніть **Add**.  
3. Після цього інтеграція з’явиться в HACS. Знайдіть **SaveEcoBot UI** і натисніть **Install**.  
4. Перезапустіть Home Assistant.  
5. Після рестарту перейдіть у **Settings → Devices & Services → Add Integration** і додайте **SaveEcoBot UI**.

#### Варіант 2. Ручна установка

1. Скопіюйте вміст цього репозиторію в:  
   `<config>/custom_components/save_eco_bot`  
2. Перезапустіть Home Assistant.

---

### ⚙️ Налаштування через UI

1. Відкрийте **Settings → Devices & Services → Integrations → Add Integration**.  
2. Знайдіть **SaveEcoBot**.  
3. У майстрі налаштування:  
   - **Крок 1:** Оберіть місто зі списку.  
     > Щоб знайти потрібну станцію, відкрийте [мапу SaveEcoBot](https://www.saveecobot.com/maps) і подивіться кінець URL — там буде `device_xxxxx`.  
   - **Крок 2:** Оберіть одну або кілька станцій.  
     - Можна натиснути **Select all**, щоб додати всі станції міста.  
     - Деякі станції можуть бути неактивні, але все одно відображаються у списку.  
4. Після збереження інтеграція створить сенсори:  
   - `PM2.5`, `PM10`  
   - `Temperature`, `Humidity`, `Pressure`  
   - `Air Quality Index`

---

### 📈 Результат

- `sensor.pm25_andriivka_main_street`  
- `sensor.temperature_andriivka_main_street`  
- `sensor.aqi_andriivka_main_street`

Дані оновлюються автоматично через офіційний API SaveEcoBot.

---

### 🧩 Можливості

- Підтримка Config Flow (налаштування через UI).  
- Dropdown-вибір міст і станцій із кнопкою **Select all**.  
- Підказка з посиланням на мапу SaveEcoBot.  
- Автоматичне оновлення кожні 30 секунд.  
- Повна сумісність з HACS.

---

### 🤝 Автори

- **Оригінальна версія:** [@kuzin2006](https://github.com/kuzin2006)  
- **Оновлена підтримка Config Flow, UI-інтерфейс і HACS:** [@TetianaKolpakova](https://github.com/TetianaKolpakova)

---

### 📄 Ліцензія

Проєкт поширюється за ліцензією MIT.
