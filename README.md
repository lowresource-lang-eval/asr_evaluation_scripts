# asr_evaluation_scripts
Запуск evaluate.py (скрипт для codalab):
`python3 evaluate.py <путь к входящей директории> <путь к директории, куда будет записан результат>`

Во входящей директории должны быть две поддиректории:
1. ref: содержит файлы:
- speakers_test.tsv
- test.tsv
- ortho_test.tsv
3. res: содержит файлы:

- input_task1.tsv (результат классификации)

- input_task2.tsv (результат транскрибирования в IPA)

- input_task3.tsv (результат орфографии)

- input_task4.tsv (результат предсказания числа спикеров)

