from ats_engine.ats_scoring import calculate_score

def test_score():
    result = calculate_score(3, 5, "bachelor")
    assert result > 0
    assert result <= 100
