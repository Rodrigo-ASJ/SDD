# habits-cli

CLI en Python para registrar hábitos de estudio y ver la racha de días
consecutivos.

## Requisitos
- Python 3.12+ (solo biblioteca estándar).

## Uso

```sh
python -m habits add <nombre>   # Crea un hábito
python -m habits done <nombre>  # Marca/confirma el hábito como hecho hoy
python -m habits list           # Lista hábitos por racha (desempate alfabético)
```

Ejemplo:

```sh
python -m habits add Leer
python -m habits done Leer
python -m habits list
```

La racha es el número de días consecutivos completados cuyo último día es hoy o
ayer; si el último registro es anterior a ayer, la racha es 0.

## Almacenamiento
Un único archivo JSON en `~/.habits/data.json` (configurable con la variable de
entorno `HABITS_FILE`). Si el archivo no existe se crea vacío; si está dañado, el
programa aborta sin sobrescribirlo.

## Códigos de salida
- `0` operación correcta.
- `1` error de usuario o datos (nombre repetido/vacío, hábito inexistente,
  archivo dañado).
- `2` uso incorrecto de los argumentos.

## Tests
```sh
pytest -q
```
