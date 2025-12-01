# Vercel MCP 트러블슈팅 가이드

일반적인 문제와 해결 방법입니다.

---

## MCP 연결 문제

### 문제: MCP 서버가 목록에 나타나지 않음

**증상:**
- `/mcp` 명령어에서 vercel 서버가 보이지 않음
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
   # Claude Code 재시작
   # 또는
   /mcp restart vercel
   ```

---

### 문제: "Authentication failed" 오류

**증상:**
- API 호출 시 401 에러
- "Invalid token" 메시지

**해결:**

1. **토큰 유효성 확인**
   ```bash
   curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
     https://api.vercel.com/v2/user
   ```

2. **토큰 재발급**
   - [Vercel Tokens](https://vercel.com/account/tokens) 접속
   - 기존 토큰 삭제
   - 새 토큰 생성

3. **환경 변수 확인**
   ```bash
   echo $VERCEL_API_TOKEN
   ```

4. **설정 파일 업데이트**
   ```json
   {
     "mcpServers": {
       "vercel": {
         "env": {
           "VERCEL_API_TOKEN": "새_토큰_여기에"
         }
       }
     }
   }
   ```

---

### 문제: "Permission denied" 오류

**증상:**
- 특정 프로젝트/팀에 접근 불가
- 403 Forbidden 응답

**해결:**

1. **토큰 스코프 확인**
   - 토큰이 해당 팀/프로젝트에 접근 권한이 있는지 확인
   - 필요시 "Full Account" 스코프로 새 토큰 발급

2. **팀 ID 확인**
   ```bash
   curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
     https://api.vercel.com/v2/teams
   ```

3. **팀 설정 추가**
   ```json
   {
     "env": {
       "VERCEL_API_TOKEN": "token",
       "VERCEL_TEAM_ID": "team_xxxxx"
     }
   }
   ```

---

## 배포 문제

### 문제: 배포 실패 - 빌드 에러

**증상:**
- 배포 상태가 "ERROR"
- 빌드 로그에 에러 표시

**해결:**

1. **로컬 빌드 테스트**
   ```bash
   npm run build
   ```

2. **Vercel 빌드 시뮬레이션**
   ```bash
   vercel build
   ```

3. **빌드 로그 확인**
   ```bash
   vercel logs <deployment-url>
   ```

4. **일반적인 빌드 에러:**

   | 에러 | 원인 | 해결 |
   |------|------|------|
   | `Module not found` | 의존성 누락 | `npm install` 재실행 |
   | `TypeScript error` | 타입 에러 | `npm run type-check` 후 수정 |
   | `Out of memory` | 메모리 부족 | Vercel 플랜 업그레이드 또는 빌드 최적화 |
   | `Build timeout` | 빌드 시간 초과 | 빌드 최적화 또는 캐시 활용 |

---

### 문제: 환경 변수가 적용되지 않음

**증상:**
- 앱에서 환경 변수 접근 불가
- `undefined` 값 반환

**해결:**

1. **환경 변수 동기화**
   ```bash
   vercel env pull .env.local
   ```

2. **환경 변수 확인**
   ```bash
   vercel env ls
   ```

3. **올바른 환경 타겟 확인**
   - `production`: 프로덕션 배포에만 적용
   - `preview`: 프리뷰 배포에만 적용
   - `development`: 로컬 개발에만 적용

4. **재배포 필요**
   - 환경 변수 변경 후 재배포 필요
   ```bash
   vercel --prod
   ```

5. **빌드 타임 vs 런타임**
   - `NEXT_PUBLIC_*`: 클라이언트에서 접근 가능
   - 그 외: 서버에서만 접근 가능

---

### 문제: 도메인 연결 실패

**증상:**
- 커스텀 도메인 접속 불가
- DNS 확인 실패

**해결:**

1. **DNS 설정 확인**
   ```bash
   # A 레코드 확인
   dig +short example.com A
   # 76.76.21.21 이어야 함

   # CNAME 확인
   dig +short www.example.com CNAME
   # cname.vercel-dns.com 이어야 함
   ```

2. **Vercel 도메인 상태 확인**
   ```bash
   vercel domains inspect example.com
   ```

3. **DNS 전파 대기**
   - DNS 변경 후 최대 48시간 소요 가능
   - [DNS Checker](https://dnschecker.org/) 로 확인

4. **SSL 인증서 확인**
   - Vercel이 자동으로 SSL 발급
   - 발급에 최대 24시간 소요 가능

---

## CLI 문제

### 문제: `vercel` 명령어를 찾을 수 없음

**해결:**

```bash
# 전역 설치
npm install -g vercel

