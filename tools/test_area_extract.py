"""Run: python -m unittest discover -s tools -p test_area_extract.py -v"""
import hashlib
import tempfile
import unittest
from pathlib import Path
from area_extract import extract, projection, validate_inputs
import ifcopenshell

PUBLIC = Path(__file__).resolve().parents[1]
INPUTS = PUBLIC / 'area-lab' / 'inputs'

class AreaLabTests(unittest.TestCase):
    def test_two_real_examples_and_source_readonly(self):
        paths = [INPUTS / '25B.ifc', INPUTS / 'A32-05.ifc']
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        result = extract(paths)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
        self.assertEqual([s['storey_count'] for s in result['sources']], [1, 1])
        self.assertEqual([s['space_count'] for s in result['sources']], [5, 14])
        self.assertEqual([s['represented_spaces'] for s in result['sources']], [5, 0])
        self.assertEqual([s['slab_count'] for s in result['sources']], [2, 54])
        self.assertEqual(len(result['unit_slabs']), 14)
        for row in result['floors']:
            self.assertAlmostEqual(row['floor_xy_union_m2'], row['registered_unit_union_m2'] + row['outside_registered_unit_m2'], places=7)
            self.assertGreaterEqual(row['slab_xy_sum_m2'] + 1e-8, row['floor_xy_union_m2'])
        self.assertEqual(len(result['rows']), 75)
        self.assertTrue(all(s['sha256_before'] == s['sha256_after'] for s in result['sources']))

    def test_profiles_match_independent_previous_floor_control(self):
        result = extract([INPUTS / 'A32-05.ifc'])
        # Independent earlier full-model extraction; excludes LANDING/ROOF.
        import json
        expected = json.loads((PUBLIC / 'area-lab' / 'expected-results.json').read_text(encoding='utf8'))
        floor = result['floors'][0]
        self.assertAlmostEqual(floor['floor_xy_union_m2'], expected['A32-05']['floor_xy_union_m2'], places=7)
        self.assertAlmostEqual(floor['registered_unit_sum_m2'], expected['A32-05']['registered_unit_sum_m2'], places=7)
        self.assertAlmostEqual(extract([INPUTS / '25B.ifc'])['floors'][0]['floor_xy_union_m2'], expected['25B']['floor_xy_union_m2'], places=7)

    def test_same_input_rejected_prevents_duplicate_occurrences(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            validate_inputs([INPUTS / '25B.ifc', INPUTS / '25B.ifc'])

    def test_missing_space_representation_is_missing_not_zero(self):
        result = extract([INPUTS / 'A32-05.ifc'])
        rows = [r for r in result['rows'] if r['class'] == 'IfcSpace']
        self.assertEqual(len(rows), 14)
        self.assertTrue(all(r['area'] is None for r in rows))
        self.assertTrue(all(r['basis'] == 'NO_SPACE_GEOMETRY' for r in rows))

    def test_unsupported_geometry_fails_explicitly(self):
        f = ifcopenshell.file(schema='IFC4')
        e = f.create_entity('IfcSlab', GlobalId=ifcopenshell.guid.new())
        with self.assertRaisesRegex(ValueError, 'No Body'):
            projection(e, 1.0)

if __name__ == '__main__':
    unittest.main()
