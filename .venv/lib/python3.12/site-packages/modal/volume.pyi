import asyncio.locks
import enum
import modal._utils.blob_utils
import modal.client
import modal.object
import modal_proto.api_pb2
import pathlib
import synchronicity.combined_types
import typing
import typing_extensions

class FileEntryType(enum.IntEnum):
    """Type of a file entry listed from a Modal volume."""

    UNSPECIFIED = 0
    FILE = 1
    DIRECTORY = 2
    SYMLINK = 3


class FileEntry:
    path: str
    type: FileEntryType
    mtime: int
    size: int

    @classmethod
    def _from_proto(cls, proto: modal_proto.api_pb2.FileEntry) -> FileEntry:
        ...

    def __getattr__(self, name: str):
        ...

    def __init__(self, path: str, type: FileEntryType, mtime: int, size: int) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...

    def __setattr__(self, name, value):
        ...

    def __delattr__(self, name):
        ...

    def __hash__(self):
        ...


class _Volume(modal.object._Object):
    _lock: asyncio.locks.Lock

    def _initialize_from_empty(self):
        ...

    @staticmethod
    def new() -> _Volume:
        ...

    @staticmethod
    def from_name(label: str, namespace=1, environment_name: typing.Union[str, None] = None, create_if_missing: bool = False) -> _Volume:
        ...

    @classmethod
    def ephemeral(cls: typing.Type[_Volume], client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None, _heartbeat_sleep: float = 300) -> typing.AsyncContextManager[_Volume]:
        ...

    @staticmethod
    def persisted(label: str, namespace=1, environment_name: typing.Union[str, None] = None, cloud: typing.Union[str, None] = None) -> _Volume:
        ...

    @staticmethod
    async def lookup(label: str, namespace=1, client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None, create_if_missing: bool = False) -> _Volume:
        ...

    @staticmethod
    async def create_deployed(deployment_name: str, namespace=1, client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None) -> str:
        ...

    async def _do_reload(self, lock=True):
        ...

    async def commit(self):
        ...

    async def reload(self):
        ...

    def iterdir(self, path: str) -> typing.AsyncIterator[FileEntry]:
        ...

    async def listdir(self, path: str) -> typing.List[FileEntry]:
        ...

    def read_file(self, path: typing.Union[str, bytes]) -> typing.AsyncIterator[bytes]:
        ...

    async def read_file_into_fileobj(self, path: typing.Union[str, bytes], fileobj: typing.IO[bytes], progress: bool = False) -> int:
        ...

    async def remove_file(self, path: typing.Union[str, bytes], recursive: bool = False) -> None:
        ...

    async def copy_files(self, src_paths: typing.Sequence[typing.Union[str, bytes]], dst_path: typing.Union[str, bytes]) -> None:
        ...

    async def batch_upload(self, force: bool = False) -> _VolumeUploadContextManager:
        ...

    async def delete(self):
        ...


class _VolumeUploadContextManager:
    _volume_id: str
    _client: modal.client._Client
    _force: bool
    _upload_generators: typing.List[typing.Generator[typing.Callable[[], modal._utils.blob_utils.FileUploadSpec], None, None]]

    def __init__(self, volume_id: str, client: modal.client._Client, force: bool = False):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    def put_file(self, local_file: typing.Union[pathlib.Path, str, typing.BinaryIO], remote_path: typing.Union[pathlib.PurePosixPath, str], mode: typing.Union[int, None] = None):
        ...

    def put_directory(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[pathlib.PurePosixPath, str], recursive: bool = True):
        ...

    async def _upload_file(self, file_spec: modal._utils.blob_utils.FileUploadSpec) -> modal_proto.api_pb2.MountFile:
        ...


