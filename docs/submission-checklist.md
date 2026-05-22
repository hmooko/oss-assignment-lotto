# 제출 체크리스트

## 코드

1. Django 프로젝트가 정상 실행된다.
2. 일반 사용자는 수동/자동 복권 구매, 구매 내역 조회, 당첨 확인을 할 수 있다.
3. 관리자는 판매 내역 확인, 추첨 실행, 당첨 내역 확인을 할 수 있다.
4. Docker Compose가 `web`, `db` multi-container로 실행된다.
5. 테스트가 통과한다.

## 보고서

1. 프로젝트 개요가 포함되어 있다.
2. 요구사항 분석이 포함되어 있다.
3. 시스템 설계와 DB 설계가 포함되어 있다.
4. 구현 과정이 포함되어 있다.
5. 테스트 결과가 포함되어 있다.
6. 실행 방법이 포함되어 있다.
7. GitHub 링크가 포함되어 있다.

## 제출 전 명령

```bash
python manage.py test
docker compose build
docker compose up -d
curl -I http://localhost:8000
```

## GitHub 업로드

```bash
gh auth login
gh repo create oss-assignment-lotto --public --source=. --remote=origin --push
```

업로드 후 [report.md](/Users/koohyunmo/Developer/oss-assignment-lotto/docs/report.md)의 `GitHub: TODO`를 실제 URL로 교체한다.
