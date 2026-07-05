# Alternative firmware for eWeLink ZB-SW01 / ZB-SW02

The original firmware has some drawbacks:

1. A no-neutral switch that also acts as a router is a bad idea. Nobody does it this way.
2. If you toggle it quickly in ZHA, sooner or later the status gets out of sync. This is probably caused by spamming Route Request packets.
3. Reporting intervals can't be configured.

To fix these drawbacks you can use a PTVO-based firmware. With it, the switch becomes super fast and stable.

Inside there is a CC2530 module / [SM015](https://github.com/CoolKit-Technologies/DevDocs/blob/master/Zigbee/SM-015应用指导.md). The DD/DC pins are not exposed. You need to either desolder the whole module with a hot air gun, or [solder](./PCB.jpg) directly to the chip (my choice). You can use an ESP8266 and <https://mt.xyzroe.cc>
