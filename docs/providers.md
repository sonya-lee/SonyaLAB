# Data providers

## 상태

| 영역 | Provider | 상태 | 인증 |
|---|---|---|---|
| 항공권 | Mock | 실제 구현, 가상 가격 | 없음 |
| 항공권 | Duffel 후보 | 계약/adapter 필요 | access token |
| 항공권 | Skyscanner 후보 | 파트너 승인/adapter 필요 | API key |
| 항공권 | Amadeus 후보 | 계정·quota 확인/adapter 필요 | OAuth client |
| 논문 | Crossref | 실제 구현 | 공개, `mailto` 권장 |
| 논문 | OpenAlex | 향후 | 무료 API key 필요 |
| 논문 | Semantic Scholar | 향후 | 정책 확인 필요 |
| 논문 | Europe PMC | 향후 | 공개 범위 검토 |
| OA | Unpaywall | 향후 보강 | email 필요 |

## 항공권 후보 비교

Duffel 공식 API는 왕복 slice, 항공편/segment, 경유, 수하물, 변경·환불 조건과 offer 만료 시각을 제공합니다. 검색 offer는 보통 짧게 유효하고 최신 상태 재조회가 필요합니다. 공식 문서의 rate limit 예시는 60초당 60회지만 변경될 수 있으며 429 reset 헤더를 따라야 합니다. Sonya Lab은 직접 예약하지 않고 검증된 외부 링크가 있는 경우에만 연결합니다. 참고: [Offer requests](https://duffel.com/docs/api/offer-requests), [Offers and expiry](https://duffel.com/docs/api/offers/get-offers), [Rate limiting](https://duffel.com/docs/api/overview/response-handling).

Skyscanner Flights Live Prices는 실시간 파트너 재고 기반 검색이지만 파트너 API 접근 승인이 필요합니다. 지역, 한국 출발 커버리지, deep link, 상업/개인 사용 조건과 quota는 계약 시 확인해야 합니다. 참고: [Flights Live Prices quick start](https://developers.skyscanner.net/docs/flights-live-prices/quick-start).

Amadeus Self-Service/Enterprise는 Flight Offers Search 후보입니다. 정확한 무료 한도, 한국 노선, 수하물·deep link 범위가 계정/상품에 따라 달라 실제 계약 전 구현 완료로 표시하지 않습니다.

HTML 임의 scraping은 기본 provider로 사용하지 않습니다. `FLIGHT_PROVIDER=mock` 상태에서는 신뢰도 `mock`, 구매 링크 없음으로 표시합니다.

## 논문 필드 출처

Crossref: 서지정보, DOI, Crossref 피인용 수, 제공된 초록. OA 여부와 Impact Factor를 추정하지 않습니다. `metadata_sources_json`에 필드별 출처를 기록합니다. Provider 장애 시 빈 결과와 오류를 반환하며 가짜 논문을 실제처럼 표시하지 않습니다. 공개 API는 가입 없이 쓸 수 있고 `mailto` polite 방식이 권장됩니다. 참고: [Crossref access](https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/), [filters](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/).
