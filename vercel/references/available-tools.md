# Vercel MCP 사용 가능한 도구

MCP 서버가 제공하는 모든 도구와 사용법입니다.

---

## 배포 관리 (Deployments)

### vercel-list-all-deployments

모든 배포 목록을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `limit` | number | ❌ | 결과 개수 제한 (기본: 20) |
| `projectId` | string | ❌ | 특정 프로젝트만 필터링 |
| `target` | string | ❌ | 환경 필터 (production, preview) |
| `state` | string | ❌ | 상태 필터 (READY, ERROR, BUILDING) |

**사용 예시:**
```
"최근 10개 배포 목록 보여줘"
"production 배포만 보여줘"
"에러 상태인 배포 찾아줘"
```

---

### vercel-get-deployment

특정 배포의 상세 정보를 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `deploymentId` | string | ✅ | 배포 ID 또는 URL |

**사용 예시:**
```
"dpl_xxxxx 배포 상세 정보 보여줘"
"https://my-app-xxxxx.vercel.app 배포 정보 확인해줘"
```

---

### vercel-create-deployment

새로운 배포를 생성합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID |
| `target` | string | ❌ | 배포 환경 (production, preview) |
| `gitSource` | object | ❌ | Git 소스 정보 |

**gitSource 구조:**
```json
{
  "type": "github",
  "ref": "main",
  "repoId": "123456789"
}
```

**사용 예시:**
```
"my-project를 production에 배포해줘"
"main 브랜치로 새 배포 생성해줘"
```

---

### vercel-get-deployment-files

배포에 포함된 파일 목록을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `deploymentId` | string | ✅ | 배포 ID |

**사용 예시:**
```
"이 배포에 어떤 파일들이 포함되어 있어?"
```

---

## 프로젝트 관리 (Projects)

### vercel-create-project

새 Vercel 프로젝트를 생성합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `name` | string | ✅ | 프로젝트 이름 |
| `framework` | string | ❌ | 프레임워크 (nextjs, vite, etc.) |
| `teamId` | string | ❌ | 팀 ID |
| `gitRepository` | object | ❌ | Git 저장소 연결 정보 |

**지원 프레임워크:**
- `nextjs`, `gatsby`, `remix`
- `vite`, `create-react-app`
- `nuxtjs`, `vue`
- `svelte`, `sveltekit`
- `astro`, `eleventy`
- `hugo`, `jekyll`

**사용 예시:**
```
"my-new-app이라는 Next.js 프로젝트 만들어줘"
"Vite 프로젝트를 팀에 생성해줘"
```

---

### vercel-list-projects

모든 프로젝트 목록을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `limit` | number | ❌ | 결과 개수 제한 |
| `from` | number | ❌ | 페이지네이션 시작점 |
| `search` | string | ❌ | 프로젝트 이름 검색 |

**사용 예시:**
```
"내 Vercel 프로젝트 목록 보여줘"
"'dashboard' 이름이 포함된 프로젝트 찾아줘"
```

---

### vercel-get-project

특정 프로젝트의 상세 정보를 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID 또는 이름 |

**사용 예시:**
```
"my-app 프로젝트 정보 보여줘"
```

---

### vercel-get-project-domains

프로젝트에 연결된 도메인 목록을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID |

**사용 예시:**
```
"이 프로젝트에 연결된 도메인 보여줘"
```

---

## 환경 변수 (Environment Variables)

### vercel-get-environments

프로젝트의 환경 변수를 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID |
| `target` | string | ❌ | 환경 (production, preview, development) |

**사용 예시:**
```
"my-app의 환경 변수 보여줘"
"production 환경 변수만 보여줘"
```

---

### vercel-create-environment-variables

환경 변수를 생성합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID |
| `key` | string | ✅ | 변수 이름 |
| `value` | string | ✅ | 변수 값 |
| `target` | array | ❌ | 적용 환경 목록 |
| `type` | string | ❌ | 타입 (plain, secret, encrypted) |

**target 옵션:**
- `["production"]` - 프로덕션만
- `["preview"]` - 프리뷰만
- `["development"]` - 개발만
- `["production", "preview"]` - 복수 환경

**사용 예시:**
```
"DATABASE_URL을 production 환경에 추가해줘"
"API_KEY를 모든 환경에 secret으로 추가해줘"
```

---

### vercel-delete-environment-variable

환경 변수를 삭제합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `projectId` | string | ✅ | 프로젝트 ID |
| `envId` | string | ✅ | 환경 변수 ID |

**사용 예시:**
```
"OLD_API_KEY 환경 변수 삭제해줘"
```

---

## 팀 관리 (Teams)

### vercel-list-all-teams

접근 가능한 모든 팀 목록을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `limit` | number | ❌ | 결과 개수 제한 |

**사용 예시:**
```
"내가 속한 Vercel 팀 목록 보여줘"
```

---

### vercel-create-team

새 팀을 생성합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `slug` | string | ✅ | 팀 URL 슬러그 |
| `name` | string | ❌ | 팀 표시 이름 |

**사용 예시:**
```
"my-company 팀 만들어줘"
```

---

## 도메인 관리 (Domains)

### vercel-list-domains

계정의 모든 도메인을 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `limit` | number | ❌ | 결과 개수 제한 |

**사용 예시:**
```
"내 Vercel 도메인 목록 보여줘"
```

---

### vercel-get-domain

특정 도메인의 상세 정보를 조회합니다.

**파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `domain` | string | ✅ | 도메인 이름 |

**사용 예시:**
```
"example.com 도메인 정보 확인해줘"
```

---

## 자연어 사용 예시 모음

### 배포 관련
```
"현재 빌드 중인 배포가 있어?"
"오늘 production에 배포된 것들 보여줘"
"마지막 배포가 왜 실패했는지 확인해줘"
"이전 버전으로 롤백할 수 있어?"
```

### 프로젝트 관련
```
"새로운 Next.js 프로젝트 생성해줘"
"dashboard 프로젝트의 프레임워크가 뭐야?"
"이 프로젝트에 연결된 Git 저장소 정보 보여줘"
```

### 환경 변수 관련
```
"production에 STRIPE_SECRET_KEY 추가해줘"
"preview 환경의 DATABASE_URL 변경해줘"
"현재 설정된 환경 변수 중 비어있는 거 있어?"
```

### 팀 관련
```
"우리 팀의 모든 프로젝트 보여줘"
"새 팀 만들어서 이 프로젝트 이동시켜줘"
```
