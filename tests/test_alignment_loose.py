from textforge.align.monotonic import TextUnit, monotonic_align
from textforge.io.readers_parallel_text import build_monotonic_parallel_records


def test_monotonic_align_prefers_merge_for_split_translation():
    src = [
        TextUnit(index=0, text_raw='Hello world.', text_norm='Hello world.', sequence_index=1, line_numbers=(1,)),
    ]
    tgt = [
        TextUnit(index=0, text_raw='Hola', text_norm='Hola', sequence_index=1, line_numbers=(1,)),
        TextUnit(index=1, text_raw='mundo.', text_norm='mundo.', sequence_index=2, line_numbers=(2,)),
    ]
    result = monotonic_align(src, tgt)
    assert result[0].src_indices == (0,)
    assert result[0].tgt_indices == (0, 1)


def test_build_monotonic_parallel_records_opensubtitles_style(tmp_path):
    src_path = tmp_path / 'sample.en'
    tgt_path = tmp_path / 'sample.es'
    src_path.write_text('- Hello\n- Stay back\n\nWe need more adrenaline.\n', encoding='utf-8')
    tgt_path.write_text('- Hola\n- Retrocede\n\nNecesitamos más adrenalina.\n', encoding='utf-8')

    segments, pairs, documents = build_monotonic_parallel_records(
        dataset_name='opensubtitles',
        domain='conversational_subtitles',
        src_lang='en',
        tgt_lang='es',
        src_path=src_path,
        tgt_path=tgt_path,
        group_name='opensubtitles_default_stream',
        strategy_name='opensubtitles_monotonic_block',
        is_dialogue=True,
        allow_skip=True,
        block_mode='blankline_blocks',
        trusted_alignment=False,
    )

    assert documents
    assert pairs
    assert all('provisional_alignment' in pair.quality_flags for pair in pairs)
    assert all(segment.is_dialogue for segment in segments)
    assert all('block_index' in segment.metadata for segment in segments)
