# Railway MCP 트러블슈팅 가이드

일반적인 문제와 해결 방법입니다.

---

## MCP 연결 문제

### 문제: MCP 서버가 목록에 나타나지 않음

**증상:**
- `/mcp` 명령어에서 railway 서버가 보이지 않음
- "MCP server not found" 오류

**해결:**

1. **설정 파일 위치 확인**
   ```bash
   # 전역 설정
   cat ~/.claude/settings.json

   # 프로젝트 설정
   cat .claude/settings.local.json
   ```

2. **JSON 문법 검증**
   ```bash
   # JSON 유효성 검사
   cat ~/.claude/settings.json | python -m json.tool
   ```

3. **서버 재시작**
   ```bash
   # Claude Code에서
   /mcp restart railway
   ```

4. **설정 재확인**
   ```json
   {
     "mcpServers": {
       "railway": {
         "command": "npx",
         "args": ["-y", "@railway/mcp-server"]
       }
     }
   }
   ```

---

### 문제: "Railway CLI not found" 오류

**증상:**
- MCP 서버가 CLI를 찾지 못함
- "railway command not found" 메시지

**해결:**

1. **Railway CLI 설치 확인**
   ```bash
   railway --version
   ```

2. **CLI 설치 (미설치 시)**
   ```bash
   npm install -g @railway/cli
   ```

3. **PATH 확인**
   ```bash
   which railway
   # 또는 Windows
   where railway
   ```

4. **Node.js 전역 바이너리 경로 확인**
   ```bash
   npm bin -g
   ```

5. **PATH에 추가 (필요시)**
   ```bash
   export PATH="$PATH:$(npm bin -g)"
   ```

---

### 문제: "Not logged in" 오류

**증상:**
- MCP 작업 시 인증 실패
- "Please login first" 메시지

**해결:**

1. **로그인 상태 확인**
   ```bash
   railway whoami
   ```

2. **재로그인**
   ```bash
   railway login
   ```

3. **토큰 로그인 (자동화 환경)**
   ```bash
   railway login --token <YOUR_TOKEN>
   ```

---

### 문제: 커뮤니티 MCP "Authentication failed" 오류

**증상:**
- API 호출 시 401 에러
- "Invalid token" 메시지

**해결:**

1. **토큰 유효성 확인**
   ```bash
   # API 토큰 테스트
   curl -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
     https://backboard.railway.app/graphql/v2 \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "{ me { name } }"}'
   ```

