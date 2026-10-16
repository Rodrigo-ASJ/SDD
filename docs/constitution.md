# Constitución — habits-cli

Principios innegociables, Toda spec, plan, tarea debe cumplirlos.

1. **Stack mínimo**: solo Python 3.12+ y biblioteca estándar; pytest es la única
   dependencia (solo para tests). Toda dependencia nueva requiere actualizar la spec.
2. **Spec primero**: ninguna funcionalidad sin una spec en `specs/`. El código
   implementa la spec; si divergen, se corrige el código, no la spec.
3. **Lógica separada de la interfaz**: `habits/core.py` es puro (sin I/O, sin print);
   `habits/cli.py` solo parsea argumentos y presenta resultados.
4. **Tests obligatorios**: cada función pública de `core` tiene test; `pytest -q`
   pasa antes de cada commit.
5. **Persistencia estable**: JSON local con esquema documentado; cambiar su formato
   exige versión y migración antes de tocar el código.
6. **Idioma**: identificadores y nombres en inglés; mensajes al usuario en español.
