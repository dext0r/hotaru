# mdns-reflector
https://github.com/vfreex/mdns-reflector

## Внутри LXC с Alpine
echo 'console::respawn:/mdns-reflector -d lan iot' >> /etc/inittab
echo 'console::respawn:/mdns-reflector -d lan iotx' >> /etc/inittab
rc-update del crond default
rc-update del syslog boot
