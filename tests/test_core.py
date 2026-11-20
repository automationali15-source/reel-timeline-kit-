import json
import tempfile
import unittest
from pathlib import Path
from reel_timeline_kit.core import ManifestError,build_timeline,export_timeline,srt_time
from reel_timeline_kit.__main__ import main

class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.plan={"project":"Demo","fps":30,"scenes":[{"duration":2,"voiceover":"Hi"},{"duration":1.5,"voiceover":"Bye"}]}
    def test_frames(self):
        t=build_timeline(self.plan)
        self.assertEqual(t["total_frames"],105)
        self.assertEqual(t["scenes"][1]["start_frame"],60)
    def test_seconds(self):
        self.assertEqual(build_timeline(self.plan)["total_seconds"],3.5)
    def test_invalid_fps(self):
        with self.assertRaises(ManifestError):
            build_timeline({"fps":True,"scenes":[{"duration":1}]})
    def test_invalid_duration(self):
        with self.assertRaises(ManifestError):
            build_timeline({"scenes":[{"duration":-1}]})
    def test_pacing(self):
        t=build_timeline({"scenes":[{"duration":1,"voiceover":"one two three four five six"}]})
        self.assertTrue(t["warnings"])
    def test_srt(self):
        self.assertEqual(srt_time(1.5),"00:00:01,500")
    def test_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            export_timeline(build_timeline(self.plan),d)
            self.assertTrue((Path(d)/"captions.srt").exists())
            self.assertEqual(json.loads((Path(d)/"summary.json").read_text())["total_frames"],105)
    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"example.json"
            p.write_text(json.dumps(self.plan))
            self.assertEqual(main([str(p),"--out",str(Path(d)/"out")]),0)

if __name__=="__main__":
    unittest.main()
