import unittest
import tkinter as tk
from main import ScientificCalculator

class TestScientificCalculator(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        # self.root.withdraw()  # Hide the main window
        self.calculator = ScientificCalculator(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initial_state(self):
        self.assertEqual(self.calculator.expression, "")
        self.assertEqual(self.calculator.input_text.get(), "")

    def test_btn_click_numbers(self):
        self.calculator.btn_click("7")
        self.assertEqual(self.calculator.expression, "7")
        self.assertEqual(self.calculator.input_text.get(), "7")
        self.calculator.btn_click("8")
        self.assertEqual(self.calculator.expression, "78")
        self.assertEqual(self.calculator.input_text.get(), "78")

    def test_btn_click_operators(self):
        self.calculator.btn_click("5")
        self.calculator.btn_click("+")
        self.calculator.btn_click("3")
        self.assertEqual(self.calculator.expression, "5+3")
        self.assertEqual(self.calculator.input_text.get(), "5+3")

    def test_btn_clear(self):
        self.calculator.btn_click("123")
        self.calculator.btn_clear()
        self.assertEqual(self.calculator.expression, "")
        self.assertEqual(self.calculator.input_text.get(), "")

    def test_btn_equal_addition(self):
        self.calculator.btn_click("5+3")
        self.calculator.btn_equal()
        self.assertEqual(self.calculator.expression, "8")
        self.assertEqual(self.calculator.input_text.get(), "8")

    def test_btn_equal_subtraction(self):
        self.calculator.btn_click("10-4")
        self.calculator.btn_equal()
        self.assertEqual(self.calculator.expression, "6")
        