2. **토큰 재발급**
   - [Railway Tokens](https://railway.app/account/tokens) 접속
   - 기존 토큰 삭제
   - 새 토큰 생성

3. **환경 변수 확인**
   ```bash
   echo $RAILWAY_API_TOKEN
   ```

4. **설정 파일 업데이트**
   ```json
   {
     "mcpServers": {
       "railway-full": {
         "env": {
           "RAILWAY_API_TOKEN": "새_토큰_여기에"
         }
       }
     }
   }
   ```

---

## 배포 문제

### 문제: 배포 실패 - 빌드 에러

**증상:**
- 배포 상태가 실패
- 빌드 로그에 에러 표시

**해결:**

1. **로컬 빌드 테스트**
   ```bash
   npm run build
   ```

2. **빌드 로그 확인**
   ```bash
   railway logs
   ```

3. **일반적인 빌드 에러:**

   | 에러 | 원인 | 해결 |
   |------|------|------|
   | `Module not found` | 의존성 누락 | `npm install` 재실행 |
   | `TypeScript error` | 타입 에러 | `npm run type-check` 후 수정 |
   | `Build command failed` | 빌드 스크립트 오류 | `package.json` 확인 |
   | `Out of memory` | 메모리 부족 | Railway 플랜 업그레이드 |

4. **Nixpacks 설정 확인**

   Railway는 Nixpacks를 사용합니다. `railway.json` 또는 `nixpacks.toml`로 설정:

   ```json
   // railway.json
   {
     "build": {
       "builder": "NIXPACKS",
       "buildCommand": "npm run build"
     },
     "deploy": {
       "startCommand": "npm start"
     }
   }
   ```

---

### 문제: 환경 변수가 적용되지 않음

**증상:**
- 앱에서 환경 변수 접근 불가
- `undefined` 값 반환

**해결:**

1. **환경 변수 확인**
   ```bash
   railway variables
   ```

2. **변수 설정**
   ```bash
   railway variables set DATABASE_URL="postgres://..."
   ```

3. **재배포 필요**
   - 환경 변수 변경 후 재배포 필요
   ```bash
   railway up
   ```

4. **올바른 환경 확인**
   ```bash
   railway status
   # 현재 연결된 환경 확인
   ```

5. **런타임 vs 빌드타임**
   - 빌드 시 필요한 변수와 런타임 변수 구분
   - Next.js: `NEXT_PUBLIC_*`는 빌드 시 필요

---

### 문제: 포트 연결 실패

**증상:**
- 앱이 시작되지만 접근 불가
- "Service unhealthy" 메시지

**해결:**

1. **PORT 환경 변수 사용**
   ```javascript
   // Node.js 예시
   const PORT = process.env.PORT || 3000;
   app.listen(PORT, '0.0.0.0', () => {
     console.log(`Server running on port ${PORT}`);
   });
   ```

2. **0.0.0.0 바인딩**
   - `localhost`가 아닌 `0.0.0.0`에 바인딩

3. **Railway 설정 확인**
   ```json
   // railway.json
   {
     "deploy": {
       "startCommand": "npm start"
     }
   }
   ```

---

### 문제: 도메인 연결 실패

**증상:**
- 커스텀 도메인 접속 불가
- DNS 확인 실패

**해결:**

1. **Railway 도메인 먼저 생성**
   ```bash
   railway domain
   ```

2. **DNS 설정 확인**
   ```bash
   # CNAME 확인
   dig +short www.example.com CNAME
   # your-app.up.railway.app 이어야 함
   ```

3. **DNS 전파 대기**
   - DNS 변경 후 최대 48시간 소요 가능
   - [DNS Checker](https://dnschecker.org/) 로 확인

4. **SSL 인증서**
   - Railway가 자동으로 SSL 발급
   - 발급에 최대 24시간 소요 가능

---

## CLI 문제

### 문제: `railway` 명령어를 찾을 수 없음

**해결:**

```bash
# 전역 설치
npm install -g @railway/cli

# 또는 npx 사용
npx @railway/cli

# PATH 확인
which railway
```

---

### 문제: 로그인 실패

**해결:**

1. **브라우저 로그인**
   ```bash
   railway login
   ```

2. **토큰 로그인**
   ```bash
   railway login --token <TOKEN>
   ```

3. **캐시 초기화**
   ```bash
   rm -rf ~/.railway
   railway login
   ```

---

### 문제: 프로젝트 연결 실패

**증상:**
- `railway link` 실패
- "Project not found" 오류

**해결:**

1. **프로젝트 존재 확인**
   - [Railway Dashboard](https://railway.app/dashboard) 확인

2. **올바른 디렉토리 확인**
   ```bash
   pwd
   ls -la
   ```

3. **연결 재설정**
   ```bash
   railway unlink
   railway link
   ```

---

## 성능 문제

### 문제: MCP 응답이 느림

**해결:**

1. **네트워크 확인**
   ```bash
   ping railway.app
   ```

2. **NPX 캐시 문제**
   ```bash
   # npm 캐시 정리
   npm cache clean --force
   ```

3. **로컬 설치 고려**
   - NPX 대신 전역 설치 사용

---

### 문제: 배포 시간이 오래 걸림

**해결:**

1. **빌드 캐시 활용**
   - Railway는 자동으로 빌드 캐시 사용

2. **.railwayignore 설정**
   ```
   node_modules
   .git
   .env.local
   ```

3. **Docker 이미지 최적화**
   - 멀티스테이지 빌드 사용

---

## 디버깅 팁

### MCP 서버 로그 확인

```bash
# 환경 변수로 디버그 모드 활성화
DEBUG=* npx @railway/mcp-server
```

### CLI 상세 출력

```bash
railway --verbose up
railway logs --verbose
```

### 프로젝트 상태 전체 확인

```bash
# 프로젝트 정보
railway status

# 서비스 목록
railway service

# 환경 변수
railway variables

# 현재 환경
railway environment
```

### API 직접 테스트 (커뮤니티 버전)

```bash
curl -H "Authorization: Bearer $RAILWAY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://backboard.railway.app/graphql/v2 \
  -d '{"query": "{ me { name email } }"}'
```

---

## 자주 묻는 질문

### Q: 공식 MCP와 커뮤니티 MCP 중 어떤 것을 사용해야 하나요?

**A:**
- **공식 (@railway/mcp-server)**: 안전한 기본 작업, 파괴적 작업 제외
- **커뮤니티 (@crazyrabbitltc/railway-mcp)**: 전체 API 접근, 고급 기능
- **권장**: 처음에는 공식 버전으로 시작, 필요시 커뮤니티 추가

### Q: MCP와 CLI 중 어떤 것을 사용해야 하나요?

**A:**
- **MCP**: 자연어로 복잡한 작업 수행, 대화형 워크플로우
- **CLI**: 빠른 단일 명령, 스크립트/자동화에 적합
- **둘 다**: 가장 유연한 조합

### Q: 토큰이 노출되면 어떻게 하나요?

**A:**
1. 즉시 [Railway Tokens](https://railway.app/account/tokens)에서 토큰 삭제
2. 새 토큰 발급
3. Git 히스토리에서 토큰 제거 (BFG Repo-Cleaner 사용)

### Q: 여러 Railway 계정을 사용할 수 있나요?

**A:**
- 공식 MCP: `railway login`으로 계정 전환
- 커뮤니티 MCP: 다른 이름으로 여러 서버 설정:

```json
{
  "mcpServers": {
    "railway-personal": { "env": { "RAILWAY_API_TOKEN": "token1" } },
    "railway-work": { "env": { "RAILWAY_API_TOKEN": "token2" } }
  }
}
```

### Q: Vercel과 Railway 중 어떤 것을 사용해야 하나요?

**A:**
- **Vercel**: 프론트엔드 중심, Next.js 최적화, Edge Functions
- **Railway**: 풀스택 앱, 데이터베이스 통합, 백엔드 서비스
- **둘 다**: Vercel (프론트엔드) + Railway (백엔드/DB) 조합 가능

---

## 지원 및 리소스

- [Railway 공식 문서](https://docs.railway.com/)
- [Railway Discord](https://discord.gg/railway)
- [Railway GitHub Issues](https://github.com/railwayapp/railway-mcp-server/issues)
- [Railway 상태 페이지](https://status.railway.app/)
