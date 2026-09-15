# Robot mobilny — praca inżynierska

Konstrukcja i oprogramowanie czterokołowego (gąsienicowego) robota mobilnego.
Firmware czasu rzeczywistego na **STM32H755**, sterowanie z **ROS 2 Humble** na Jetson Nano, płyta główna w **KiCad** oraz modele mechaniczne przekładni i obudowy.

Autor: **Błażej Kruszka**, Uniwersytet Mikołaja Kopernika w Toruniu, 2025–2026.

## Architektura

```
gamepad  →  ROS 2 (Jetson)  →  UART 115200  →  STM32H755
                 │                                  │
                 └── /telemetry ← prędkości PI ← enkodery DC, PWM, A4988
```

- **STM32 (CM7)** — enkodery, regulatory PI, mostki H (4× DC), silniki krokowe (4× A4988), protokół UART.
- **ROS 2** — odczyt pada, mostek szeregowy, logger telemetrii.
- **PCB** — płyta główna pod Nucleo-H755, 8 kanałów wykonawczych i interfejsy czujników.

## Struktura repozytorium

| Katalog | Zawartość |
| --- | --- |
| `firmware/` | Projekt STM32CubeIDE (dual-core STM32H755ZITX), bez artefaktów kompilacji |
| `ros2_ws/` | Pakiet `robot_control` + Dockerfile |
| `pcb/` | KiCad (schemat, PCB, Gerber) |
| `mechanical/` | Modele STL i archiwum Fusion 360 |
| `control/` | Skrypt MATLAB do identyfikacji regulatorów PI |
| `docs/` | Praca, prezentacja, opis protokołu UART |

Nie ma tu notatek roboczych, dumpów CubeIDE, kopii zapasowych KiCad, filmów ani cudzych prac.

## Firmware (STM32)

Otwórz folder `firmware/` w STM32CubeIDE (projekt dual-core nadal nazywa się `jakie_wyjscia` — tak zapisał CubeMX). Zbuduj konfigurację **CM7 Debug** oraz CM4, jeśli boot dual-core ma zostać zachowany.

Aplikacja użytkownika:

- `firmware/CM7/Core/Src/PI.c` — pomiar prędkości z enkodera, filtr i regulator PI z rampą oraz anti-windup
- `firmware/CM7/Core/Src/motor_control.c` — PWM + kierunek mostka H, sleep/dir silników krokowych
- `firmware/CM7/Core/Src/main.c` — parser UART, pętla 10 ms, telemetria

Po resecie STM32 czeka na komendę `ready` (buzzer), dopiero potem przyjmuje zadawanie prędkości i krokowych.

## ROS 2

Wymagania: ROS 2 Humble, `python3-serial`, pakiet `inputs`.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch robot_control robot.launch.py
```

Port UART można zmienić parametrem węzła `stm_bridge`:

```bash
ros2 run robot_control stm_bridge --ros-args -p port:=/dev/ttyACM0 -p baudrate:=115200
```

### Docker (Jetson)

```bash
cd ros2_ws
sudo docker build -t robot_control:humble .
xhost +local:root
sudo docker run -it --rm --network host \
  --runtime nvidia \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --device /dev/input/js0 \
  --device /dev/ttyACM0 \
  robot_control:humble
```

W kontenerze: `source /home/ros_user/ws/install/setup.bash && ros2 launch robot_control robot.launch.py`.

## MATLAB

`control/pi_identification.m` wysyła sekwencję skoków `lspeed`/`rspeed` i rysuje zadanie vs. pomiar dla czterech kół. Ustaw `portName` na swój port (`COM18` w Windows, `/dev/ttyACM0` w Linux).

## PCB

Projekt KiCad 8: `pcb/PCBV2.kicad_pro`. Gerbery do produkcji są w `pcb/gerber/`. Podgląd schematu: `pcb/PCBV2.pdf`.

## Protokół UART

Zobacz [docs/uart.md](docs/uart.md).
