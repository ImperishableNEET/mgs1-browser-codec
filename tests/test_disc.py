import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import disc

class DiscTests(unittest.TestCase):
    def test_raw_modes(self):
        raw=bytearray(2352);raw[:12]=bytes.fromhex('00ffffffffffffffffffff00');raw[15]=2
        raw[24:2072]=b'x'*2048
        self.assertEqual(disc.read_user_bin(raw,0),b'x'*2048)
        raw[18]=raw[22]=32
        with self.assertRaises(ValueError):disc.read_user_bin(raw,0)
    def test_bounds(self):
        with self.assertRaises(ValueError):disc.read_user_bin(b'',0)
        with self.assertRaises(ValueError):disc.read_file(disc.read_user_bin,b'',1,2048)
        with self.assertRaises(ValueError):disc.parse_directory_entries(bytes([3,0,0]))
    def test_missing_path(self):
        with self.assertRaises(ValueError):disc.resolve_iso_file(None,b'',{},'MISSING')

if __name__=='__main__':unittest.main()
