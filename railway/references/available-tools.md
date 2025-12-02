# Railway MCP 사용 가능한 도구

MCP 서버가 제공하는 모든 도구와 사용법입니다.

---

## 공식 MCP 서버 도구 (@railway/mcp-server)

공식 서버는 안전한 워크플로우에 중점을 둔 도구를 제공합니다. 파괴적 작업(삭제 등)은 의도적으로 제외되어 있습니다.

### 상태 확인 (Status)

#### check-railway-status

Railway CLI 설치 및 로그인 상태를 확인합니다.

**사용 예시:**
```
"Railway 상태 확인해줘"
"Railway CLI가 제대로 설치되어 있어?"
"Railway 로그인 상태 확인해줘"
```

**반환 정보:**
- CLI 설치 여부
- 로그인 상태
- 현재 연결된 프로젝트/환경

---

### 프로젝트 관리 (Projects)

#### list-projects

모든 Railway 프로젝트 목록을 조회합니다.

**사용 예시:**
```
"Railway 프로젝트 목록 보여줘"
"내 Railway 프로젝트들 확인해줘"
```

---

#### create-project-and-link

새 프로젝트를 생성하고 현재 디렉토리에 연결합니다.

**사용 예시:**
```
"새 Railway 프로젝트 만들어줘"
"my-app이라는 프로젝트 생성해줘"
```

---

### 서비스 관리 (Services)

#### list-services

현재 프로젝트의 서비스 목록을 조회합니다.

**사용 예시:**
```
"이 프로젝트의 서비스 목록 보여줘"
"현재 실행 중인 서비스들 확인해줘"
```

---

#### link-service

특정 서비스를 현재 디렉토리에 연결합니다.

**사용 예시:**
```
"backend 서비스에 연결해줘"
"api 서비스 링크해줘"
```

---

#### deploy

현재 디렉토리를 Railway에 배포합니다.

**사용 예시:**
```
"이 프로젝트 Railway에 배포해줘"
"현재 코드 배포해줘"
"Railway 배포 실행해줘"
```

---

#### deploy-template

Railway 템플릿을 배포합니다 (데이터베이스, 캐시 등).

**지원 템플릿:**
- PostgreSQL
- MySQL
- MongoDB
- Redis
- ClickHouse
- 그 외 Railway 템플릿

**사용 예시:**
```
"Postgres 데이터베이스 배포해줘"
"Redis 캐시 서버 추가해줘"
"단일 노드 ClickHouse 배포해줘"
"MongoDB 데이터베이스 생성해줘"
```

---

### 환경 관리 (Environments)

#### create-environment

새 환경을 생성합니다.

**사용 예시:**
```
"development 환경 만들어줘"
"staging 환경 생성해줘"
"production 환경을 복제해서 dev 환경 만들어줘"
```

---

#### link-environment

특정 환경을 현재 작업 환경으로 연결합니다.

**사용 예시:**
```
"production 환경으로 전환해줘"
"staging 환경에 연결해줘"
```

---

### 설정 관리 (Configuration)

#### list-variables

현재 환경의 환경 변수 목록을 조회합니다.

**사용 예시:**
```
"환경 변수 목록 보여줘"
"현재 설정된 변수들 확인해줘"
```

---

#### set-variables

환경 변수를 설정합니다.

**사용 예시:**
```
"DATABASE_URL 환경 변수 설정해줘"
"API_KEY를 xxx로 설정해줘"
"NODE_ENV를 production으로 변경해줘"
```

---

#### generate-domain

서비스에 railway.app 도메인을 생성합니다.

**사용 예시:**
```
"이 서비스에 도메인 할당해줘"
"Railway 도메인 생성해줘"
```

---

### 모니터링 (Monitoring)

#### get-logs

빌드 및 배포 로그를 조회합니다.

**기능 (CLI v4.9.0+):**
- 스트리밍/비스트리밍 모드
- 로그 필터링
- 배포별 로그 조회

**사용 예시:**
```
"배포 로그 보여줘"
"최근 빌드 로그 확인해줘"
"에러 로그만 필터링해서 보여줘"
"마지막 실패한 배포 로그 분석해줘"
```

