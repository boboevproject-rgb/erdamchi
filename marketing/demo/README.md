# Как снимался ролик marketing/erdamchi-threads.mp4

1. `backdrop.py` — ровный тёмный фон на весь экран (pythonw), поверх него окно Проводника с одной картинкой, поставленное командой `demo_input.py place <HWND> 520 180 1840 1440` (физические пиксели, экран 2880×1800).
2. `demo_input.py script plan.json` — скриптовый курсор через SendInput (глобальный хук Erdamchi видит только его): Ctrl + нажатие на файл, через 450 мс вокруг файла появляется донат, обход форматов по дуге, переворот колёсиком, отпускание на JPG.
3. Запись: `ffmpeg -f gdigrab -framerate 30 -offset_x 410 -offset_y 150 -video_size 1080x1350 -i desktop -t 26 …` параллельно со скриптом.
4. Монтаж: `ffmpeg -i take.mp4 -filter_complex_script filters.txt -map "[v]" …` — интро и финальный титр генерируются на лету, подписи по таймкодам, xfade между частями. Шрифты Segoe UI (bold/semibold) копируются из C:\Windows\Fonts в `fonts/` рядом со скриптом — в путях FFmpeg нельзя двоеточие.

Текущая версия ролика (14 с, без титров) собрана по `filters-cut.txt`; `filters.txt` — вариант с интро и финальным титром.