class Volume(modal.object.Object):
    _lock: asyncio.locks.Lock

    def __init__(self, *args, **kwargs):
        ...

    def _initialize_from_empty(self):
        ...

    @staticmethod
    def new() -> Volume:
        ...

    @staticmethod
    def from_name(label: str, namespace=1, environment_name: typing.Union[str, None] = None, create_if_missing: bool = False) -> Volume:
        ...

    @classmethod
    def ephemeral(cls: typing.Type[Volume], client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None, _heartbeat_sleep: float = 300) -> synchronicity.combined_types.AsyncAndBlockingContextManager[Volume]:
        ...

    @staticmethod
    def persisted(label: str, namespace=1, environment_name: typing.Union[str, None] = None, cloud: typing.Union[str, None] = None) -> Volume:
        ...

    class __lookup_spec(typing_extensions.Protocol):
        def __call__(self, label: str, namespace=1, client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None, create_if_missing: bool = False) -> Volume:
            ...

        async def aio(self, *args, **kwargs) -> Volume:
            ...

    lookup: __lookup_spec

    class __create_deployed_spec(typing_extensions.Protocol):
        def __call__(self, deployment_name: str, namespace=1, client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None) -> str:
            ...

        async def aio(self, *args, **kwargs) -> str:
            ...

    create_deployed: __create_deployed_spec

    class ___do_reload_spec(typing_extensions.Protocol):
        def __call__(self, lock=True):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _do_reload: ___do_reload_spec

    class __commit_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    commit: __commit_spec

    class __reload_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    reload: __reload_spec

    class __iterdir_spec(typing_extensions.Protocol):
        def __call__(self, path: str) -> typing.Iterator[FileEntry]:
            ...

        def aio(self, path: str) -> typing.AsyncIterator[FileEntry]:
            ...

    iterdir: __iterdir_spec

    class __listdir_spec(typing_extensions.Protocol):
        def __call__(self, path: str) -> typing.List[FileEntry]:
            ...

        async def aio(self, *args, **kwargs) -> typing.List[FileEntry]:
            ...

    listdir: __listdir_spec

    class __read_file_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes]) -> typing.Iterator[bytes]:
            ...

        def aio(self, path: typing.Union[str, bytes]) -> typing.AsyncIterator[bytes]:
            ...

    read_file: __read_file_spec

    class __read_file_into_fileobj_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes], fileobj: typing.IO[bytes], progress: bool = False) -> int:
            ...

        async def aio(self, *args, **kwargs) -> int:
            ...

    read_file_into_fileobj: __read_file_into_fileobj_spec

    class __remove_file_spec(typing_extensions.Protocol):
        def __call__(self, path: typing.Union[str, bytes], recursive: bool = False) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    remove_file: __remove_file_spec

    class __copy_files_spec(typing_extensions.Protocol):
        def __call__(self, src_paths: typing.Sequence[typing.Union[str, bytes]], dst_path: typing.Union[str, bytes]) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    copy_files: __copy_files_spec

    class __batch_upload_spec(typing_extensions.Protocol):
        def __call__(self, force: bool = False) -> VolumeUploadContextManager:
            ...

        async def aio(self, *args, **kwargs) -> VolumeUploadContextManager:
            ...

    batch_upload: __batch_upload_spec

    class __delete_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    delete: __delete_spec


class VolumeUploadContextManager:
    _volume_id: str
    _client: modal.client.Client
    _force: bool
    _upload_generators: typing.List[typing.Generator[typing.Callable[[], modal._utils.blob_utils.FileUploadSpec], None, None]]

    def __init__(self, volume_id: str, client: modal.client.Client, force: bool = False):
        ...

    def __enter__(self):
        ...

    async def __aenter__(self, *args, **kwargs):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    async def __aexit__(self, *args, **kwargs):
        ...

    def put_file(self, local_file: typing.Union[pathlib.Path, str, typing.BinaryIO], remote_path: typing.Union[pathlib.PurePosixPath, str], mode: typing.Union[int, None] = None):
        ...

    def put_directory(self, local_path: typing.Union[pathlib.Path, str], remote_path: typing.Union[pathlib.PurePosixPath, str], recursive: bool = True):
        ...

    class ___upload_file_spec(typing_extensions.Protocol):
        def __call__(self, file_spec: modal._utils.blob_utils.FileUploadSpec) -> modal_proto.api_pb2.MountFile:
            ...

        async def aio(self, *args, **kwargs) -> modal_proto.api_pb2.MountFile:
            ...

    _upload_file: ___upload_file_spec


def _open_files_error_annotation(mount_path: str) -> typing.Union[str, None]:
    ...
