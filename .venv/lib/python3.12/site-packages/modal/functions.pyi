import google.protobuf.message
import modal._output
import modal._utils.async_utils
import modal._utils.function_utils
import modal.app
import modal.call_graph
import modal.client
import modal.cloud_bucket_mount
import modal.gpu
import modal.image
import modal.mount
import modal.network_file_system
import modal.object
import modal.parallel_map
import modal.proxy
import modal.retries
import modal.schedule
import modal.scheduler_placement
import modal.secret
import modal.volume
import modal_proto.api_grpc
import modal_proto.api_pb2
import pathlib
import typing
import typing_extensions

class _Invocation:
    def __init__(self, stub: modal_proto.api_grpc.ModalClientStub, function_call_id: str, client: modal.client._Client):
        ...

    @staticmethod
    async def create(function_id: str, args, kwargs, client: modal.client._Client) -> _Invocation:
        ...

    def pop_function_call_outputs(self, timeout: typing.Union[float, None], clear_on_success: bool) -> typing.AsyncIterator[modal_proto.api_pb2.FunctionGetOutputsItem]:
        ...

    async def run_function(self) -> typing.Any:
        ...

    async def poll_function(self, timeout: typing.Union[float, None] = None):
        ...

    def run_generator(self):
        ...


class FunctionStats:
    backlog: int
    num_active_runners: int
    num_total_runners: int

    def __init__(self, backlog: int, num_active_runners: int, num_total_runners: int) -> None:
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


def _parse_retries(retries: typing.Union[int, modal.retries.Retries, None], raw_f: typing.Union[typing.Callable, None] = None) -> typing.Union[modal_proto.api_pb2.FunctionRetryPolicy, None]:
    ...


class _FunctionSpec:
    image: typing.Union[modal.image._Image, None]
    mounts: typing.Sequence[modal.mount._Mount]
    secrets: typing.Sequence[modal.secret._Secret]
    network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system._NetworkFileSystem]
    volumes: typing.Dict[typing.Union[str, pathlib.PurePosixPath], typing.Union[modal.volume._Volume, modal.cloud_bucket_mount._CloudBucketMount]]
    gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig]
    cloud: typing.Union[str, None]
    cpu: typing.Union[float, None]
    memory: typing.Union[int, typing.Tuple[int, int], None]

    def __init__(self, image: typing.Union[modal.image._Image, None], mounts: typing.Sequence[modal.mount._Mount], secrets: typing.Sequence[modal.secret._Secret], network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system._NetworkFileSystem], volumes: typing.Dict[typing.Union[str, pathlib.PurePosixPath], typing.Union[modal.volume._Volume, modal.cloud_bucket_mount._CloudBucketMount]], gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig], cloud: typing.Union[str, None], cpu: typing.Union[float, None], memory: typing.Union[int, typing.Tuple[int, int], None]) -> None:
        ...

    def __repr__(self):
        ...

    def __eq__(self, other):
        ...


