import unittest
from scraper import allowed, parse_page

class ExtractionTests(unittest.TestCase):
    def test_text_tags_and_pagination(self):
        html = '<div class="quote"><span class="text"> A  thought </span><small class="author">Writer</small><a href="/author/Writer">about</a><a class="tag">ideas</a></div><li class="next"><a href="/page/2/">next</a></li>'
        rows, next_url, rejected = parse_page(html, 'https://quotes.toscrape.com/')
        self.assertEqual(rows[0]['text'], 'A thought')
        self.assertEqual(rows[0]['tags'], ['ideas'])
        self.assertEqual(next_url, 'https://quotes.toscrape.com/page/2/')
        self.assertEqual(rejected, 0)
        self.assertEqual(rows, parse_page(html, 'https://quotes.toscrape.com/')[0])
    def test_malformed_records_and_scope(self):
        self.assertEqual(parse_page('<div class="quote">missing fields</div>', 'https://quotes.toscrape.com/')[2], 1)
        self.assertFalse(allowed('https://quotes.toscrape.com.evil.invalid/'))
        self.assertFalse(allowed('http://127.0.0.1/'))
        self.assertFalse(allowed('https://quotes.toscrape.com/?next=anything'))

if __name__ == '__main__': unittest.main()