# 또는 npx 사용
npx vercel

# PATH 확인
which vercel
```

---

### 문제: 로그인 실패

**해결:**

1. **브라우저 로그인**
   ```bash
   vercel login
   ```

2. **토큰 로그인**
   ```bash
   vercel login --token $VERCEL_API_TOKEN
   ```

3. **캐시 초기화**
   ```bash
   rm -rf ~/.vercel
   vercel login
   ```

---

### 문제: 프로젝트 연결 실패

**증상:**
- `vercel link` 실패
- "Project not found" 오류

**해결:**

1. **프로젝트 존재 확인**
   ```bash
   vercel projects ls
   ```

2. **올바른 디렉토리 확인**
   ```bash
   pwd
   ls -la .vercel
   ```

3. **연결 재설정**
   ```bash
   rm -rf .vercel
   vercel link
   ```

---

## 성능 문제

### 문제: MCP 응답이 느림

**해결:**

1. **네트워크 확인**
   ```bash
   ping api.vercel.com
   ```

2. **로컬 서버 사용**
   - NPX 대신 로컬 설치 사용
   - Docker 컨테이너 사용

3. **캐싱 활용**
   - 자주 사용하는 조회는 캐싱 고려

---

### 문제: Rate Limit 초과

**증상:**
- 429 Too Many Requests 오류
- "Rate limit exceeded" 메시지

**해결:**

1. **요청 간격 조절**
   - API 호출 사이에 딜레이 추가

2. **배치 요청 사용**
   - 여러 요청을 하나로 묶기

3. **Vercel 플랜 확인**
   - Pro/Enterprise 플랜은 더 높은 limit 제공

---

## 디버깅 팁

### MCP 서버 로그 확인

```bash
# 환경 변수로 디버그 모드 활성화
DEBUG=* npx mcp-vercel
```

### API 직접 테스트

```bash
# 사용자 정보 확인
curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
  https://api.vercel.com/v2/user | jq

# 프로젝트 목록
curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
  https://api.vercel.com/v9/projects | jq

# 배포 목록
curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
  "https://api.vercel.com/v6/deployments?limit=5" | jq
```

### Claude Code 디버그 모드

```bash
# 상세 로그와 함께 실행
claude --debug
```

---

## 자주 묻는 질문

### Q: MCP와 CLI 중 어떤 것을 사용해야 하나요?

**A:**
- **MCP**: 자연어로 복잡한 작업 수행, 자동화에 적합
- **CLI**: 빠른 단일 명령, 스크립트에 적합
- **둘 다**: 가장 유연한 조합

### Q: 토큰이 노출되면 어떻게 하나요?

**A:**
1. 즉시 [Vercel Tokens](https://vercel.com/account/tokens)에서 토큰 삭제
2. 새 토큰 발급
3. Git 히스토리에서 토큰 제거 (BFG Repo-Cleaner 사용)

### Q: 여러 Vercel 계정을 사용할 수 있나요?

**A:** 네, 다른 이름으로 MCP 서버를 여러 개 설정:
```json
{
  "mcpServers": {
    "vercel-personal": { "env": { "VERCEL_API_TOKEN": "token1" } },
    "vercel-work": { "env": { "VERCEL_API_TOKEN": "token2" } }
  }
}
```
