from src.agent.agent import (
    kwargs_from_blob,
    normalize_arg_tokens,
    parse_action,
    parse_final_answer,
    split_csv_args,
)


def test_split_csv_args_basic():
    assert split_csv_args('1, "Hanoi"') == ['1', '"Hanoi"']
    assert split_csv_args("a, b") == ["a", "b"]


def test_normalize_args():
    assert normalize_arg_tokens(['1', '"Hanoi"']) == [1, "Hanoi"]
    assert normalize_arg_tokens(["0.8", "'HCm'"]) == [0.8, "HCm"]


def test_parse_action():
    text = 'Thought: x\nAction: check_stock("iPhone")\n'
    assert parse_action(text) == ("check_stock", '"iPhone"')


def test_parse_final_answer():
    text = "Thought: done\nFinal Answer: $42.00\n"
    assert parse_final_answer(text) == "$42.00"


def test_kwargs_from_blob_json():
    d = kwargs_from_blob('{"city": "Da Lat", "max_price": 800000}')
    assert d["city"] == "Da Lat"
    assert d["max_price"] == 800000


def test_kwargs_from_blob_key_value():
    d = kwargs_from_blob('city="Da Lat", max_price=800000')
    assert d["city"] == "Da Lat"
    assert d["max_price"] == 800000
