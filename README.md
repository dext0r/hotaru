# Мой "умный" дом
В этом репозитории собраны конфиги моего умного дома, а так же список всех устройства и DIYых костылей.

- [Об объекте и УД](#об-объекте-и-уд)
- [Платформа](#платформа)
- [Освещение](#освещение)
  - [Выключатели без нейтрали](#выключатели-без-нейтрали)
  - [Диммеры AC](#диммеры-ac)
  - [Ленты](#ленты)
  - [Остальное](#остальное)
- [Датчики](#датчики)
- [Розетки](#розетки)
- [Климат](#климат)
- [Замки](#замки)
- [Кнопки](#кнопки)
- [Шторы](#шторы)
- [Разное](#разное)
- [Датчики DIY](#датчики-diy)
- [Странный DIY](#странный-diy)
- [Новогодний DLC](#новогодний-dlc)
- [О разном](#о-разном)
  - [Мнение о TTLock Ultra](#мнение-о-ttlock-ultra)
  - [Мнение о Danalock](#мнение-о-danalock)
  - [Рулонные шторы](#рулонные-шторы)
- [Статистика по устройствам](#статистика-по-устройствам)

## Об объекте и УД
Квартира 83 м3, три комнаты (гостиная, спальня, мастерская), совмещённый с/у, отдельная кухня, два балкона на север и юг, огороженный тамбур ("крыльцо"). Внутри живёт два взрослых человека и два кота. Объект покупался на вторичном рынке, поэтому не всё можно было сделать так, как хочется. Приходится работать с тем что есть.

Основная концепция моего УД - "всё должно работать без УД". Другими словами, все важные компоненты управляются с физических выключателей или пультов (начиная от света в ванной и кончая электрическими шторами).

Весь IOT вынесен в два изолированных VLAN без доступа и локальной сети, в одном VLAN есть постоянный доступ в интернет. Для ретрансляции мультикаста между всеми VLAN запущен [mdns-reflector](https://github.com/vfreex/mdns-reflector).

## Платформа
* Mac Mini (Late 2012)
* Debian 12 c Proxmox
* ИБП Ippon Back Basic 650S Euro
* Основной роутер: Mikrotik hAP ax3
* Zigbee: Sonoff Zigbee 3.0 USB Dongle Plus
* HA OS в виртуальной машине
* Аддоны HA: supervisor, chrony, let's encrypt, mosquitto broker, nginx home assistant ssl proxy, timescale db, ttlock, zigbee2mqtt, advanced ssh & web terminal
* Интеграции HA: Glances (сбор метрик с физического хоста), Mikrotik (трекинг присутствия дома по регистрации на WiFi), Nut (состояние ИБП), Yandex Smart Home (облачное подключение) и другие

## Освещение
### Выключатели без нейтрали
* 2x **Xiaomi WS-EUK02**: хороший выключатель, практически всегда работает без "конденсатора", одна из кнопок у меня отвязана от реле.
* 4x **[eWeLink ZB-SW01/SW02](https://aliexpress.ru/item/4001331194955.html)**: с этих выключателей начался мой умный дом :) Минусы: спамят в эфир, отвратительны тактильно, яркие светодиоды (заглушил термоусадкой), часто нужен конденсатор (идёт в комплекте).

### Диммеры AC
* 1x **Shelly Dimmer 2** (esphome) + лампы Navigator NLL-GX53-10-230-4K-DIMM: лучший диммер на рынке! Поддерживает transition (в отличии от туи) + дополнительное управление физическим выключателем.

### Ленты
* 3x Диммер **[H801](https://aliexpress.ru/item/33025692161.html)** (esphome): лучший пятиканальный диммер для диодных лент. Один диммер без проблем держит 170 ватт диодного света (по 85 ватт на канал, ленты Arlight RT-A168-10mm 24V Day4000 019094). Физические выключатели подключены на TX/RX пины.
* 2x Диммер **MagicHome** (esphome) - маломощный диммер, но то, что продаётся сейчас, уже не на esp :(
* Пять кусков разной длины [адресной RGBW ленты](https://aliexpress.ru/item/32476317187.html) SK6812 (60 вт/м): подключены к четёрым разным ESP на esphome. Используются как "путевая подсветка" для хождения в темноте (у меня блекаут шторы :)
* RGB лента под **Sonoff L1** (esphome): подсветка под кроватью.

### Остальное
* Светильник Луна 20 см. с алихи: управляется через IR от Hyper IoT v1 и [релейный модуль](https://aliexpress.ru/item/1624699191.html), который был под рукой ([безумная конфигурация](esphome/bedroom-moon-light.yaml))
* 6x Лампа **Yeelight YLDP004-A**: декоративная подсветка.
* 1x Реле **Sonoff Basic R2** (esphome): диодная лента над ванной (IP67, всё по-красоте)
* 1x Реле **Sonoff Mini** (esphome): простой светильник из мерлена над зеркалом в ванне.

## Датчики
* 6x Температура/влажность **[Xiaomi LYWSD03MMC](https://www.wildberries.ru/catalog/35891286/detail.aspx)** перешитые в [PVVX/ATC_MiThermometer](https://github.com/pvvx/ATC_MiThermometer): супер датчики за 300, работают по BT, все откалиброваны и защищены PIN кодом, принимаются на ESP32 ([пример](esphome/bedroom-ubox.yaml))
* 3x Температура/влажность **Xiaomi WXKG01LM**: использовал до переход на BT датчики, теперь валяются в холодильнике и морозильнике.
* 2x Освещенность **Xiaomi GZCGQ01LM**: лежат на балконах в тени.
* 5x Открытие **Xiaomi MCCGQ01LM**: двери в разные помещения, посудомойка и стиралка.
* 1x Открытие **Life Control MCLH-04**: отвратительные гигантские датчики с дорогой батарейкой, не рекомендую. Плохо срабатывает закрытие при низком уровне сигнала. Стоит на морозилке. Два лежат в столе :)
* 6x Открытие **Perenio PECWS01**: дешевая альтернатива Xiaomi, работают хорошо, большой диапазон магнита. Надпись Perenio стирается ацетоном. Стоят на окнах и балконных дверях (не дают шторам работать при открытых окнах), и ещё на дверях в холодильник и кладовку.
* 10x Движение **Xiaomi RTCGQ01LM/RTCGQ11LM**: разбросаны по всему дому, несколько с [перемычкой](https://community.smartthings.com/t/making-xiaomi-motion-sensor-a-super-motion-sensor/139806) для ускорения срабатывания.
* 1x Присутствие **Xiaomi RTCZCGQ11LM**: безупречно определяет присутствие по всей ванной комнате, жаль стоит дорого :(
* 4x Протечка **Xiaomi SJCGQ11LM**
* 2x Открытие **SONOFF SNZB-04**: концевики для ригелей во входной двери ([фото 1](images/lock-1.jpg), [фото 2](images/lock-2.jpg))
* 3x Дым **GS SSHM-I1**
* 1x PM 2.5 **IKEA E2014 Vindriktning**: c ESP32 и SenseAir S8 внутри. Пока для ловли дыма когда сосед курит и его мерзкий дым затягивает в приточку. Датчик дым не видит :( Поэтому использую как корпус для S8.

## Розетки
* 2x Zigbee **[Aubess 16A](https://aliexpress.ru/item/1005003656847898.html)**: после обновления через OTA начинают работать отлично, потребление прилетает практически мгновенно. Стоят на посудомойке и зарядке самоката (лол, я параноик).
* 2x WiFi **[Tuya CBE 16A](https://aliexpress.ru/item/1005002378544572.html)** с **перепаенным модулем** [ESP-02S](https://aliexpress.ru/item/1005003949251076.html): стиральная машина и водонагреватель ([конфиг](esphome/generic/cbe_socket.yaml))

## Климат
* 2x Инверторный **Midea MSAG1-09N8C2**: управляется по USB через esphome платой [ESP8266 ESP-12F](https://aliexpress.ru/item/32815395082.html) (там есть конвертер уровней) + диодик для управления подсветкой/follow me
* 3x Бризер **Tion 4S**: управляется по BT через ESP32 (https://github.com/dentra/esphome-tion)
* Тупой обогреватель на **Sonoff Basic R3** (esphome)
* Тупой вентилятор на **Sonoff Basic** (esphome) - временно решение для нагнетания холодного воздуха в гостиную
* 2x Увлажнитель **Smartmi Zhimi Air Humidifier CJXJSQ02ZM** (интеграция Xiaomi Miot Auto)
* Увлажнитель **Xiaomi Mijia Pure Smart Humidifier Pro CJSJSQ02LX** (интеграция Xiaomi Miot Auto)
* Увлажнитель **Tion Iris**, он же **AIRMX A3S**: куплен с безумной скидкой на Мегамаркете. По такому случаю даже пришлось написать [собственную интеграцию](https://github.com/dext0r/airmx) :)

## Замки
* **Danalock 3 Zigbee + BT**: в общий тамбур, соседи ходят по физически ключам.
* **[TTLock Ultra Black](http://ttlock.com.ru/shop/ttlock-motorlock-ultra/)**: в квартиру, открываем только отпечатками. Интегрируется через аддон [ttlock-hass-integration](https://github.com/kind3r/hass-addons/tree/master/ttlock-hass-integration) и шлюз на ESP32 ([прошивка](https://github.com/kind3r/esp32-ble-gateway)).

Дополнительно в дверях стоят концевики (смотри раздел Датчики и Мнения о замках).

## Кнопки
* 4x **Xiaomi WXKG01LM**: мои любимые кнопочки, офигенные тактильно (не нужно целится как во второй версии), большая вариативность комбинаций (single-double-triple-hold-many).
* 2x **IKEA E1743**: норм, удобно, что есть "вверх-вниз", но бесят иногда отваливаться.

## Шторы
* 2x Рулонные Zigbee **[Zemismart ZM25TQ](https://aliexpress.ru/item/4000336263991.html)** c пультом: подробнее о [трубе и полотне](#рулонные-шторы).
* **Xiaomi ZNCLDJ11LM**: брал в комплекте с карнизом на aqara.ru. Стоит дорого, но мне надо было срочно.
* Tuya с мотором и карнизом (ссылка протухла): заказывал Zigbee, прислал Wifi, пришлось перепаять на ESP/esphome.

## Мультимедиа
* 1x **Яндекс Станция 2**
* 1x **Яндекс Станция Миди**
* 2x **Яндекс Станция Мини**
* 1x **Яндекс Хаб**
* Телевизор **Hisense H50B7100** (управляется по MQTT)
* Apple TV

## Разное
* 4x Приводы на краны Zigbee **[Tuya ZN231392](https://aliexpress.ru/item/1005003766950419.html)**
* **Nelma5** управлялка домофоном на ESP32 от SCratORS (https://github.com/SCratORS/SmartIntercom): [конфиг](esphome/nelma5.yaml) полностью свой.
* 3x **[PZEM-004](https://aliexpress.ru/item/33043137964.html)** для мониторинга энергопотребления + [аналоговые клещи](https://aliexpress.ru/item/32708887594.html): подключено к управлялке домфоном :) Никогда не используйте аналоговые клещи, только PZEM! (гуглить о power factor)

## Датчики DIY
* 3x CO2 **[SenseAir S8](https://aliexpress.ru/item/32863793412.html)**
* 2x Присутствие **[LD2410C](https://aliexpress.ru/item/1005004351593073.html)**. Собраны в совместным корпусах с S8 ([фото](images/ubox.jpg)), подключение по UART.
* 2x Потребление воды на осмосе (Гейзер Престиж): [крутилка](https://aliexpress.ru/item/1005002080608743.html) + esphome ([фото](images/water-filter.jpg))

## Странный DIY
* Датчик присутствия в кровати: две [ленты](https://aliexpress.ru/item/1005001572817402.html) + модуль [ADS1115](https://aliexpress.ru/item/32817162654.html) + ESP. Гайд: https://dannytsang.co.uk/bed-sensor-with-home-assistant/
* Чайник Redmond **SkyKettle G240S** с контролем уровня воды на весах HX711: esphome + патченный компонент [ESPHome-Ready4Sky](https://github.com/KomX/ESPHome-Ready4Sky). Подробнее о реализации - https://t.me/yandex_smart_home/48400 (для владельцев 3D принтеров - https://github.com/malinovsku/device-esphome/tree/master/kyxna-kettle)

## Новогодний DLC
* Несколько гирлянд с перемычками, чтобы не мигали эпилиптично
* Несколько USBшных гирлянд (жена купила задешево)
* 1x WiFi Tuya диммер[^1] (через Local Tuya)
* 2x Zigbee Tuyz диммер[^1]
* 1x Розетка **Lellki WK34-EU** (всё равно валяется без дела)
* 3х Реле **Sonoff Mini/Basic R3**

[^1] Эти диммеры только для такого применения и подходят. У них не контролируется время разгорания/потухания (transition)

## О разном
### Мнение о TTLock Ultra
Минусы:

1. Не передаёт текущее состояние с вероятностью 100%, нужно ставить [концевик](images/lock-1.jpg), который будет замыкаться ригелем.
2. Не задаётся сколько вертеть до состояний "открыто" и "закрыто". Замок вертит пока вертится 🙂 У Danalock позиции задаются, поэтому при ручном вращении Danalock текущее состояние четко ловит.
3. Интеграция - это жесть. Есть два варианта: родной шлюз через интернет и костыли в виде аддона и прокси на esp32 (которую геморно собирать и готовых сборок нет). В случае с костылями теряется возможность управлять через родную приложуху. Но я смог это обойти немного пропатчив приложуху для вытягивания нужных ключей 🙂
И в целом стабильность этого решения отвратительная. При подачи команды через HA шлюз может не подключиться, пришлось городить автоматизации.
Но я через HA особо и не управляю, так, закрытие на ночь (вдруг забыл), или автооткрытие в режиме "ждём гостей".
4. Чувствительно к сопротивлению на ригеле. Ригель должен ходить свободно. Малейшее сопротивление - замок перестаёт вращать. Поэтому если ригель задевает за коробку - напильник в руки и точить.
5. Гигантский резервный ключ. Но мне пофиг, я ключ спрятал в стратегическом месте (тссс).

Плюсы:
1. Ну оно работает 🙂 Вроде даже стабильно на закрытие/открытие пальцами. За несколько месяцев использования никаких проблем не возникло.
2. Легко монтируется. Если конечно просверлены сквозные дырочки, у меня их не было, пришлось немного посверлить дверь сверлом на 7 🙂
3. Вроде не громко шумит. Даналок шумит громче как мне показалось. Если автоматика открывает/закрывает - от внезапного шума пугаешься.

### Мнение о Danalock
Минусы:

1. Нужен родной цилиндр за много денег, на имеющийся хрен поставишь.
2. Снаружи нет нормального управления: только пинпад за 10к или с блютусом как дебил тыкаться.
3. Стоит неоправдано дорого.
4. Шумный, но они все шумные.

Плюсы:

1. Очень легко ставится на родной цилиндр (у меня Lince) :)
2. Офигенно настраиваются точки до которых он будет крутить при открытии/закрытии.
3. Очень четко ловится текущее состояние при ручном управлении (актуально, когда у тебя соседи).

### Рулонные шторы
Первый способ:

1. Идём в мерлен, покупаем [трубу на 40](https://kirov.leroymerlin.ru/product/truba-40x15x2000-mm-12360177/) и любую самую дешманскую рулонную штору.
2. Отрываем полотно от шторы.
3. В трубе сверлим дырку и закручиваем болтик прям пластиковую фиговину на моторе.
4. Наматываем полотно и приклеиваем на супер-клей, или как я, на малярный скотч :)

Второй способ: Покупаем готовое полотно на трубе здесь - https://m-pl.ru/rulonnye-shtory-krep-blackout-pod-motor

## Статистика по устройствам
* Zigbee устройств: 58
* Esphome устройств: 26
* Прочих УД устройств на wifi: 16
