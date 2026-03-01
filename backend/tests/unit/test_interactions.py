"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    test_interaction = _make_log(id=1, learner_id=2, item_id=1)
    other_interaction = _make_log(id=2, learner_id=1, item_id=2)

    interactions = [test_interaction, other_interaction]
    filtered_interactions = _filter_by_item_id(interactions, 1)

    assert len(filtered_interactions) == 1
    assert filtered_interactions[0].id == 1
    assert filtered_interactions[0].item_id == 1
    assert filtered_interactions[0].learner_id == 2


def test_filter_by_item_id_with_zero_item_id():
    """Test _filter_by_item_id with item_id=0 (boundary value)."""
    interactions = [
        InteractionLog(id=1, learner_id=1, item_id=0, kind="view"),
        InteractionLog(id=2, learner_id=1, item_id=1, kind="attempt"),
        InteractionLog(id=3, learner_id=1, item_id=0, kind="hint"),
    ]

    result = _filter_by_item_id(interactions, 0)

    assert len(result) == 2
    assert all(i.item_id == 0 for i in result)
    assert set(i.id for i in result) == {1, 3}


def test_filter_by_item_id_with_large_item_id():
    """Test _filter_by_item_id with a very large item_id value."""
    large_id = 2**31 - 1  # Max 32-bit signed integer
    interactions = [
        InteractionLog(id=1, learner_id=1, item_id=large_id, kind="view"),
        InteractionLog(id=2, learner_id=1, item_id=1, kind="attempt"),
    ]

    result = _filter_by_item_id(interactions, large_id)

    assert len(result) == 1
    assert result[0].item_id == large_id
