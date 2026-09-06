# Проверки развёрнутого Kittygram

Проверено 6 сентября 2026 года. Приложение: [http://93.77.186.223:9000/](http://93.77.186.223:9000/).
Развёрнут коммит `59474450ae0dc87b5743193f24aa082fe2c6d92a`; последующие изменения документации приложение не меняют.

## Инфраструктура

- Terraform создал 5 ресурсов: VPC, подсеть, Security Group, статический IPv4 и ВМ.
- ВМ `kittygram`, ID `fhmlm2fj2n6iqhpgdsf0`, зона `ru-central1-a`: Ubuntu 24.04 LTS, 2 vCPU с core fraction 20%, 2 ГБ RAM, SSD 20 ГБ.
- Security Group проверена через YC API: входящие TCP22/9000, весь исходящий трафик. PostgreSQL наружу не опубликован.
- Бакет `kittygram-state-mezhnun89-b1g49hdr2hurtub7lqhs` создан заранее через S3 API. ACL закрытый, versioning включён.
- `kittygram/production.tfstate` прочитан из S3; outputs содержат фактические ID и IP ВМ.
- Cloud-init автоматически установил Docker/Compose; `cloud-init status --wait` вернул `status: done`, Compose — `v5.5.1`.
- Ключ SSH-сервера получен через доверенный serial output YC и записан в `SSH_KNOWN_HOSTS`. Actions подключается с `StrictHostKeyChecking=yes`.
- Новые ключи и пароли записаны в Actions Secrets, в исходники они не добавлялись. State и планы не публиковались в Git или Actions artifacts.

## Подтверждения GitHub Actions

| Проверка | Результат |
| --- | --- |
| [CI pull request](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34029552140) | PEP8, 5 backend-тестов с PostgreSQL, frontend, 7 проверок файлов, Terraform validate и Compose syntax — успешно |
| [Terraform plan](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34033720576) | 5 to add, 0 to change, 0 to destroy |
| [Terraform apply](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34033792732) | 5 ресурсов созданы; tests.yml автоматически обновлён |
| [Первый деплой](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34034021505/attempts/1) | Три образа опубликованы, миграции и статика выполнены, smoke и 11 автотестов пройдены, Telegram — успешно |
| [Повторный деплой](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34034021505/attempts/2) | Успешно; миграций для применения нет, smoke и все 11 автотестов снова пройдены |

JUnit доступен в [артефакте kittygram-test-results](https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final/actions/runs/34034021505/artifacts/9989785827).

## Функциональные проверки реального API

Проверки выполнялись на созданной ВМ с двумя временными тестовыми аккаунтами:

- Регистрация и вход проходят; гость получает 401 при запросе списка котов.
- Созданы карточки без фото; HEX-цвет корректно преобразуется в название.
- Своя карточка изменяется, фото и достижения сохраняются; URL media возвращает изображение.
- Второй аккаунт читает чужую карточку, но PATCH и DELETE возвращают 403.
- При 12 карточках первая страница содержит 10 записей, вторая доступна.
- Удаление своей карточки успешно; последующее чтение возвращает 404.
- После повторного деплоя все 11 оставшихся карточек доступны, SHA256 фотографии совпадает с исходным.

Главная страница возвращает HTTP200; React и JavaScript проверены отдельным smoke-тестом.
Облачный просмотрщик этой сессии не отобразил HTTP-сайт из-за собственной ошибки TLS.
Поэтому визуальная проверка интерфейса здесь не заявляется: доступность подтверждена HTTP-запросами и Actions,
а сценарии регистрации, карточек и прав — через реальный API.

## После проверки ревьюером

До завершения ревью ВМ должна оставаться включённой.
После зачёта сохраните нужные данные, отключите `DEPLOY_ENABLED` и выполните Terraform `destroy`,
чтобы прекратить расход на ВМ и публичный IP. Это удаляет диск ВМ вместе с базой и фотографиями.
Бакет state сохраняется отдельно; state не является резервной копией данных приложения.
