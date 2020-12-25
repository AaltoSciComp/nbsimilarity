# TODO: absolute import
from . import util


def test_reversed_string():
    assert util.reversed_string('abc') == 'cba'

def test_common_prefix_length():
    common_prefix_length = util.common_prefix_length
    assert common_prefix_length(['abc123', 'abcd123']) == 3
    assert common_prefix_length(['', 'abcd123']) == 0
    assert common_prefix_length(['', '']) == 0
    assert common_prefix_length(['abc', 'abc']) == 3
    assert common_prefix_length(['abc', 'abcd']) == 3
    assert common_prefix_length(['abcd', 'abc']) == 3
    assert common_prefix_length(['abcd', '']) == 0

def test_remove_common_parts():
    remove_common_parts = util.remove_common_parts
    assert remove_common_parts(('ab123cd', 'ab555cd')) == ('123', '555')
    assert remove_common_parts(('', '555')) == ('', '555')
    assert remove_common_parts(('123', '')) == ('123', '')
    assert remove_common_parts(('ab123', 'ab555')) == ('123', '555')
    assert remove_common_parts(('ab123', '555cd')) == ('ab123', '555cd')
    assert remove_common_parts(('', '')) == ('', '')
    assert remove_common_parts(('abcd', 'abcd')) == ('', '')
    assert remove_common_parts(('abbc', 'abc')) == ('b', '')
    assert remove_common_parts(('abc', 'abbc')) == ('', 'b')
