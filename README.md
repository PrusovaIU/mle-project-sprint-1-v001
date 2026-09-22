# Проект 1 спринта

## О проекте

Репозиторий содержит решение проекта 1 спринта: пайплайн подготовки данных
и обучения модели для предсказания стоимости квартир Яндекс Недвижимости.

Проект разбит на две части:

- `part1_airflow/` — DAG очистки и предобработки данных (удаление пропусков,
  выбросов и битых записей).
- `part2_dvc/` — DVC-пайплайн с feature engineering и обучением модели
  на подготовленных данных из первой части.

## Хранилище артефактов

**Имя бакета:** `s3-student-mle-20260908-0538921743`

Endpoint: `https://storage.yandexcloud.net`

Чтобы проверить артефакты, выполните `dvc pull` в директории `part2_dvc/` —
будут скачаны датасеты (`data/*.csv`) и обученная модель
(`models/fitted_model.pkl`).

---

## Часть 1. Apache Airflow — предобработка данных

### DAG `buildings_flats`

- **Путь к файлу DAG:** `part1_airflow/dags/buildings_flats.py`
- **Имя DAG:** `buildings_flats`
- **Расписание:** `@once`
- **Теги:** `buildings`, `flats`
- **Вспомогательные функции (реализация шагов):**
  `part1_airflow/plugins/steps/buildings_flats.py`

### Шаги DAG

| Шаг (task_id)   | Функция (python_callable) | Назначение                                                        |
|-----------------|---------------------------|-------------------------------------------------------------------|
| `create_table`  | `create_table`            | Создание целевой таблицы в БД для подготовленных данных           |
| `extract`       | `extract`                 | Выгрузка исходных данных из источника                             |
| `transform`     | `transform`               | Очистка данных: удаление пропусков, выбросов и битых записей      |
| `load`          | `load`                    | Загрузка подготовленных данных в целевую таблицу                  |

Порядок выполнения шагов задан цепочкой зависимостей:

```python
create_table_step >> extract_step >> transform_step >> load_step
```

Результат работы DAG — очищенный датасет, который используется как вход
для DVC-пайплайна во второй части проекта.

### Вспомогательные модули

- `part1_airflow/plugins/steps/buildings_flats.py` — реализация шагов
  `create_table`, `extract`, `transform`, `load`.
- `part1_airflow/plugins/steps/messages.py` — функции для отправки
  уведомлений в Telegram. Используются как колбэки DAG'а:
  - `send_telegram_success_message` — вызывается при успешном завершении DAG
    (передан в `on_success_callback`);
  - `send_telegram_failure_message` — вызывается при падении DAG
    (передан в `on_failure_callback`).

### Запуск Airflow

```bash
cd part1_airflow
docker-compose up
```

Подробности конфигурации — в `part1_airflow/docker-compose.yaml`
и `part1_airflow/Dockerfile`. Переменные окружения задаются в
`part1_airflow/env_template` (скопируйте в `.env` и заполните).

---

## Часть 2. DVC-пайплайн — feature engineering и обучение модели

### Структура `part2_dvc/`

```
part2_dvc/
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── env_template
├── scripts/
│   ├── __init__.py
│   ├── utils.py
│   ├── data.py
│   ├── split.py
│   ├── fit.py
│   └── evaluate.py
├── data/          # артефакты под контролем DVC
├── models/        # артефакты под контролем DVC
├── cv_results/    # метрики
├── mlruns/        # MLflow (эксперименты)
└── notebooks/
    └── learn_baseline.ipynb
```

### Python-код этапов DVC

| Стейдж DVC        | Файл скрипта                       | Функция DAG         | Назначение                                                       |
|-------------------|------------------------------------|---------------------|------------------------------------------------------------------|
| `get_data`        | `part2_dvc/scripts/data.py`        | `get_data()`        | Загрузка подготовленных данных из БД                              |
| `split_data`      | `part2_dvc/scripts/split.py`       | `split_data()`      | Разбиение данных на train/val                                     |
| `fit_model`       | `part2_dvc/scripts/fit.py`         | `fit_model()`       | Feature engineering (кодирование, масштабирование) и обучение     |
| `evaluate_model`  | `part2_dvc/scripts/evaluate.py`    | `evaluate_model()`  | Расчёт метрик (MAE, MAPE, MedAE, R²)                              |

Общие утилиты — `part2_dvc/scripts/utils.py` (функция `load_params`).

### Конфигурация DVC

- `part2_dvc/dvc.yaml` — описание стейджей пайплайна
- `part2_dvc/params.yaml` — гиперпараметры и пути к артефактам
- `part2_dvc/dvc.lock` — зафиксированные хэши зависимостей и выходов

### Запуск DVC-пайплайна

```bash
cd part2_dvc

# Подтянуть данные и модель из S3
dvc pull

# Воспроизвести пайплайн
dvc repro

# Посмотреть метрики
dvc metrics show

# Отправить обновлённые артефакты в S3
dvc push
```

### Метрики baseline-модели

| Метрика | Значение          |
|---------|-------------------|
| MAE     | 1 863 224.51 руб  |
| MAPE    | 16.68 %           |
| MedAE   | 1 574 104.35 руб  |
| R²      | 0.728             |

---

## Требования

Общие зависимости — в `requirements.txt` в корне репозитория:

```bash
pip install -r requirements.txt
```

Для работы DVC с S3 нужен пакет с поддержкой S3:

Для запуска DAG'ов Airflow — Docker и docker-compose, см. `part1_airflow/`.

## Переменные окружения

В репозитории лежат шаблоны без секретов:

- `part1_airflow/env_template` — переменные для Airflow;
- `part2_dvc/env_template` — переменные для подключения к БД и S3.

Скопируйте шаблон в `.env`, заполните своими значениями и **не коммитьте**
`.env` в Git.