"""O mesmo teste em unittest (biblioteca padrão) e em pytest."""
import io
import unittest

from pricing import apply_discount


class DiscountTests(unittest.TestCase):
    def setUp(self):
        self.price = 100

    def test_basic(self):
        self.assertEqual(apply_discount(self.price, 10), 90)

    def test_invalid(self):
        with self.assertRaisesRegex(ValueError, "inválido"):
            apply_discount(self.price, 101)

    def test_almost_equal(self):
        self.assertAlmostEqual(0.1 + 0.2, 0.3)

    @unittest.expectedFailure
    def test_bug(self):
        self.assertEqual(1, 2)


stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiscountTests)
result = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
print(stream.getvalue().strip().splitlines()[-1], "| executados:", result.testsRun, "| falhas esperadas:", len(result.expectedFailures))

# Em pytest: funções simples e assert nu
def test_basic():
    assert apply_discount(100, 10) == 90


test_basic()
print("pytest: sem classe, sem self.assertEqual: o assert nu mostra os valores quando falha")
