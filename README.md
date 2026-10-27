# Erdamchi — конвертер файлов перетаскиванием

**Erdamchi** («помощник») — бесплатный офлайновый конвертер файлов для Windows (Linux и macOS унаследованы от
оригинала, не проверялись). Зажимаете клавишу, тянете файл — под курсором раскрывается круглое меню форматов,
бросаете на нужный, и готовый файл появляется рядом с оригиналом. 255 форматов в 18 категориях: изображения, PDF,
Word, Excel, PowerPoint, HWP/HWPX, видео, аудио, электронные книги, архивы, CAD, 3D-модели, шрифты, субтитры,
геоданные. Ничего не загружается в облако, Office не нужен.

Это форк проекта **[Filee](https://github.com/KnifeLemon/Filee)** (Myeonggu Kim / KnifeLemon, лицензия MIT),
переименованный и переведённый на данные владельца. Исходная лицензия и уведомления о сторонних компонентах
сохранены (`LICENSE`, `THIRD-PARTY-NOTICES.md`).

## Что изменено относительно Filee

- Название продукта, окна, трей, страница «О программе», тексты на 17 языках: Filee → Erdamchi.
- Исполняемые файлы: `Erdamchi.exe`, `erdamchi-cli.exe`, команда `erdamchi` (`cli\erdamchi.cmd`).
- Ссылки «репозиторий», «сообщить об ошибке», «последний релиз», «сайт», проверка обновлений →
  <https://github.com/boboevproject-rgb/erdamchi>. Спонсорские ссылки автора заменены на GitHub владельца.
- Папка настроек `%APPDATA%\Erdamchi`, движки `%LOCALAPPDATA%\Erdamchi\engines`, свой GUID установщика и свой
  мьютекс — Erdamchi не конфликтует с установленным Filee.
- Авторы и копирайт в метаданных сборки: Bilol Bobozoda; оригинал указан как основа.
- Удалены переводы README и FUNDING оригинала; CODEOWNERS, SECURITY, CODE_OF_CONDUCT указывают на владельца.

Не трогалось: внутренние пространства имён `Filee.*` и имена проектов (чтобы не ломать сборку), иконки и логотип,
тесты (`tests/`, ссылаются на старые имена), установщики Linux/macOS.

## Сборка на Windows

Нужен .NET SDK 10 (`global.json`). Если SDK стоит в `D:\dotnet`, как на машине владельца:

```powershell
$env:DOTNET_ROOT = "D:\dotnet"; $env:PATH = "D:\dotnet;$env:PATH"; $env:NUGET_PACKAGES = "D:\dev\nuget"
.\build\fetch-fonts.ps1                                   # шрифты Noto для интерфейса (36 МБ, один раз)
dotnet publish src\Filee.App\Filee.App.csproj -c Release -r win-x64 --self-contained -p:FileeRelease=true -p:PublishReadyToRun=false -o publish\win-x64
dotnet publish src\Filee.Cli\Filee.Cli.csproj -c Release -r win-x64 --self-contained -p:FileeRelease=true -p:PublishReadyToRun=false -o publish\win-x64
```

Запуск: `publish\win-x64\Erdamchi.exe`. Это «портативная» копия (без `uninstall.exe` рядом с exe приложение считает
себя портативным). Большие движки (LibreOffice, FFmpeg, Pandoc и др.) приложение скачивает само по запросу; rhwp и
7-Zip для установщика кладёт `build\fetch-engines.ps1 -Only rhwp,7zip`.

Полный установщик `Erdamchi-<версия>-win-Setup.exe` и портативный zip (нужен PowerShell 7, `pwsh`):

```powershell
.\build\fetch-engines.ps1 -Only rhwp,7zip -Destination publish\win-x64\engines -RuntimeTo publish\win-x64
pwsh .\build\build-explorer-menu.ps1 -Destination publish\win-x64      # сам скачает zig, соберёт DLL и MSIX меню Проводника
dotnet publish src\Filee.Setup\Filee.Setup.csproj -c Release -r win-x64 -p:FileeSetupPublish=true -o build\.cache\setup
pwsh .\build\build-installer.ps1 -PublishDir publish\win-x64 -SetupProgram build\.cache\setup\Filee.Setup.exe -Portable
```

Результат в `Releases\`. Сборка не подписана: SmartScreen покажет предупреждение, «Подробнее → Выполнить в любом случае».

## Обновления из оригинала

Исходный репозиторий подключён как `upstream`: `git fetch upstream && git merge upstream/main`, после чего заново
прогнать замену бренда (`tools\rebrand.py`).
