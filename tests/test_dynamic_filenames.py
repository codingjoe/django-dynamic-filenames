import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

from dynamic_filenames import FilePattern
from tests.testapp.models import DefaultModel


class FixedUUIDFilePattern(FilePattern):

    @staticmethod
    def get_uuid():
        return uuid.UUID('522d6f3519204b0fb82ae8f558af2749')


class TestFilePattern:

    def test_init(self):
        assert FilePattern().kwargs == {}
        assert FilePattern().override_values == {}

        assert FilePattern(slug_from='title').kwargs == {'slug_from': 'title'}
        assert FilePattern(slug_from='title').override_values == {}

        assert FilePattern(slug_from='title').kwargs == {'slug_from': 'title'}
        assert FilePattern(slug_from='title').override_values == {}

        assert FilePattern(path='sth').kwargs == {'path': 'sth'}
        assert FilePattern(path='sth').override_values == {'path': 'sth'}

    def test_call__default(self):
        assert FilePattern()(instance=DefaultModel(), filename='test_file.txt') == 'test_file.txt'

    def test_call__no_extension(self):
        assert FilePattern()(instance=DefaultModel(), filename='test_file') == 'test_file'

    def test_call__only_extension(self):
        assert FilePattern()(instance=DefaultModel(), filename='.htaccess') == '.htaccess'

    def test_call__dot_file(self):
        assert FilePattern()(
            instance=DefaultModel(), filename='.hidden-truth.txt'
        ) == '.hidden-truth.txt'

    def test_call__full_path(self):
        assert FilePattern()(
            instance=DefaultModel(), filename='/var/www/index.html'
        ) == 'index.html'

    def test_call__override_pattern(self):
        assert FilePattern(filename_pattern='my_file{ext}')(
            instance=DefaultModel(), filename='other_file.txt'
        ) == 'my_file.txt'

    def test_call__uuid_base10(self):
        assert FixedUUIDFilePattern(filename_pattern='{uuid_base10}{ext}')(
            instance=DefaultModel(), filename='other_file.txt'
        ) == '109232604567331952752042348453722793801.txt'

    def test_call__uuid_base16(self):
        assert FixedUUIDFilePattern(filename_pattern='{uuid_base16}{ext}')(
            instance=DefaultModel(), filename='other_file.txt'
        ) == '522d6f3519204b0fb82ae8f558af2749.txt'

    def test_call__uuid_base32(self):
        assert FixedUUIDFilePattern(filename_pattern='{uuid_base32}{ext}')(
            instance=DefaultModel(), filename='other_file.txt'
        ) == 'KIWW6NIZEBFQ7OBK5D2VRLZHJE.txt'

    def test_call__uuid_base64(self):
        assert FixedUUIDFilePattern(filename_pattern='{uuid_base64}{ext}')(
            instance=DefaultModel(), filename='other_file.txt'
        ) == 'Ui1vNRkgSw-4Kuj1WK8nSQ.txt'

    def test_call__app_label(self):
        assert FilePattern(filename_pattern='{app_label}/{name}{ext}')(
            instance=DefaultModel(), filename='some_file.txt'
        ) == 'testapp/some_file.txt'

    def test_call__model_name(self):
        assert FilePattern(filename_pattern='{model_name}/{name}{ext}')(
            instance=DefaultModel(), filename='some_file.txt'
        ) == 'defaultmodel/some_file.txt'

    def test_call__name_override(self):
        assert FilePattern(name='special_name')(
            instance=DefaultModel(), filename='some_file.txt'
        ) == 'special_name.txt'

    def test_call__slug(self):
        assert FilePattern(slug_from='title', filename_pattern='{slug}{ext}')(
            instance=DefaultModel(title='best model'), filename='some_file.txt'
        ) == 'best-model.txt'

    def test_destruct(self):
        assert FilePattern().deconstruct() == ('dynamic_filenames.FilePattern', [], {})
        assert FilePattern(slug_from='title').deconstruct() == (
            'dynamic_filenames.FilePattern', [], {'slug_from': 'title'})
        assert FilePattern(name='sth').deconstruct() == (
            'dynamic_filenames.FilePattern', [], {'name': 'sth'})

    def test_uuid(self):
        assert isinstance(FilePattern.get_uuid(), uuid.UUID), "type uuid.UUID expected"
        assert FilePattern.get_uuid().hex[12] == '4', "UUID version 4 expected"

    def test_uuid_2_base10(self):
        guid = uuid.UUID('522d6f3519204b0fb82ae8f558af2749')
        assert isinstance(FilePattern.uuid_2_base10(guid), int)
        assert len(str(FilePattern.uuid_2_base10(guid))) == 39
        assert FilePattern.uuid_2_base10(guid) == 109232604567331952752042348453722793801

    def test_uuid_2_base16(self):
        guid = uuid.UUID('522d6f3519204b0fb82ae8f558af2749')
        assert isinstance(FilePattern.uuid_2_base16(guid), str)
        assert len(str(FilePattern.uuid_2_base16(guid))) == 32
        assert FilePattern.uuid_2_base16(guid) == '522d6f3519204b0fb82ae8f558af2749'

    def test_uuid_2_base32(self):
        guid = uuid.UUID('522d6f3519204b0fb82ae8f558af2749')
        assert isinstance(FilePattern.uuid_2_base32(guid), str)
        assert len(str(FilePattern.uuid_2_base32(guid))) == 26
        assert FilePattern.uuid_2_base32(guid) == 'KIWW6NIZEBFQ7OBK5D2VRLZHJE'

    def test_uuid_2_base64(self):
        guid = uuid.UUID('522d6f3519204b0fb82ae8f558af2749')
        assert isinstance(FilePattern.uuid_2_base64(guid), str)
        assert len(str(FilePattern.uuid_2_base64(guid))) == 22
        assert '=' not in FilePattern.uuid_2_base64(guid), "Trim padding"
        assert FilePattern.uuid_2_base64(guid) == 'Ui1vNRkgSw-4Kuj1WK8nSQ'


def test_migrations(db):
    """Integration tests for deconstruct method."""
    call_command('makemigrations', 'testapp', '--no-input')


def test_call(db):
    obj = DefaultModel.objects.create(
        title='hello world',
        file_field=SimpleUploadedFile(name='sample.txt', content=b'hello world')
    )

    assert obj.file_field.name == 'hello-world.txt'
