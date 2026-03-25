# ESPHome File component

This component allows you to "inject" any raw file into the firmware as a progmem byte array.

## Example

```yaml
file:
  - id: my_file
    file: my_file.wav

button:
  - platform: template
    name: Play my file
    on_press:
      - lambda: id(my_speaker).play(id(my_file), sizeof(id(my_file)));
```
