'''
Test suite for judge.py
'''
import json
import os

import pytest

import judge


BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def test_dump_result(storage):
    '''
    Test judge._dump_data
    '''
    data = {
        3: [('db', 'db_003', None), ('db', 'db_003', 'User_Commit')],
    }
    filename = os.path.join(storage, 'test_dump_result.csv')
    judge._dump_data(data, filename)  # pylint: disable=protected-access
    with open(filename) as obj:
        lines = obj.read().strip().split('\n')
        # one row for header and two rows of answer
        assert len(lines) == 3


@pytest.mark.parametrize(('answer_path', 'result_path', 'expectation'), [
    (os.path.join(BASE_DIR, 'answer', 'answer-0411.json'),
     os.path.join(BASE_DIR, 'sample_result.csv'), 10.9),
    ('nonexistent_answer.json', 'nonexisstent_result.json', 0),
])
def test_judge(answer_path, result_path, expectation):
    '''Test judge.judge'''
    ret = judge.judge(answer_path, result_path, grade_gradient=(100, 20))
    assert ret['data'] == pytest.approx(expectation, 0.1), ret['message']


def test_function(capsys):
    '''
    Test judge.main

    Sample data is supposed to be created with insufficient arguments.
    Judging the created sample data is supposed to get a grade of 30.
    '''
    cmd = 'judge.py'
    iters = 2  # Verify idempotence

    for _ in range(iters):
        # Create sample data
        answer_path, result_path, action = judge.main([cmd, ])
        assert action == 'demo'
        _ = capsys.readouterr()
        # Judge with created data
        _, _, action = judge.main([cmd, answer_path, result_path])
        assert action == 'judge'
        captured = capsys.readouterr()
        ret = json.loads(captured.out)
        assert ret['data'] == pytest.approx(0.3, 1e-4), ret['message']

    result_path = 'result.json'
    judge._demo(answer_path, result_path)  # pylint: disable=protected-access
    _ = capsys.readouterr()
    # Judge with created data
    _, _, action = judge.main([cmd, answer_path, result_path])
    assert action == 'judge'
    captured = capsys.readouterr()
    ret = json.loads(captured.out)
    assert ret['data'] == pytest.approx(0.3, 1e-4), ret['message']
