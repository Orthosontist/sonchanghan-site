# 글 관리

관리자 주소: https://drsonchanghan.com/admin/

상담 일기와 치료 증례 25편을 `content/articles/<게시글 ID>.json`에서 관리합니다.
제목, 핵심 요약, 소제목, 문단, 사진, 사진 설명, 연속 사진 묶음을 편집할 수 있습니다.
본문의 각 항목은 위아래로 순서를 바꿀 수 있습니다. 현재 새 글 생성과 삭제는 비활성화되어 있습니다.
네이버에서 새로 가져오는 글은 기존 동기화 작업에서 편집용 파일을 추가합니다.
편집용 파일이 있으면 네이버 동기화와 재빌드가 수동 수정 내용을 덮어쓰지 않습니다.

## 활성화 전에 필요한 로그인 연결

코드와 CMS 설정은 준비했지만 실제 OAuth 로그인 및 저장은 아직 검증하지 않았습니다.
ChatGPT의 GitHub 연결은 홈페이지의 OAuth 로그인 설정을 대신하지 않습니다.

1. GitHub Settings → Developer settings → OAuth Apps에서 앱을 등록합니다.
2. 홈페이지 URL: `https://drsonchanghan.com`.
3. Authorization callback URL: `https://api.netlify.com/auth/done`.
4. Netlify 프로젝트 → Project configuration → Access & security → OAuth에서 GitHub 제공자를 설치하고 Client ID와 Client Secret을 입력합니다.
5. 이 변경사항을 배포한 뒤 `/admin/`에서 저장소 쓰기 권한이 있는 본인 계정으로 로그인합니다.
6. 한 글의 초안을 저장하고 미리보기·발행·사이트 반영까지 검증해야 운영 준비가 완료됩니다.

Client Secret은 Netlify 설정에만 입력합니다. 소스코드나 채팅에 붙여넣지 않습니다.
GitHub 저장소 쓰기 권한이 없는 방문자는 공개 관리자 주소를 알아도 저장할 수 없습니다.

## 편집과 발행

`editorial_workflow`를 사용하므로 초안 저장과 실제 발행이 분리됩니다.
오른쪽 편집기 미리보기는 서버 배포 없이 문장과 사진의 배치를 확인하는 용도입니다.
초안 저장으로 만들어진 PR/브랜치가 Netlify Deploy Preview를 실행하는지는 계정의 배포 설정에 따릅니다.
크레딧 절약을 위해 반복 저장 전 편집기 미리보기로 충분히 검토하고, 자동 미리보기 배포 설정을 확인합니다.
발행 시 main에 반영되고 Netlify 빌드가 정적 HTML을 생성합니다.

사진은 `/images/` 아래 파일만 허용합니다. 기존 임상사진은 다시 압축하거나 가공하지 않습니다.
관리자는 검색 목록에서 제외하며 기존 글의 공개 URL은 유지합니다.

참고: https://decapcms.org/docs/github-backend/
참고: https://docs.netlify.com/manage/security/secure-access-to-sites/oauth-provider-tokens/

## 편집 확인 메모

앞니 공간·정중선 증례의 원문에는 치료 기간이 1년 3개월로 기재되어 있으나,
사진은 치료 전 2024.09, 치료 후 2026.01/2026.02로 표기되어 있습니다.
사진 자체와 원문의 기간은 임의로 변경하지 않았습니다. 게시 전 작성자에게 날짜 확인이 필요합니다.
