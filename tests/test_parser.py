# tests/test_parser.py
"""
Unit testler - Product Parser modülü.
"""
import unittest
from src.parsers.product_parser import extract_unit_and_quantity


class TestExtractUnitAndQuantity(unittest.TestCase):
    """extract_unit_and_quantity fonksiyonunu test eder."""
    
    def test_simple_gram(self):
        """Basit gram formatı."""
        birim, miktar = extract_unit_and_quantity("Un 500 gr")
        self.assertEqual(birim, 'gr')
        self.assertEqual(miktar, 500.0)
    
    def test_simple_kg(self):
        """Kilogram - grama dönüşüm."""
        birim, miktar = extract_unit_and_quantity("Pirinç 1 kg")
        self.assertEqual(birim, 'gr')
        self.assertEqual(miktar, 1000.0)
    
    def test_simple_ml(self):
        """Basit mililitre formatı."""
        birim, miktar = extract_unit_and_quantity("Süt 1000 ml")
        self.assertEqual(birim, 'ml')
        self.assertEqual(miktar, 1000.0)
    
    def test_simple_liter(self):
        """Litre - ml'ye dönüşüm."""
        birim, miktar = extract_unit_and_quantity("Ayran 1.5 lt")
        self.assertEqual(birim, 'ml')
        self.assertEqual(miktar, 1500.0)
    
    def test_multiplication_format(self):
        """Çarpım formatı (6x200ml)."""
        birim, miktar = extract_unit_and_quantity("Kola 6x200ml")
        self.assertEqual(birim, 'ml')
        self.assertEqual(miktar, 1200.0)
    
    def test_multiplication_with_asterisk(self):
        """Yıldız ile çarpım (12*25 gr)."""
        birim, miktar = extract_unit_and_quantity("Çikolata 12*25 gr")
        self.assertEqual(birim, 'gr')
        self.assertEqual(miktar, 300.0)
    
    def test_adet_format(self):
        """Adet formatı (100'lü)."""
        birim, miktar = extract_unit_and_quantity("Peçete 100'lü")
        self.assertEqual(birim, 'adet')
        self.assertEqual(miktar, 100.0)
    
    def test_no_unit(self):
        """Birim olmayan ürün - varsayılan."""
        birim, miktar = extract_unit_and_quantity("Ekmek")
        self.assertEqual(birim, 'adet')
        self.assertEqual(miktar, 1.0)
    
    def test_decimal_quantity(self):
        """Ondalıklı miktar."""
        birim, miktar = extract_unit_and_quantity("Yağ 1.5 lt")
        self.assertEqual(birim, 'ml')
        self.assertEqual(miktar, 1500.0)
    
    def test_comma_as_decimal(self):
        """Virgül ile ondalık."""
        birim, miktar = extract_unit_and_quantity("Süt 2,5 lt")
        self.assertEqual(birim, 'ml')
        self.assertEqual(miktar, 2500.0)


class TestProductParserIntegration(unittest.TestCase):
    """Product parser integration testleri."""
    
    def test_import_modules(self):
        """Tüm modüller import edilebilmeli."""
        from src.parsers.product_parser import parse_products_data
        from src.utils.validators import validate_product_data
        self.assertTrue(callable(parse_products_data))
        self.assertTrue(callable(validate_product_data))


if __name__ == '__main__':
    unittest.main()
