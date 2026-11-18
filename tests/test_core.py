import unittest, tempfile, pathlib
from unittest.mock import patch
from beru import knowledge


class RetrievalTests(unittest.TestCase):
    def test_diacritics_and_provenance(self):
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(knowledge, "DB", pathlib.Path(d) / "test.sqlite"),
        ):
            c = knowledge.connect()
            c.execute(
                "INSERT INTO passages VALUES (?,?,?)",
                (
                    "course.md",
                    "Page 3",
                    "La distance hiérarchique concerne les inégalités de pouvoir.",
                ),
            )
            c.commit()
            c.close()
            hits = knowledge.search("distance hierarchique")
            self.assertEqual(hits[0]["section"], "Page 3")
            self.assertEqual(hits[0]["source"], "course.md")

    def test_empty_query(self):
        self.assertEqual(knowledge.search("!?"), [])

    def test_query_operators_are_data(self):
        with (
            tempfile.TemporaryDirectory() as d,
            patch.object(knowledge, "DB", pathlib.Path(d) / "test.sqlite"),
        ):
            self.assertEqual(knowledge.search('" OR NOT *'), [])


if __name__ == "__main__":
    unittest.main()


class ProviderTests(unittest.TestCase):
    def test_missing_key(self):
        from beru.providers import answer

        with patch.dict("os.environ", {}, clear=True), patch("beru.providers.load_env"):
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                answer("Question", [])

    def test_citation_bounds(self):
        from beru.providers import answer

        response = __import__("unittest.mock", fromlist=["Mock"]).Mock()
        response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"answer":"A","uncertain":false,"citations":[1,999,-1]}'
                            }
                        ]
                    }
                }
            ]
        }
        with (
            patch.dict("os.environ", {"GEMINI_API_KEY": "test"}, clear=True),
            patch("beru.providers.load_env"),
            patch("beru.providers.requests.post", return_value=response),
        ):
            result = answer("Question", [{"source": "course", "text": "evidence"}])
            self.assertEqual(result["citations"], [1])
