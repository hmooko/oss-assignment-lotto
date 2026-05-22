# 6/45 Lotto

Django와 Docker Compose를 사용한 6/45 Lotto 웹 사이트 과제입니다.

## 실행 방법

```bash
cp .env.example .env
docker compose up --build
```

브라우저에서 `http://localhost:8000`으로 접속합니다.
`.env`를 만들지 않아도 기본 개발값으로 실행되지만, 제출/배포 전에는 `.env.example`을 복사해 값을 명시하는 것을 권장합니다.

## 관리자 계정 생성

```bash
docker compose exec web python manage.py createsuperuser
```

첫 회차 생성:

```bash
docker compose exec web python manage.py create_next_round
```

관리자는 Django Admin에서 회차를 생성하고, 웹 관리자 대시보드에서 판매 내역 확인, 추첨 실행, 당첨 내역 확인을 할 수 있습니다.

## 테스트

```bash
python manage.py test
```

Make 명령을 사용할 수도 있습니다.

```bash
make check
make test
make verify
```

Docker 실행 검증:

```bash
docker compose build
docker compose up -d
curl -I http://localhost:8000
```

## GitHub 제출 준비

GitHub CLI 인증이 되어 있다면 다음 명령으로 원격 저장소를 만들고 push합니다.

```bash
gh auth login
gh repo create oss-assignment-lotto --public --source=. --remote=origin --push
```

push 후 `docs/report.md`의 GitHub 링크를 실제 저장소 URL로 교체합니다.

제출 전 점검 항목은 `docs/submission-checklist.md`에 정리되어 있습니다.

## 주요 기능

- 일반 사용자: 회원가입, 로그인, 수동 번호 구매, 자동 번호 구매, 구매 내역 조회, 당첨 확인
- 관리자: 회차 관리, 판매 내역 확인, 추첨 실행, 당첨 내역 확인
- Docker multi-container: Django `web`, PostgreSQL `db`
