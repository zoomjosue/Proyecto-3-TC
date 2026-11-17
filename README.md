# Simulador de Máquinas de Turing

Simulador determinista de Máquinas de Turing (MT) de **una cinta**, configurable mediante YAML. Procesa todas las cadenas declaradas, imprime la secuencia completa de descripciones instantáneas (IDs) y concluye si cada cadena fue aceptada, rechazada o detenida por el límite de seguridad.


## Requisitos

- Python 3.10 o posterior.
- PyYAML 6.x (se instala con el proyecto).

## Ejecución

```powershell
python main.py examples/reconocedor_anbn.yaml
```

Para reemplazar temporalmente las cadenas del YAML o modificar el límite de seguridad:

```powershell
python main.py examples/reconocedor_anbn.yaml --input aaabbb --input aabbb
python main.py examples/reconocedor_anbn.yaml --max-steps 20000
```

## Máquinas incluidas para la demostración

### 1. Reconocedor

[`examples/reconocedor_anbn.yaml`](examples/reconocedor_anbn.yaml) reconoce el lenguaje:

```text
L = { a^n b^n | n >= 1 }
```

Marca cada `a` procesada con `X` y su `b` correspondiente con `Y`. Incluye exactamente los casos requeridos, todos de longitud mayor o igual a cinco:

| Cadena | Resultado esperado |
|---|---|
| `aaabbb` | Aceptada |
| `aaaabbbb` | Aceptada |
| `aabbb` | Rechazada |
| `aaabb` | Rechazada |

### 2. Alterador

[`examples/alterador_duplicador.yaml`](examples/alterador_duplicador.yaml) transforma una cadena binaria `w` en `w#w`. La máquina usa `X`/`Y` como marcas temporales y la memoria caché para transportar cada bit al extremo derecho. Antes de aceptar, restaura la entrada original.

Incluye cuatro cadenas de longitud mayor o igual a cinco:

| Entrada | Cinta final esperada |
|---|---|
| `01010` | `01010#01010` |
| `11100` | `11100#11100` |
| `001011` | `001011#001011` |
| `101101` | `101101#101101` |

## Formato YAML

El blanco se representa con `null`. Cada símbolo debe tener un carácter. `tape_alphabet` debe contener todos los símbolos de `alphabet`, los símbolos auxiliares y `null`.

```yaml
q_states:
  q_list: [q0, q_accept]
  initial: q0
  final: q_accept       # también se admite una lista de estados finales

alphabet: [a]
tape_alphabet: [a, X, null]

delta:
  - params:
      initial_state: q0
      mem_cache_value: null
      tape_input: a
      output:
        final_state: q_accept
        mem_cache_value: null
        tape_output: X
        tape_displacement: S  # L, R o S

simulation_strings:
  - aaaaa
```

La función de transición se indexa por la terna `(estado, caché, símbolo leído)`. Por ello, dos entradas con esa misma terna se rechazan como una definición no determinista.

## Salida

Cada ID tiene la forma:

```text
0003 | _ X <q_find_b, cache=_> a b b _
```

- El número inicial es el paso.
- `_` representa el blanco.
- `<estado, cache=valor>` aparece inmediatamente antes de la celda bajo el cabezal.
- Se presenta la cinta significativa completa, con un blanco de contexto en cada extremo.

Una cadena se **acepta** al alcanzar un estado final. Se **rechaza** cuando no existe una transición para la configuración actual y el estado no es final. Si alcanza `--max-steps`, se reporta como **detenida**, no como rechazada, para evitar una conclusión falsa sobre una máquina que podría estar en un ciclo.

## Pruebas

No requieren dependencias adicionales:

```powershell
python -m unittest discover -s tests -v
```

## Códigos de salida

- `0`: todas las simulaciones terminaron por aceptación o falta de transición.
- `2`: error de argumentos o configuración.
- `3`: al menos una simulación alcanzó el límite de pasos.

## Video
https://youtu.be/pdeIM_XN8aQ