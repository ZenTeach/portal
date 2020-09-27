import pytest
# from server.lib import LocalImageStore
from werkzeug.datastructures import FileStorage


@pytest.fixture
def mock_file_storage():
    return FileStorage(name='Test File', )


def mock_global_config():
    return {
        'UPLOAD_FOLDER': ''
    }


def test_local_image_store_save(client, mocker):
    # @mocker.patch('server.lib.local_file_store.globalConfig', mock_global_config)
    # @mocker.object(FileStorage, 'save')
    pass
