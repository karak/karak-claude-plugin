import classify

GB = 1024 ** 3
NOW = 1_800_000_000.0


def sample_rows():
    return [
        {"id": "a", "title_ja": "npm の npx キャッシュ", "class": "CHEAP", "section": "propose",
         "bytes": 2 * GB, "confidence": 0.85, "priority": 1.1, "admin": False, "blocked": None,
         "method_label": "ごみ箱を経由せず完全削除", "evidence": ["最終更新 40日前"], "regen_ja": "再取得"},
        {"id": "b", "title_ja": "Claude デスクトップの VM", "class": "DECISION", "section": "decision",
         "bytes": 8 * GB, "confidence": 0, "priority": 0, "admin": False, "blocked": None,
         "method_label": "助言のみ", "evidence": ["使用中の印あり"], "regen_ja": "再ダウンロード"},
        {"id": "c", "title_ja": "ページファイル", "class": "ADVICE", "section": "advice",
         "bytes": 21 * GB, "confidence": 0, "priority": 0, "admin": True, "blocked": None,
         "method_label": "助言のみ", "evidence": ["自動管理"], "regen_ja": "-"},
    ]


def scan_meta(age_hours=0):
    return {"scanned_at": NOW - age_hours * 3600, "disk": {"free": 17 * GB, "total": 236 * GB}}


def test_report_is_in_japanese_with_proposal_decision_and_advice_sections():
    text = classify.render_report(sample_rows(), scan_meta(), now=NOW)

    for heading in ("提案", "判断が必要", "助言のみ"):
        assert heading in text
    assert "npm の npx キャッシュ" in text


def test_report_states_free_space_and_proposed_total_in_gigabytes():
    text = classify.render_report(sample_rows(), scan_meta(), now=NOW)

    assert "17.0 GB" in text and "236.0 GB" in text
    assert "2.0 GB" in text


def test_report_shows_how_each_item_would_be_removed():
    text = classify.render_report(sample_rows(), scan_meta(), now=NOW)

    assert "方法" in text
    assert "ごみ箱を経由せず完全削除" in text


def test_report_warns_when_the_scan_is_older_than_a_day():
    fresh = classify.render_report(sample_rows(), scan_meta(age_hours=1), now=NOW)
    stale = classify.render_report(sample_rows(), scan_meta(age_hours=30), now=NOW)

    assert "古い" not in fresh
    assert "古い" in stale
