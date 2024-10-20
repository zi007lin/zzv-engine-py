import unittest

from common.utility import clean_requirements


class TestRequirementsCleaner(unittest.TestCase):
    def test_remove_duplicates(self):
        input_content = """
        package1==1.0.0
        package2>=2.0.0
        package1==1.1.0
        """
        expected_output = "package1==1.1.0\npackage2>=2.0.0\n"
        self.assertEqual(clean_requirements(input_content), expected_output)

    def test_sort_alphabetically(self):
        input_content = """
        c-package==1.0.0
        a-package==2.0.0
        b-package==3.0.0
        """
        expected_output = "a-package==2.0.0\nb-package==3.0.0\nc-package==1.0.0\n"
        self.assertEqual(clean_requirements(input_content), expected_output)

    def test_remove_comments_and_empty_lines(self):
        input_content = """
        # This is a comment
        package1==1.0.0

        # Another comment
        package2==2.0.0
        """
        expected_output = "package1==1.0.0\npackage2==2.0.0\n"
        self.assertEqual(clean_requirements(input_content), expected_output)

    def test_keep_higher_version(self):
        input_content = """
        package1==1.0.0
        package1==2.0.0
        package1==1.5.0
        """
        expected_output = "package1==2.0.0\n"
        self.assertEqual(clean_requirements(input_content), expected_output)


if __name__ == '__main__':
    unittest.main()