class _Function(modal.object._Object):
    _info: typing.Union[modal._utils.function_utils.FunctionInfo, None]
    _all_mounts: typing.Collection[modal.mount._Mount]
    _app: modal.app._App
    _obj: typing.Any
    _web_url: typing.Union[str, None]
    _is_remote_cls_method: bool
    _function_name: typing.Union[str, None]
    _is_method: bool
    _spec: _FunctionSpec
    _tag: str
    _raw_f: typing.Callable[..., typing.Any]
    _build_args: dict
    _parent: _Function

    @staticmethod
    def from_args(info: modal._utils.function_utils.FunctionInfo, app, image: modal.image._Image, secret: typing.Union[modal.secret._Secret, None] = None, secrets: typing.Sequence[modal.secret._Secret] = (), schedule: typing.Union[modal.schedule.Schedule, None] = None, is_generator=False, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, mounts: typing.Collection[modal.mount._Mount] = (), network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system._NetworkFileSystem] = {}, allow_cross_region_volumes: bool = False, volumes: typing.Dict[typing.Union[str, pathlib.PurePosixPath], typing.Union[modal.volume._Volume, modal.cloud_bucket_mount._CloudBucketMount]] = {}, webhook_config: typing.Union[modal_proto.api_pb2.WebhookConfig, None] = None, memory: typing.Union[int, typing.Tuple[int, int], None] = None, proxy: typing.Union[modal.proxy._Proxy, None] = None, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, cpu: typing.Union[float, None] = None, keep_warm: typing.Union[int, None] = None, cloud: typing.Union[str, None] = None, _experimental_boost: bool = False, _experimental_scheduler: bool = False, _experimental_scheduler_placement: typing.Union[modal.scheduler_placement.SchedulerPlacement, None] = None, is_builder_function: bool = False, is_auto_snapshot: bool = False, enable_memory_snapshot: bool = False, checkpointing_enabled: typing.Union[bool, None] = None, allow_background_volume_commits: bool = False, block_network: bool = False, max_inputs: typing.Union[int, None] = None) -> None:
        ...

    def from_parametrized(self, obj, from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args: typing.Sized, kwargs: typing.Dict[str, typing.Any]) -> _Function:
        ...

    async def keep_warm(self, warm_pool_size: int) -> None:
        ...

    @classmethod
    def from_name(cls: typing.Type[_Function], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None) -> _Function:
        ...

    @staticmethod
    async def lookup(app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client._Client, None] = None, environment_name: typing.Union[str, None] = None) -> _Function:
        ...

    @property
    def tag(self) -> str:
        ...

    @property
    def app(self) -> modal.app._App:
        ...

    @property
    def stub(self) -> modal.app._App:
        ...

    @property
    def info(self) -> modal._utils.function_utils.FunctionInfo:
        ...

    @property
    def spec(self) -> _FunctionSpec:
        ...

    def get_build_def(self) -> str:
        ...

    def _initialize_from_empty(self):
        ...

    def _hydrate_metadata(self, metadata: typing.Union[google.protobuf.message.Message, None]):
        ...

    def _get_metadata(self):
        ...

    def _set_mute_cancellation(self, value: bool = True):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    @property
    def web_url(self) -> str:
        ...

    @property
    def is_generator(self) -> bool:
        ...

    def _map(self, input_queue: modal.parallel_map._SynchronizedQueue, order_outputs: bool, return_exceptions: bool) -> typing.AsyncGenerator[typing.Any, None]:
        ...

    async def _call_function(self, args, kwargs):
        ...

    async def _call_function_nowait(self, args, kwargs) -> _Invocation:
        ...

    def _call_generator(self, args, kwargs):
        ...

    async def _call_generator_nowait(self, args, kwargs):
        ...

    async def remote(self, *args, **kwargs) -> typing.Any:
        ...

    def remote_gen(self, *args, **kwargs) -> typing.AsyncGenerator[typing.Any, None]:
        ...

    async def shell(self, *args, **kwargs) -> None:
        ...

    def _get_is_remote_cls_method(self):
        ...

    def _get_info(self):
        ...

    def _get_obj(self):
        ...

    def local(self, *args, **kwargs) -> typing.Any:
        ...

    async def spawn(self, *args, **kwargs) -> typing.Union[_FunctionCall, None]:
        ...

    def get_raw_f(self) -> typing.Callable[..., typing.Any]:
        ...

    async def get_current_stats(self) -> FunctionStats:
        ...

    class __map_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> modal._utils.async_utils.AsyncOrSyncIteratable:
            ...

        def aio(self, *input_iterators: typing.Union[typing.Iterable[typing.Any], typing.AsyncIterable[typing.Any]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    map: __map_spec

    class __starmap_spec(typing_extensions.Protocol):
        def __call__(self, input_iterator: typing.Iterable[typing.Sequence[typing.Any]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> modal._utils.async_utils.AsyncOrSyncIteratable:
            ...

        def aio(self, input_iterator: typing.Union[typing.Iterable[typing.Sequence[typing.Any]], typing.AsyncIterable[typing.Sequence[typing.Any]]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncIterable[typing.Any]:
            ...

    starmap: __starmap_spec

    class __for_each_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
            ...

        async def aio(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
            ...

    for_each: __for_each_spec


class Function(modal.object.Object):
    _info: typing.Union[modal._utils.function_utils.FunctionInfo, None]
    _all_mounts: typing.Collection[modal.mount.Mount]
    _app: modal.app.App
    _obj: typing.Any
    _web_url: typing.Union[str, None]
    _is_remote_cls_method: bool
    _function_name: typing.Union[str, None]
    _is_method: bool
    _spec: _FunctionSpec
    _tag: str
    _raw_f: typing.Callable[..., typing.Any]
    _build_args: dict
    _parent: Function

    def __init__(self, *args, **kwargs):
        ...

    @staticmethod
    def from_args(info: modal._utils.function_utils.FunctionInfo, app, image: modal.image.Image, secret: typing.Union[modal.secret.Secret, None] = None, secrets: typing.Sequence[modal.secret.Secret] = (), schedule: typing.Union[modal.schedule.Schedule, None] = None, is_generator=False, gpu: typing.Union[None, bool, str, modal.gpu._GPUConfig] = None, mounts: typing.Collection[modal.mount.Mount] = (), network_file_systems: typing.Dict[typing.Union[str, pathlib.PurePosixPath], modal.network_file_system.NetworkFileSystem] = {}, allow_cross_region_volumes: bool = False, volumes: typing.Dict[typing.Union[str, pathlib.PurePosixPath], typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount]] = {}, webhook_config: typing.Union[modal_proto.api_pb2.WebhookConfig, None] = None, memory: typing.Union[int, typing.Tuple[int, int], None] = None, proxy: typing.Union[modal.proxy.Proxy, None] = None, retries: typing.Union[int, modal.retries.Retries, None] = None, timeout: typing.Union[int, None] = None, concurrency_limit: typing.Union[int, None] = None, allow_concurrent_inputs: typing.Union[int, None] = None, container_idle_timeout: typing.Union[int, None] = None, cpu: typing.Union[float, None] = None, keep_warm: typing.Union[int, None] = None, cloud: typing.Union[str, None] = None, _experimental_boost: bool = False, _experimental_scheduler: bool = False, _experimental_scheduler_placement: typing.Union[modal.scheduler_placement.SchedulerPlacement, None] = None, is_builder_function: bool = False, is_auto_snapshot: bool = False, enable_memory_snapshot: bool = False, checkpointing_enabled: typing.Union[bool, None] = None, allow_background_volume_commits: bool = False, block_network: bool = False, max_inputs: typing.Union[int, None] = None) -> None:
        ...

    def from_parametrized(self, obj, from_other_workspace: bool, options: typing.Union[modal_proto.api_pb2.FunctionOptions, None], args: typing.Sized, kwargs: typing.Dict[str, typing.Any]) -> Function:
        ...

    class __keep_warm_spec(typing_extensions.Protocol):
        def __call__(self, warm_pool_size: int) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    keep_warm: __keep_warm_spec

    @classmethod
    def from_name(cls: typing.Type[Function], app_name: str, tag: typing.Union[str, None] = None, namespace=1, environment_name: typing.Union[str, None] = None) -> Function:
        ...

    class __lookup_spec(typing_extensions.Protocol):
        def __call__(self, app_name: str, tag: typing.Union[str, None] = None, namespace=1, client: typing.Union[modal.client.Client, None] = None, environment_name: typing.Union[str, None] = None) -> Function:
            ...

        async def aio(self, *args, **kwargs) -> Function:
            ...

    lookup: __lookup_spec

    @property
    def tag(self) -> str:
        ...

    @property
    def app(self) -> modal.app.App:
        ...

    @property
    def stub(self) -> modal.app.App:
        ...

    @property
    def info(self) -> modal._utils.function_utils.FunctionInfo:
        ...

    @property
    def spec(self) -> _FunctionSpec:
        ...

    def get_build_def(self) -> str:
        ...

    def _initialize_from_empty(self):
        ...

    def _hydrate_metadata(self, metadata: typing.Union[google.protobuf.message.Message, None]):
        ...

    def _get_metadata(self):
        ...

    def _set_mute_cancellation(self, value: bool = True):
        ...

    def _set_output_mgr(self, output_mgr: modal._output.OutputManager):
        ...

    @property
    def web_url(self) -> str:
        ...

    @property
    def is_generator(self) -> bool:
        ...

    class ___map_spec(typing_extensions.Protocol):
        def __call__(self, input_queue: modal.parallel_map.SynchronizedQueue, order_outputs: bool, return_exceptions: bool) -> typing.Generator[typing.Any, None, None]:
            ...

        def aio(self, input_queue: modal.parallel_map.SynchronizedQueue, order_outputs: bool, return_exceptions: bool) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    _map: ___map_spec

    class ___call_function_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _call_function: ___call_function_spec

    class ___call_function_nowait_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs) -> _Invocation:
            ...

        async def aio(self, *args, **kwargs) -> _Invocation:
            ...

    _call_function_nowait: ___call_function_nowait_spec

    def _call_generator(self, args, kwargs):
        ...

    class ___call_generator_nowait_spec(typing_extensions.Protocol):
        def __call__(self, args, kwargs):
            ...

        async def aio(self, *args, **kwargs):
            ...

    _call_generator_nowait: ___call_generator_nowait_spec

    class __remote_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Any:
            ...

        async def aio(self, *args, **kwargs) -> typing.Any:
            ...

    remote: __remote_spec

    class __remote_gen_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Generator[typing.Any, None, None]:
            ...

        def aio(self, *args, **kwargs) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    remote_gen: __remote_gen_spec

    class __shell_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> None:
            ...

        async def aio(self, *args, **kwargs) -> None:
            ...

    shell: __shell_spec

    def _get_is_remote_cls_method(self):
        ...

    def _get_info(self):
        ...

    def _get_obj(self):
        ...

    def local(self, *args, **kwargs) -> typing.Any:
        ...

    class __spawn_spec(typing_extensions.Protocol):
        def __call__(self, *args, **kwargs) -> typing.Union[FunctionCall, None]:
            ...

        async def aio(self, *args, **kwargs) -> typing.Union[FunctionCall, None]:
            ...

    spawn: __spawn_spec

    def get_raw_f(self) -> typing.Callable[..., typing.Any]:
        ...

    class __get_current_stats_spec(typing_extensions.Protocol):
        def __call__(self) -> FunctionStats:
            ...

        async def aio(self, *args, **kwargs) -> FunctionStats:
            ...

    get_current_stats: __get_current_stats_spec

    class __map_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> modal._utils.async_utils.AsyncOrSyncIteratable:
            ...

        def aio(self, *input_iterators: typing.Union[typing.Iterable[typing.Any], typing.AsyncIterable[typing.Any]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncGenerator[typing.Any, None]:
            ...

    map: __map_spec

    class __starmap_spec(typing_extensions.Protocol):
        def __call__(self, input_iterator: typing.Iterable[typing.Sequence[typing.Any]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> modal._utils.async_utils.AsyncOrSyncIteratable:
            ...

        def aio(self, input_iterator: typing.Union[typing.Iterable[typing.Sequence[typing.Any]], typing.AsyncIterable[typing.Sequence[typing.Any]]], kwargs={}, order_outputs: bool = True, return_exceptions: bool = False) -> typing.AsyncIterable[typing.Any]:
            ...

    starmap: __starmap_spec

    class __for_each_spec(typing_extensions.Protocol):
        def __call__(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
            ...

        async def aio(self, *input_iterators, kwargs={}, ignore_exceptions: bool = False):
            ...

    for_each: __for_each_spec


class _FunctionCall(modal.object._Object):
    def _invocation(self):
        ...

    async def get(self, timeout: typing.Union[float, None] = None):
        ...

    async def get_call_graph(self) -> typing.List[modal.call_graph.InputInfo]:
        ...

    async def cancel(self):
        ...

    @staticmethod
    async def from_id(function_call_id: str, client: typing.Union[modal.client._Client, None] = None) -> _FunctionCall:
        ...


class FunctionCall(modal.object.Object):
    def __init__(self, *args, **kwargs):
        ...

    def _invocation(self):
        ...

    class __get_spec(typing_extensions.Protocol):
        def __call__(self, timeout: typing.Union[float, None] = None):
            ...

        async def aio(self, *args, **kwargs):
            ...

    get: __get_spec

    class __get_call_graph_spec(typing_extensions.Protocol):
        def __call__(self) -> typing.List[modal.call_graph.InputInfo]:
            ...

        async def aio(self, *args, **kwargs) -> typing.List[modal.call_graph.InputInfo]:
            ...

    get_call_graph: __get_call_graph_spec

    class __cancel_spec(typing_extensions.Protocol):
        def __call__(self):
            ...

        async def aio(self, *args, **kwargs):
            ...

    cancel: __cancel_spec

    class __from_id_spec(typing_extensions.Protocol):
        def __call__(self, function_call_id: str, client: typing.Union[modal.client.Client, None] = None) -> FunctionCall:
            ...

        async def aio(self, *args, **kwargs) -> FunctionCall:
            ...

    from_id: __from_id_spec


async def _gather(*function_calls: _FunctionCall):
    ...


class __gather_spec(typing_extensions.Protocol):
    def __call__(self, *function_calls: FunctionCall):
        ...

    async def aio(self, *args, **kwargs):
        ...

gather: __gather_spec
