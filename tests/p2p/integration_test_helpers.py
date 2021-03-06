import asyncio
from typing import Type

from eth_keys import datatypes

from evm import MainnetChain, RopstenChain
from evm.chains.base import Chain
from evm.db.chain import AsyncChainDB

from p2p import kademlia
from p2p.peer import BasePeer, HardCodedNodesPeerPool

from trinity.db.header import AsyncHeaderDB


def async_passthrough(base_name):
    coro_name = 'coro_{0}'.format(base_name)

    async def passthrough_method(self, *args, **kwargs):
        return getattr(self, base_name)(*args, **kwargs)
    passthrough_method.__name__ = coro_name
    return passthrough_method


class SingleNodePeerPool(HardCodedNodesPeerPool):
    """A PeerPool that will only attempt to connect to the enode passed to its __init__()"""

    def __init__(self,
                 peer_class: Type[BasePeer],
                 chaindb: AsyncChainDB,
                 network_id: int,
                 privkey: datatypes.PrivateKey,
                 enode: str,
                 ) -> None:
        discovery = None
        self._node = kademlia.Node.from_uri(enode)
        super().__init__(
            peer_class, chaindb, network_id, privkey, discovery, max_peers=1,
        )

    def get_nodes_to_connect(self):
        yield self._node


class FakeAsyncChainDB(AsyncChainDB):
    coro_get_score = async_passthrough('get_score')
    coro_get_block_header_by_hash = async_passthrough('get_block_header_by_hash')
    coro_get_canonical_head = async_passthrough('get_canonical_head')
    coro_header_exists = async_passthrough('header_exists')
    coro_get_canonical_block_hash = async_passthrough('get_canonical_block_hash')
    coro_persist_header = async_passthrough('persist_header')
    coro_persist_uncles = async_passthrough('persist_uncles')
    coro_persist_trie_data_dict = async_passthrough('persist_trie_data_dict')
    coro_get_canonical_block_header_by_number = async_passthrough(
        'get_canonical_block_header_by_number')
    coro_get_block_transactions = async_passthrough('get_block_transactions')
    coro_get_block_uncles = async_passthrough('get_block_uncles')
    coro_get_receipts = async_passthrough('get_receipts')


async def coro_import_block(chain, block, perform_validation=True):
    # Be nice and yield control to give other coroutines a chance to run before us as
    # importing a block is a very expensive operation.
    await asyncio.sleep(0)
    return chain.import_block(block, perform_validation=perform_validation)


class FakeAsyncRopstenChain(RopstenChain):
    chaindb_class = FakeAsyncChainDB
    coro_import_block = coro_import_block


class FakeAsyncMainnetChain(MainnetChain):
    chaindb_class = FakeAsyncChainDB
    coro_import_block = coro_import_block


class FakeAsyncChain(Chain):
    coro_import_block = coro_import_block


class FakeAsyncHeaderDB(AsyncHeaderDB):
    coro_get_canonical_block_hash = async_passthrough('get_canonical_block_hash')
    coro_get_canonical_block_header_by_number = async_passthrough('get_canonical_block_header_by_number')  # noqa: E501
    coro_get_canonical_head = async_passthrough('get_canonical_head')
    coro_get_block_header_by_hash = async_passthrough('get_block_header_by_hash')
    coro_get_score = async_passthrough('get_score')
    coro_header_exists = async_passthrough('header_exists')
    coro_persist_header = async_passthrough('persist_header')
