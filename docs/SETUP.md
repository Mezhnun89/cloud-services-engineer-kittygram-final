# Первый запуск в Yandex Cloud

## 1. Подготовить учётные записи

Используйте свой аккаунт Yandex Cloud с промокодом куратора и отдельный каталог для Kittygram.
Локальная VirtualBox-ВМ из предыдущей практики не нужна для этого проекта.
Старый DBOps-сервер и старый Kittygram-сервер не участвуют в новом деплое.

Понадобятся Terraform **1.13.x**, YC CLI с вашим профилем и GitHub CLI (`gh auth login`).
Можно выполнять подготовку в доверенном терминале, где доступен `yc`; JSON и приватные ключи в чат не отправляйте.

Создайте сервисный аккаунт `kittygram-terraform` в учебном каталоге.
Для учебного отдельного каталога можно выдать ему `editor` и `storage.admin` на **этот каталог**.
Создайте для него авторизованный JSON-ключ (для провайдера YC) и статический ключ доступа (для S3 backend).
Авторизованный JSON и пара S3 access/secret — разные учётные данные.

Создайте отдельную пару SSH-ключей для `deploy`. Пример PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.ssh" | Out-Null
ssh-keygen -t ed25519 -f "$HOME\.ssh\kittygram_deploy" -C kittygram-deploy
```

Для автоматического runner нужен ключ без passphrase. Если файл уже существует, не соглашайтесь на перезапись:
выберите другое имя. Публичный `.pub` нужен cloud-init; приватный файл нужен GitHub Actions.

## 2. Создать отдельный бакет state

В клоне этой ветки, в PowerShell (значения замените своими):

```powershell
$env:YC_SERVICE_ACCOUNT_KEY_FILE = (Resolve-Path 'C:\path\to\yc-key.json').Path
$env:TF_VAR_folder_id = 'YOUR_FOLDER_ID'
$env:TF_VAR_state_bucket = 'kittygram-state-mezhnun89-UNIQUE_SUFFIX'
$env:CHECKPOINT_DISABLE = '1'
terraform -chdir=bootstrap init
terraform -chdir=bootstrap plan -out=bootstrap.tfplan
terraform -chdir=bootstrap apply bootstrap.tfplan
```

`bootstrap/` использует локальный state, потому что бакета до этого шага ещё нет.
Сохраните `bootstrap/terraform.tfstate` в личном защищённом месте; не добавляйте его в Git.
Бакет закрыт, versioning включён, `prevent_destroy` защищает от случайного Terraform destroy.
Основной `infra/` использует уже созданный бакет и отдельный state.
Альтернатива — заранее создать такой же закрытый бакет с versioning в консоли; не запускайте bootstrap
повторно для уже существующего бакета без `terraform import`.

## 3. GitHub Secrets и Variables

Репозиторий: `Mezhnun89/cloud-services-engineer-kittygram-final`.
Settings → Secrets and variables → Actions. Секреты добавляются во вкладке **Secrets**, обычные параметры — **Variables**.

| Secret | Значение |
| --- | --- |
| `YC_SERVICE_ACCOUNT_JSON` | Полное содержимое авторизованного JSON-ключа сервисного аккаунта |
| `AWS_ACCESS_KEY_ID` | ID статического ключа сервисного аккаунта для S3 |
| `AWS_SECRET_ACCESS_KEY` | Секретная часть статического ключа |
| `SSH_PUBLIC_KEY` | Одна строка из `kittygram_deploy.pub` |
| `SSH_KEY` | Полное содержимое приватного `kittygram_deploy` |
| `SSH_KNOWN_HOSTS` | Строка с IP и проверенным публичным ключом сервера; добавляется после apply |
| `POSTGRES_PASSWORD` | Новый случайный пароль БД для новой ВМ, сохранить для следующих деплоев |
| `DJANGO_SECRET_KEY` | Новый постоянный случайный ключ Django |
| `DOCKER_USERNAME` | `mezhnun` — прежний DockerHub login |
| `DOCKER_PASSWORD` | DockerHub access token с правом записи трёх образов |
| `TELEGRAM_TO` | ID чата для уведомления о сдаваемом проекте |
| `TELEGRAM_TOKEN` | Токен существующего бота для этого чата |

Для пароля БД и Django удобно генерировать URL-safe строки: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
Не используйте переносы строк, одинарные кавычки и обратный слеш в этих двух значениях.
Не меняйте пароль уже инициализированной БД только через `.env`: PostgreSQL не переустанавливает пароль существующей роли.

| Variable | Значение |
| --- | --- |
| `YC_CLOUD_ID` | ID вашего облака |
| `YC_FOLDER_ID` | ID отдельного учебного каталога |
| `TF_STATE_BUCKET` | Имя созданного бакета |
| `GATEWAY_PORT` | `9000` |
| `DEPLOY_ENABLED` | Сначала `false`, после apply и проверки SSH — `true` |

Прежние `SSH_HOST`, `SSH_USER`, `SSH_PORT` для нового workflow не используются:
адрес приходит из Terraform, пользователь — `deploy`, порт — 22.
Не удаляйте старые секреты, если они используются другими вашими workflow.
Три DockerHub-репозитория `kittygram_backend`, `kittygram_frontend`, `kittygram_gateway` должны быть публичными
для скачивания на ВМ и проверок Практикума.

## 4. Создать инфраструктуру

После успешного CI объедините PR с `main`.
Actions → Terraform infrastructure → Run workflow, ветка `main`, операция `plan`.
Проверьте, что создаются только ресурсы Kittygram в нужном каталоге.
Запустите `apply`. Workflow сохранит state в S3, выведет URL в Summary и обновит `tests.yml` в main.
Если branch protection запрещает push боту, инфраструктура может быть создана, а запись tests.yml отклонена:
в таком случае обновите только `kittygram_domain` через обычный PR значением из Summary.
Секреты и права workflow задаются до запуска; runner не может получить их из вашего локального `yc` автоматически.

Бакет S3 здесь используется без отдельного сервиса distributed locking.
GitHub concurrency сериализует два workflow; **не запускайте параллельно Terraform из локального терминала**.
Для нескольких независимых операторов нужно дополнительно настроить штатную блокировку state через YDB.

## 5. Проверить SSH и завершение cloud-init

В консоли YC откройте созданную ВМ → вывод последовательного порта.
В конце cloud-init появятся маркер `KITTYGRAM_SSH_HOST_KEY`, публичный ключ `ssh-ed25519 AAAA...` и fingerprint.
Получить тот же вывод через доверенный YC CLI можно командой:

```bash
yc compute instance get-serial-port-output --id <VM_ID>
```

Сформируйте Secret `SSH_KNOWN_HOSTS` из фактического IPv4 и ключа из консоли:

```text
<VM_IP> ssh-ed25519 <PUBLIC_HOST_KEY_BASE64>
```

Это **публичный ключ самого сервера**, а не ваш `kittygram_deploy.pub` и не одна строка fingerprint.
Не подменяйте проверку ключа отключением `StrictHostKeyChecking`.
При пересоздании ВМ её ключ меняется — повторите проверку.

Первое SSH-подключение с ПК:

```powershell
ssh -i "$HOME\.ssh\kittygram_deploy" deploy@<VM_IP>
```

Далее на ВМ:

```bash
sudo cloud-init status --long
sudo docker compose version
```

В workflow уже предусмотрено ожидание SSH, завершения cloud-init и готовности PostgreSQL.
Если cloud-init завершился с ошибкой, смотрите `/var/log/cloud-init-output.log` и `sudo journalctl -u cloud-final`.

## 6. Деплой и сдача

1. Установите Variable `DEPLOY_ENABLED=true`.
2. Запустите **Kittygram deployment** вручную с ветки `main` (после записи актуального tests.yml).
3. Дождитесь backend/frontend checks, DockerHub build, deploy и итоговых тестов.
4. Откройте URL из Summary; выполните ручные пункты `docs/VERIFICATION.md`.
5. Сохраните JUnit artifact из workflow и скриншоты Terraform ресурсов/бакета, сайта и зелёного Actions.
6. Отправьте в Практикум ссылку `https://github.com/Mezhnun89/cloud-services-engineer-kittygram-final`.

Workflow отправит сообщение в настроенный Telegram-чат только после успешных проверок.
Ответ ревьюера ожидается по условиям курса в течение 48 часов; возможны до трёх доработок.

## Источники

- [State в Object Storage](https://yandex.cloud/en/docs/tutorials/infrastructure-management/terraform-state-storage)
- [Блокировка state через YDB](https://yandex.cloud/en/docs/tutorials/infrastructure-management/terraform-state-lock)
- [Создание ВМ с cloud-init](https://yandex.cloud/en/docs/compute/operations/vm-create/create-with-cloud-init-scripts)
- [Docker Engine на Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Функциональность Kittygram из задания](https://storage.yandexcloud.net/practicum-devops/dcm/kittygram-project.pdf)
