"""
Test Factory to make fake objects for testing
"""

from factory import Factory, SubFactory, Sequence, post_generation
from factory.fuzzy import FuzzyInteger, FuzzyFloat
from service.models import Shopcart, ShopcartItem


class ShopcartFactory(Factory):
    """Creates fake Shopcarts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps factory to data model"""

        model = Shopcart

    id = Sequence(lambda n: n)
    total_price = FuzzyFloat(0, 200, precision=2)

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ShopcartItemFactory(Factory):
    """Creates fake ShopcartItems"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps factory to data model"""

        model = ShopcartItem

    id = Sequence(lambda n: n)
    shopcart_id = Sequence(lambda n: n)
    product_id = Sequence(lambda n: n)
    name = Sequence(lambda n: f"i-{n}")
    quantity = FuzzyInteger(1, 10)
    price = FuzzyFloat(0, 20, precision=2)
    shopcart = SubFactory(ShopcartFactory)
