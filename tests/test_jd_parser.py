from parsers.jd_parser import parse_job_description


def test_jd_parser():

    with open("data/job_descriptions/portfolio_manager.txt") as f:
        jd_text = f.read()

    result = parse_job_description(jd_text)

    assert result["role"] != ""
    assert len(result["skills"]) > 0