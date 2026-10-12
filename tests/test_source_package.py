from pathlib import Path
import re, unittest

class SourcePackageTests(unittest.TestCase):
    def test_frontend_has_no_embedded_assets(self):
        html=(Path(__file__).resolve().parents[1]/'web/index.html').read_text(encoding='utf-8')
        self.assertNotIn('base64,',html)
        self.assertNotIn('atob(',html)
        self.assertNotIn('"subtitles":',html)
        self.assertIn('assets/scenes.json',html)
    def test_ignore_generated_content(self):
        text=(Path(__file__).resolve().parents[1]/'.gitignore').read_text()
        for rule in ['/web/assets/','/web/codec.wasm','*.bin','*.mp3']:self.assertIn(rule,text)

if __name__=='__main__':unittest.main()
