# naverzine.co.kr 배포 확인

## 현재 상태 (자동 점검 기준)

1. **GitHub Actions** — `Deploy static site` 워크플로는 **GitHub Pages가 켜지지 않아** `deploy-pages` 단계에서 실패한 적이 있습니다.  
   → [Settings → Pages](https://github.com/inchowon58-beep/pumshelter/settings/pages) 에서 한 번 설정이 필요합니다.

2. **도메인 DNS** — `www.naverzine.co.kr` 이 Cloudflare IP로 연결되어 있고, 응답이 `NOT_FOUND`(Vercel 계열)로 나오면 **GitHub Pages와 연결되지 않은 상태**입니다.

## 권장: gh-pages 브랜치로 배포

1. GitHub 저장소 **Settings → Pages**
2. **Build and deployment → Source**: `Deploy from a branch`
3. **Branch**: `gh-pages` / **Folder**: `/ (root)` → Save
4. **Actions** 탭에서 `Publish site to gh-pages branch` 가 **초록색(성공)** 인지 확인
5. 잠시 후 접속 테스트:
   - `https://inchowon58-beep.github.io/pumshelter/` (저장소 Pages URL — Settings에 표시됨)
6. **Custom domain**에 `www.naverzine.co.kr` 입력 후 GitHub가 안내하는 DNS 확인

## DNS (GitHub Pages + www)

- **www** CNAME → `inchowon58-beep.github.io` (Cloudflare 사용 시 처음엔 **DNS only(회색 구름)** 권장)
- 루트(`naverzine.co.kr`)는 호스팅 업체 안내대로 A 레코드 또는 www로 리다이렉트

Vercel·다른 호스팅에 같은 도메인이 연결돼 있으면 **해당 프로젝트 연결을 끊거나** DNS를 GitHub 쪽으로 바꿔야 합니다.

## Actions 방식(선택)

Pages Source를 **GitHub Actions**로 두려면 Settings → Pages에서 Source를 `GitHub Actions`로 저장한 뒤, `Deploy static site` 워크플로를 **Re-run** 하세요.

## 로컬 확인

```powershell
cd site
python -m http.server 8891 --bind 127.0.0.1
```

브라우저: http://127.0.0.1:8891
