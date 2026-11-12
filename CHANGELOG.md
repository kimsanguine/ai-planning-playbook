# 변경 이력

## 2026-11-12

- 다섯 문서(customer, prd, architecture, design, progress)를 함께 읽고 갱신하는 `ai-project-planning` Agent Skill을 추가했습니다.
- 스킬 설치 안내와 수동 설치 경로를 README에 추가하고, 전체 키트 ZIP 다운로드 안내를 제거했습니다.
- `npx skills add`로 Codex 프로젝트 스킬을 복사 설치하는 실제 명령과 GitHub CLI 2.90.0 이상용 설치·미리보기 경로를 확인했습니다. 새 프로젝트의 다섯 문서는 `docs/`에 둡니다.
- 기존 cases와 examples는 비교용 자료로 유지했으며, 다섯 번째 설계 문서 템플릿과 스킬 자산 검사를 추가했습니다.

## 2026-11-10

- 한국어 핸드북 28쪽과 입력 양식, 채운 실행예 10쌍을 공개 키트로 구성했습니다.
- customer, prd, architecture, progress의 네 템플릿, 영상 현지화 연습 예시, 세 사례를 포함했습니다.
- Habix의 웹 경로와 PDF 경로, GitHub의 파일 경로에 맞춰 링크를 연결했습니다.
- 포함된 폰트로 PDF와 웹용 JSON을 생성하고 바이트 해시를 기록하는 빌드를 추가했습니다.
- 원문 보존, 상대 링크, 개인정보 패턴, 생성물을 검사하는 로컬 명령과 CI를 추가했습니다.
