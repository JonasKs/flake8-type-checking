"""
File tests TYO201:
    Annotation is wrapped in unnecessary quotes
"""
import textwrap

import pytest

from flake8_typing_only_imports.constants import TYO201
from tests import _get_error

examples = [
    # No error
    ('', set()),
    # Basic AnnAssign with futures import
    ("from __future__ import annotations\nx: 'int'", {'2:3 ' + TYO201.format(annotation='int')}),
    # Basic AnnAssign with quotes and no type checking block
    ("x: 'Dict[int]'", {'1:3 ' + TYO201.format(annotation='Dict[int]')}),
    # Basic AnnAssign with type-checking block and exact match
    (
        "from __future__ import annotations\nif TYPE_CHECKING:\n\tfrom typing import Dict\nx: 'Dict'",
        {'4:3 ' + TYO201.format(annotation='Dict')},
    ),
    # Nested ast.AnnAssign with quotes
    (
        "from __future__ import annotations\nfrom typing import Dict\nx: Dict['int']",
        {'3:8 ' + TYO201.format(annotation='int')},
    ),
    # ast.AnnAssign from type checking block import with quotes
    (
        textwrap.dedent(
            f'''
            from __future__ import annotations

            if TYPE_CHECKING:
                import something

            x: "something"
            '''
        ),
        {'7:3 ' + TYO201.format(annotation='something')},
    ),
    # No futures import and no type checking block
    ("from typing import Dict\nx: 'Dict'", {'2:3 ' + TYO201.format(annotation='Dict')}),
    (
        textwrap.dedent(
            f'''
        from __future__ import annotations

        if TYPE_CHECKING:
            import something

        def example(x: "something") -> something:
            pass
        '''
        ),
        {'7:15 ' + TYO201.format(annotation='something')},
    ),
    (
        textwrap.dedent(
            f'''
        from __future__ import annotations

        if TYPE_CHECKING:
            import something

        def example(x: "something") -> "something":
            pass
        '''
        ),
        {'7:15 ' + TYO201.format(annotation='something'), '7:31 ' + TYO201.format(annotation='something')},
    ),
    (
        textwrap.dedent(
            f'''
        from __future__ import annotations

        if TYPE_CHECKING:
            import something

        def example(x: "something") -> "something":
            pass
        '''
        ),
        {'7:15 ' + TYO201.format(annotation='something'), '7:31 ' + TYO201.format(annotation='something')},
    ),
    (
        textwrap.dedent(
            f'''
    import something

    def example(x: "something") -> "something":
        pass
    '''
        ),
        {'4:15 ' + TYO201.format(annotation='something'), '4:31 ' + TYO201.format(annotation='something')},
    ),
]


@pytest.mark.parametrize('example, expected', examples)
def test_tyo201_errors(example, expected):
    assert _get_error(example, error_code_filter='TYO201') == expected
