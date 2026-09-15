# Protokół UART (115200 8N1)

Linie kończy `\n`. STM32 zaczyna wykonywać komendy jezdne dopiero po `ready`.

## Komendy do STM32

| Komenda | Znaczenie |
| --- | --- |
| `ready` | Start pętli regulacji i krótki sygnał buzzera |
| `lspeed=<int>` | Zadana prędkość lewej burty, zakres ok. −100…100 (% max RPM) |
| `rspeed=<int>` | Zadana prędkość prawej burty |
| `forward` / `backward` / `stop` | Kierunek / zatrzymanie silników krokowych (aktywne tylko te, które włączono `*_step`) |
| `fright_step` / `fleft_step` / `bright_step` / `bleft_step` | Przełączenie danego silnika krokowego |
| `P=<int>` / `I=<int>` | Współczynniki PI dla wszystkich czterech kół DC |

## Telemetria ze STM32

CSV, 8 wartości, okres 100 ms:

```
rb_set, rb_meas, rf_set, rf_meas, lb_set, lb_meas, lf_set, lf_meas
```

Jednostka: RPM (zadanie i prędkość przefiltrowana z enkodera).
Mostek ROS dopina na końcu aktualne `lspeed` i `rspeed` wysłane z pada.
