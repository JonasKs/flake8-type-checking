"""
Contains special test cases that fall outside the scope of remaining test files.
"""
import textwrap

from flake8_type_checking.constants import TCH001, TCH002, TCH003, TCH004, TCHA001
from tests import _get_error, mod


class TestFoundBugs:
    def test_mixed_errors(self):
        example = textwrap.dedent(
            f"""
        import {mod}
        import pytest
        from x import y
        """
        )
        assert _get_error(example) == {
            '2:0 ' + TCH001.format(module=f'{mod}'),
            '3:0 ' + TCH002.format(module=f'pytest'),
            '4:0 ' + TCH002.format(module=f'x.y'),
        }

    def test_type_checking_block_imports_dont_generate_errors(self):
        example = textwrap.dedent(
            """
        import x
        from y import z

        if TYPE_CHECKING:
            import a

            # arbitrary whitespace

            from b import c

        def test():
            pass
        """
        )
        assert _get_error(example) == {
            '1:0 ' + TCHA001,
            '2:0 ' + TCH002.format(module='x'),
            '3:0 ' + TCH002.format(module='y.z'),
        }

    def test_model_declarations_dont_trigger_error(self):
        """
        Initially found false positives in Django project, because name
        visitor did not capture the SomeModel usage in the example below.
        """
        example = textwrap.dedent(
            """
        from django.db import models
        from app.models import SomeModel

        class LoanProvider(models.Model):
            fk: SomeModel = models.ForeignKey(
                SomeModel,
                on_delete=models.CASCADE,
            )
        """
        )
        assert _get_error(example) == set()

    def test_all_declaration(self):
        """
        __all__ declarations originally generated false positives.
        """
        example = textwrap.dedent(
            """
        from app.models import SomeModel
        from another_app.models import AnotherModel

        __all__ = ['SomeModel', 'AnotherModel']
        """
        )
        assert _get_error(example) == set()

    def test_callable_import(self):
        """
        __all__ declarations originally generated false positives.
        """
        example = textwrap.dedent(
            """
        from x import y

        class X:
            def __init__(self):
                self.all_sellable_models: list[CostModel] = y(
                    country=self.country
                )
        """
        )
        assert _get_error(example) == set()

    def test_ellipsis(self):
        example = textwrap.dedent(
            """
        x: Tuple[str, ...]
        """
        )
        assert _get_error(example) == set()

    def test_literal(self):
        example = textwrap.dedent(
            """
        from __future__ import annotations

        x: Literal['string']
        """
        )
        assert _get_error(example) == set()

    def test_conditional_import(self):
        example = textwrap.dedent(
            """
        version = 2

        if version == 2:
            import x
        else:
            import y as x

        var: x
        """
        )
        assert _get_error(example) == {"7:4 TCH002: Move third-party import 'x' into a type-checking block"}

    def test_called_typing_import(self):
        example = textwrap.dedent(
            """
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from datetime import datetime
            from datetime import date

        x = datetime

        def example():
            return date()
        """
        )
        assert _get_error(example) == {'5:0 ' + TCH004.format(module='datetime'), '6:0 ' + TCH004.format(module='date')}
