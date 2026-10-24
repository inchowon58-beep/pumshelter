# naverzine.co.kr 배포 (Vercel)

`www.naverzine.co.kr` 응답 헤더에 **`x-vercel-error`** 가 보이면, 도메인은 **Vercel**에 연결된 상태입니다.  
예전처럼 **GitHub에 push만** 하면 되려면, Vercel 프로젝트가 **이 저장소(`pumshelter`)** 와 연결돼 있어야 합니다. GitHub Pages 설정과는 별개입니다.

## 저장소 설정

루트의 `vercel.json` 이 **빌드 결과 폴더를 `site/`** 로 지정합니다. (HTML은 `site/` 아래에 생성됨)

## Vercel에서 확인 (GitHub 설정 건드리지 않아도 됨)

1. [Vercel Dashboard](https://vercel.com/dashboard) 로그인
2. **naverzine** (또는 이 도메인이 붙어 있던) 프로젝트 선택
3. **Settings → Git**  
   - Repository가 `inchowon58-beep/pumshelter` 인지 확인  
   - 다른 저장소면 **Connect Git Repository** 로 `pumshelter` 로 바꾸거나, 새 프로젝트로 이 repo import
4. **Deployments** 탭  
   - 최근 배포가 **Failed** 이면 로그 확인 (용량·경로 오류 등)
5. 실패 시 **Redeploy** 또는 `main`에 push 한 번 더 (자동 배포)

## 도메인

- **Settings → Domains** 에 `www.naverzine.co.kr` (및 필요 시 apex) 이 **이 프로젝트**에 붙어 있는지 확인
- DNS는 Cloudflare → Vercel 구조로 두셔도 됩니다 (지금과 동일)

## GitHub Pages (선택)

Vercel을 쓰지 않고 Pages만 쓸 때만 [Settings → Pages](https://github.com/inchowon58-beep/pumshelter/settings/pages) 에서 `gh-pages` 브랜치 / root 를 켭니다.

## 로컬

```powershell
cd site
python -m http.server 8891 --bind 127.0.0.1
```

http://127.0.0.1:8891