---

## 커뮤니티 MCP 서버 도구 (@crazyrabbitltc/railway-mcp)

커뮤니티 버전은 146+ 도구로 100% Railway API 커버리지를 제공합니다.

### 추가 기능 카테고리

#### 프로젝트 고급 관리
- 프로젝트 삭제
- 프로젝트 설정 변경
- 프로젝트 전송

#### 서비스 고급 관리
- 서비스 삭제
- 서비스 재시작
- 서비스 스케일링
- 서비스 설정 변경

#### 배포 고급 관리
- 배포 롤백
- 배포 취소
- 배포 재시작
- 배포 상세 조회

#### 볼륨 관리
- 볼륨 생성
- 볼륨 삭제
- 볼륨 연결

#### 네트워킹
- 프라이빗 네트워킹
- TCP 프록시
- 커스텀 도메인 관리

#### 팀 관리
- 팀 생성/삭제
- 멤버 관리
- 권한 설정

#### 모니터링 고급
- 메트릭 조회
- 사용량 통계
- 비용 분석

**주의**: 커뮤니티 버전은 삭제 등 파괴적 작업도 포함됩니다. 신중하게 사용하세요.

---

## 자연어 사용 예시 모음

### 프로젝트 시작

```
"새 Next.js 프로젝트를 Railway에 생성하고 배포해줘"
"현재 디렉토리를 Railway 프로젝트로 초기화해줘"
"기존 프로젝트에 연결해줘"
```

### 데이터베이스 설정

```
"Postgres 데이터베이스 추가하고 DATABASE_URL 환경 변수 설정해줘"
"Redis 캐시 서버 배포해줘"
"MongoDB 연결 정보 보여줘"
```

### 배포 관리

```
"현재 코드를 Railway에 배포해줘"
"배포 상태 확인해줘"
"최근 배포 로그 보여줘"
"실패한 배포 원인 분석해줘"
```

### 환경 관리

```
"production 환경에서 staging으로 환경 변수 복사해줘"
"development 환경 만들어줘"
"현재 환경 변수 목록 보여줘"
```

### 도메인 설정

```
"이 서비스에 도메인 할당해줘"
"현재 도메인 정보 보여줘"
```

### 문제 해결

```
"마지막 배포가 왜 실패했는지 분석해줘"
"배포 로그에서 에러 찾아줘"
"서비스 상태 확인해줘"
```

### 고급 워크플로우

```
"production 환경을 복제해서 development 환경을 만들고, 테스트용 환경 변수로 변경해줘"
"Next.js 앱과 Postgres 데이터베이스를 같이 배포하고 연결해줘"
"최근 실패한 배포를 찾아서 로그를 분석하고 수정안을 제안해줘"
```

---

## CLI 명령어 참조

MCP와 함께 CLI도 활용할 수 있습니다:

| 명령어 | 설명 |
|--------|------|
| `railway login` | 로그인 |
| `railway logout` | 로그아웃 |
| `railway whoami` | 현재 사용자 확인 |
| `railway init` | 새 프로젝트 생성 |
| `railway link` | 기존 프로젝트 연결 |
| `railway unlink` | 프로젝트 연결 해제 |
| `railway up` | 배포 |
| `railway up -d` | 분리 모드 배포 |
| `railway logs` | 로그 확인 |
| `railway logs -f` | 실시간 로그 |
| `railway variables` | 환경 변수 목록 |
| `railway variables set KEY=value` | 변수 설정 |
| `railway domain` | 도메인 생성 |
| `railway open` | 대시보드 열기 |
| `railway status` | 상태 확인 |
| `railway run <cmd>` | 환경 변수와 함께 명령 실행 |

---

## MCP vs CLI 선택 가이드

| 상황 | 권장 |
|------|------|
| 자연어로 복잡한 작업 | MCP |
| 빠른 단일 명령 | CLI |
| 스크립트/자동화 | CLI |
| 대화형 워크플로우 | MCP |
| 로그 실시간 확인 | CLI (`railway logs -f`) |
| 여러 작업 조합 | MCP |
