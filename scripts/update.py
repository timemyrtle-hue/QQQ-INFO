#!/usr/bin/env python3
"""QQQ 일별 종가를 Alpha Vantage에서 받아 site/data.json에 추가한다.

- API 키는 환경 변수 AV_API_KEY에서만 읽는다(코드나 로그에 남기지 않는다).
- data.json의 lastDate보다 새로운 거래일만 closes에 추가한다.
- 새 거래일이 없어도(휴장일 등) updatedAt은 확인한 시각으로 갱신한다.
- 응답이 비정상이면 오류로 종료한다. GitHub Actions에서 실행이 실패로 표시된다.

개발용: AV_RESPONSE_FILE에 응답 JSON 파일 경로를 주면 네트워크 호출 없이 그 파일을 쓴다.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYMBOL = "QQQ"
DATA_PATH = Path(__file__).resolve().parent.parent / "site" / "data.json"


def fetch_daily():
    fake = os.environ.get("AV_RESPONSE_FILE")
    if fake:
        return json.loads(Path(fake).read_text(encoding="utf-8"))

    key = os.environ.get("AV_API_KEY", "").strip()
    if not key:
        sys.exit("AV_API_KEY가 설정되어 있지 않습니다. 저장소 Settings > Secrets에 등록하세요.")
    query = urllib.parse.urlencode({
        "function": "TIME_SERIES_DAILY",
        "symbol": SYMBOL,
        "outputsize": "compact",
        "datatype": "json",
        "apikey": key,
    })
    url = "https://www.alphavantage.co/query?" + query
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    payload = fetch_daily()
    series = payload.get("Time Series (Daily)")
    if not isinstance(series, dict) or not series:
        # 호출 한도 초과나 키 오류일 때 안내 문구가 들어온다. 키는 출력하지 않는다.
        note = payload.get("Information") or payload.get("Note") or payload.get("Error Message") or "알 수 없는 응답"
        sys.exit("시세를 받지 못했습니다: " + str(note)[:300])

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    closes = data.setdefault("closes", {})
    last_date = data.get("lastDate") or max(closes)

    added = []
    for day in sorted(series):
        if day <= last_date:
            continue
        try:
            close = round(float(series[day]["4. close"]), 4)
        except (KeyError, ValueError, TypeError):
            sys.exit("종가를 읽을 수 없는 날짜가 있습니다: " + day)
        closes[day] = close
        added.append((day, close))

    if closes:
        data["lastDate"] = max(closes)
    data["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    DATA_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if added:
        print("추가된 거래일:", ", ".join(f"{d} {c}" for d, c in added))
    else:
        print("새 거래일이 없습니다. 마지막 거래일:", data["lastDate"])


if __name__ == "__main__":
    main()
