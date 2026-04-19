from textforge.orchestration.stages import _apply_runtime_limits
from textforge.settings import Settings
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord
from textforge.schemas.document import DocumentRecord


def test_apply_runtime_limits_by_pairs():
    pairs = [ParallelPairRecord(dataset_name='dgt', domain='x', origin_path='a', doc_group_id='g', pair_index=i, src_text_norm='hello', tgt_text_norm='hola') for i in range(5)]
    segs = [SegmentRecord(dataset_name='dgt', domain='x', origin_path='a', doc_group_id='g', segment_id=str(i), lang='en', text_norm='hello') for i in range(5)]
    docs = [DocumentRecord(dataset_name='dgt', domain='x', origin_path='a', doc_group_id='g')]
    cfg = Settings({'runtime': {'max_pairs': 2}})
    segs2, pairs2, docs2, stats = _apply_runtime_limits(cfg, segs, pairs, docs)
    assert len(pairs2) == 2
    assert stats['max_pairs'] == 2
    assert len(segs2) == 5
    assert len(docs2) == 1
