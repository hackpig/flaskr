import pytest

import os
import flaskr
import tempfile

@pytest.fixture
def client(request):
    db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    flaskr.app.config['TESTING'] = True
    client = flaskr.app.test_client()
    with flaskr.app.app_context():
        flaskr.init_db()

    def teardown():
        os.close(db_fd)
        os.unlink(flaskr.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client

def login(client,username,password):
    return client.post('/login',data=dict(
        username=username,
        password=password
    ),follow_redirects=True)

def logout(client):
    return client.get('/logout',follow_redirects=True)

def test_empty_db(client):
    rv = client.get('/')
    assert b'No entries here so far' in rv.data

def test_login_logout(client):
    rv = login(client,flaskr.app.config['USERNAME'],
            flaskr.app.config['PASSWORD'])
    assert b'You were logged in' in rv.data
    rv = logout(client)
    assert b'You were logged out' in rv.data

def test_message(client):
    login(client,flaskr.app.config['USERNAME'],flaskr.app.config['PASSWORD'])
    rv = client.post('/add',data=dict(title='<hello>',text='<strong>HTML</strong> allowed here'),follow_redirects=True)
    assert b'No entries here so far' not in rv.data
    assert b'hello' in rv.data

