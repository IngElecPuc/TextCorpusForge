from textforge.schemas.contract import (
    DOCUMENT_COLUMNS,
    PAIR_COLUMNS,
    SCHEMA_CONTRACT_VERSION,
    SEGMENT_COLUMNS,
    describe_contract,
)


def test_schema_contract_is_frozen_stage1_v1():
    assert SCHEMA_CONTRACT_VERSION == 'stage1-v1'
    assert SEGMENT_COLUMNS == [
        'dataset_name', 'domain', 'origin_path', 'doc_group_id', 'metadata',
        'segment_id', 'lang', 'text_raw', 'text_norm', 'sequence_index', 'segment_key',
        'segment_key_numeric', 'speaker', 'is_dialogue', 'can_concat_left', 'can_concat_right',
        'casing_profile', 'num_chars', 'num_words', 'quality_flags',
    ]
    assert PAIR_COLUMNS == [
        'dataset_name', 'domain', 'origin_path', 'doc_group_id', 'metadata',
        'pair_id', 'pair_index', 'src_lang', 'tgt_lang', 'src_text_raw', 'tgt_text_raw',
        'src_text_norm', 'tgt_text_norm', 'src_segment_keys', 'tgt_segment_keys',
        'src_sequence_indices', 'tgt_sequence_indices', 'alignment_type', 'src_words',
        'tgt_words', 'length_ratio', 'quality_flags',
    ]
    assert DOCUMENT_COLUMNS == [
        'dataset_name', 'domain', 'origin_path', 'doc_group_id', 'metadata',
        'document_id', 'src_lang', 'tgt_lang', 'split_hint', 'is_parallel',
        'segment_count_src', 'segment_count_tgt', 'pair_count', 'total_chars_src',
        'total_chars_tgt', 'total_words_src', 'total_words_tgt',
    ]


def test_describe_contract_contains_all_tables():
    contract = describe_contract()
    assert contract['version'] == SCHEMA_CONTRACT_VERSION
    assert contract['segments'] == SEGMENT_COLUMNS
    assert contract['pairs'] == PAIR_COLUMNS
    assert contract['documents'] == DOCUMENT_COLUMNS
