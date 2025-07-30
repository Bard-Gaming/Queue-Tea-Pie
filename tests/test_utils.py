from unittest import TestCase

from qtp import generate_request


class Test(TestCase):
    def test_generate_request_single(self) -> None:
        body = "hihi"
        request = generate_request(body)

        self.assertEqual(request.get("Records", [{}])[0].get("body"), body)

    def test_generate_request_empty(self) -> None:
        request = generate_request()
        expected = {"Records": []}

        self.assertEqual(request, expected)

    def test_generate_request_invalid_type(self) -> None:
        with self.assertRaises(TypeError):
            generate_request(32)
