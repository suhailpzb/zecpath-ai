from ats_engine.ats_scoring import calculate_score

def test_score():
    result = calculate_score(8, 2)
    assert result == 82
