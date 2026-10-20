"""Read-only IFC area lab. No Blender session or project modules required.

Only vertical polygonal swept profiles are accepted. This deliberate boundary
keeps A32's tiny valid profiles out of the known display-mesh triangulation bug.
Unsupported shapes stop the run; they are never replaced with bounding boxes.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import hashlib
import html
import json
from pathlib import Path
import sys

import numpy as np
import ifcopenshell
import ifcopenshell.util.element as element
import ifcopenshell.util.placement as placement
import ifcopenshell.util.representation as representation
import ifcopenshell.util.unit as units
from shapely.geometry import Polygon
from shapely.ops import unary_union

FIELDS = ['inputfile', 'GUID', 'class', 'storey', 'basis', 'area', 'unit',
          'limitations', 'name', 'classification', 'type_GUID', 'source_sha256']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_inputs(paths):
    resolved = [Path(p).resolve(strict=True) for p in paths]
    hashes = [sha(p) for p in resolved]
    if len(set(hashes)) != len(hashes):
        raise ValueError('Duplicate input content: choose each unit/floor IFC once.')
    if any(p.suffix.lower() != '.ifc' for p in resolved):
        raise ValueError('Choose saved .ifc files, not .blend display snapshots.')
    return resolved

def curve_points(curve):
    if curve.is_a('IfcPolyline'):
        return [list(p.Coordinates)[:2] for p in curve.Points]
    if curve.is_a('IfcIndexedPolyCurve') and curve.Segments is None:
        return [list(p)[:2] for p in curve.Points.CoordList]
    raise ValueError(f'Unsupported profile curve: {curve.is_a()}; polygon without arcs required')

def projection(product, scale):
    """Union exact vertical swept polygons in world XY, retaining inner holes."""
    reps = [] if product.Representation is None else product.Representation.Representations
    bodies = [r for r in reps if r.RepresentationIdentifier == 'Body']
    if not bodies:
        raise ValueError(f'No Body representation: {product.GlobalId}')
    polygons = []
    product_matrix = placement.get_local_placement(product.ObjectPlacement)
    for rep in bodies:
        for resolved in representation.resolve_items(rep):
            item = resolved['item']
            if not item.is_a('IfcExtrudedAreaSolid'):
                raise ValueError(f'Unsupported solid {item.is_a()}: {product.GlobalId}')
            matrix = product_matrix @ resolved['matrix'] @ placement.get_axis2placement(item.Position)
            direction = matrix[:3, :3] @ np.asarray(item.ExtrudedDirection.DirectionRatios)
            if not np.allclose(direction[:2], 0, atol=1e-10) or not np.allclose(matrix[2, :2], 0, atol=1e-10):
                raise ValueError(f'Inclined profile/extrusion requires a separate method: {product.GlobalId}')
            profile = item.SweptArea
            if not profile.is_a('IfcArbitraryClosedProfileDef'):
                raise ValueError(f'Unsupported profile {profile.is_a()}: {product.GlobalId}')
            def ring(curve):
                return [((matrix @ np.asarray([x, y, 0, 1]))[:2] * scale).tolist()
                        for x, y in curve_points(curve)]
            polygon = Polygon(ring(profile.OuterCurve), [ring(c) for c in getattr(profile, 'InnerCurves', [])])
            if not polygon.is_valid or polygon.area <= 0:
                raise ValueError(f'Invalid source profile: {product.GlobalId}; do not auto-repair silently')
            polygons.append(polygon)
    if not polygons:
        raise ValueError(f'Empty Body representation: {product.GlobalId}')
    return unary_union(polygons)

def storey_of(product):
    direct = element.get_container(product, ifc_class='IfcBuildingStorey')
    if direct:
        return direct
    parent = element.get_aggregate(product)
    seen = set()
    while parent and parent.id() not in seen:
        if parent.is_a('IfcBuildingStorey'):
            return parent
        seen.add(parent.id())
        parent = element.get_aggregate(parent)
    return None

def floor_id(storey):
    return element.get_pset(storey, 'A32Storey', 'FloorId') or storey.Name or storey.GlobalId

def extract(paths):
    result = {'schema': 'area-lab/1', 'area_unit': 'm2', 'rows': [], 'floors': [],
              'unit_slabs': [], 'sources': [], 'limitations': [
                  'Model review areas only; statutory exclusive/common/gross floor area is not certified.',
                  'Space projection, slab projection and source dimension worksheet are different boundaries.',
                  'LANDING and ROOF slabs are separate; ordinary slabs are unioned per storey.',
                  'Only placed occurrences are counted. IfcTypeProduct definitions are never summed.',
                  'No bounding-box, type-name number, missing-space zero, or display-mesh substitution.'
              ]}
    all_guids = set()
    for path in validate_inputs(paths):
        before = sha(path)
        model = ifcopenshell.open(str(path))
        scale = units.calculate_unit_scale(model)
        groups = defaultdict(lambda: defaultdict(list))
        units_by_guid = defaultdict(list)
        space_floor = {}
        for space in model.by_type('IfcSpace'):
            st = storey_of(space)
            space_floor[space.GlobalId] = floor_id(st) if st else 'UNASSIGNED'
        for obj in sorted(model.by_type('IfcSlab') + model.by_type('IfcSpace'), key=lambda o: o.GlobalId):
            if obj.GlobalId in all_guids:
                raise ValueError(f'Duplicate occurrence GUID across inputs: {obj.GlobalId}; do not combine tower and its floors')
            all_guids.add(obj.GlobalId)
            st = storey_of(obj)
            floor = floor_id(st) if st else 'UNASSIGNED'
            typ = element.get_type(obj)
            row = {'inputfile': path.name, 'GUID': obj.GlobalId, 'class': obj.is_a(),
                   'storey': floor, 'name': obj.Name or '', 'area': None, 'unit': 'm2',
                   'type_GUID': typ.GlobalId if typ else '', 'source_sha256': before}
            if obj.is_a('IfcSpace'):
                row['classification'] = 'space'
                if obj.Representation is None:
                    row.update(basis='NO_SPACE_GEOMETRY', limitations='Missing space geometry. Blank area is not zero; use separately labelled contained slab union.')
                else:
                    geom = projection(obj, scale)
                    row.update(basis='SPACE_XY_PROFILE_PROJECTION', area=geom.area,
                               limitations='Model room profile projection; space name does not establish legal area classification.')
                    groups[floor]['spaces'].append(geom)
            else:
                predefined = element.get_predefined_type(obj) or 'NOTDEFINED'
                kind = {'LANDING': 'landing', 'ROOF': 'roof'}.get(predefined, 'floor')
                geom = projection(obj, scale)
                row.update(basis='SLAB_XY_PROFILE_PROJECTION', area=geom.area, classification=kind,
                           limitations='Single placed slab projection; overlaps remain until storey union. Model boundary, not legal room area.')
                groups[floor][kind].append(geom)
                space = element.get_container(obj, ifc_class='IfcSpace')
                if kind == 'floor' and space:
                    units_by_guid[space.GlobalId].append(geom)
            result['rows'].append(row)
        unit_geoms = defaultdict(list)
        unit_sums = defaultdict(float)
        for guid, geoms in sorted(units_by_guid.items()):
            space = model.by_guid(guid)
            geom = unary_union(geoms)
            floor = space_floor[guid]
            unit_geoms[floor].append(geom)
            unit_sums[floor] += geom.area
            props = element.get_pset(space, 'A32Unit') or {}
            result['unit_slabs'].append({'inputfile': path.name, 'GUID': guid, 'storey': floor,
                'name': space.Name or '', 'type_code': props.get('TypeCode', ''),
                'basis': 'CONTAINED_ORDINARY_SLAB_XY_UNION', 'area': geom.area, 'unit': 'm2',
                'slab_occurrences': len(geoms), 'limitations': 'Registered unit slab union; not IfcSpace geometry or statutory exclusive area.'})
        for floor in sorted(set(groups) | set(space_floor.values())):
            kinds = groups[floor]
            ordinary = unary_union(kinds['floor'])
            assigned = unary_union(unit_geoms[floor])
            result['floors'].append({'inputfile': path.name, 'storey': floor,
                'slab_xy_sum_m2': sum(g.area for g in kinds['floor']),
                'floor_xy_union_m2': ordinary.area if kinds['floor'] else None,
                'overlap_removed_m2': sum(g.area for g in kinds['floor']) - ordinary.area if kinds['floor'] else None,
                'registered_unit_sum_m2': unit_sums[floor],
                'registered_unit_union_m2': assigned.area,
                'outside_registered_unit_m2': ordinary.difference(assigned).area if kinds['floor'] else None,
                'landing_xy_union_m2': unary_union(kinds['landing']).area if kinds['landing'] else None,
                'roof_xy_union_m2': unary_union(kinds['roof']).area if kinds['roof'] else None,
                'represented_space_sum_m2': sum(g.area for g in kinds['spaces']) if kinds['spaces'] else None,
                'space_xy_union_m2': unary_union(kinds['spaces']).area if kinds['spaces'] else None,
                'registered_unit_count': len(unit_geoms[floor]),
                'limitations': 'Outside registered unit may include walls/core/unclassified use; not statutory common area.'})
        after = sha(path)
        if before != after:
            raise RuntimeError('Input changed during extraction; results discarded')
        result['sources'].append({'inputfile': path.name, 'sha256_before': before,
            'sha256_after': after, 'source_bytes': path.stat().st_size,
            'ifc_schema': model.schema, 'length_scale_to_m': scale,
            'storey_count': len(model.by_type('IfcBuildingStorey')),
            'space_count': len(model.by_type('IfcSpace')),
            'represented_spaces': sum(s.Representation is not None for s in model.by_type('IfcSpace')),
            'slab_count': len(model.by_type('IfcSlab')),
            'physical_occurrences': len(model.by_type('IfcElement')),
            'type_definitions_excluded': len(model.by_type('IfcTypeProduct'))})
    return result

def csv_write(path, rows, fields=None):
    if not rows:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def write_outputs(result, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'areas.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    csv_write(out / 'objects.csv', result['rows'], FIELDS)
    csv_write(out / 'floors.csv', result['floors'])
    csv_write(out / 'unit-slabs.csv', result['unit_slabs'])
    headers = ['Input IFC', 'Storey', 'Floor XY union (m²)', 'Registered unit slabs (m²)', 'Space geometry']
    cells = []
    for r in result['floors']:
        source = next(s for s in result['sources'] if s['inputfile'] == r['inputfile'])
        values = [r['inputfile'], r['storey'], f"{r['floor_xy_union_m2']:.6f}" if r['floor_xy_union_m2'] is not None else 'n.a.',
                  f"{r['registered_unit_sum_m2']:.6f}" if r['registered_unit_count'] else 'n.a.',
                  f"{source['represented_spaces']} / {source['space_count']}"]
        cells.append('<tr>' + ''.join('<td>' + html.escape(str(v)) + '</td>' for v in values) + '</tr>')
    (out / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>IFC area review</title>'
        '<style>body{font:17px system-ui;margin:40px;color:#192b41;background:#f5f2ec}main{max-width:1100px;margin:auto}'
        'h1{font-size:36px}table{border-collapse:collapse;width:100%;background:white}th{background:#243852;color:white}'
        'td,th{padding:18px;text-align:left;border-bottom:1px solid #d8dfe5}p{line-height:1.6}.note{background:#fff0cc;padding:20px}</style>'
        '<main><h1>Saved IFC area review</h1><p>Read one unit and one floor. Count placed occurrences once.</p><table><thead><tr>'
        + ''.join('<th>' + h + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(cells) + '</tbody></table>'
        '<p class="note">These are model profile projections. A32 unit spaces have no own geometry. Blank space area is missing data, not zero. '
        'Floor, unit slab and room space values describe different boundaries and must not be added together.</p>'
        '<p>CSV and JSON beside this page retain source filename, GUID, class, storey, method, m² and limitations. '
        'The report records SHA256 before and after. This tool never writes IFC or .blend files.</p></main>', encoding='utf8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ifc', nargs='+', type=Path, help='One unit/floor IFC, or several disjoint IFC files')
    parser.add_argument('--out', required=True, type=Path, help='New output folder; existing folders are refused')
    args = parser.parse_args()
    try:
        result = extract(args.ifc)
        write_outputs(result, args.out)
    except (ValueError, RuntimeError, FileExistsError, FileNotFoundError) as exc:
        parser.exit(2, f'Area lab stopped: {exc}\n')
    print(json.dumps({'output': str(args.out), 'sources': result['sources'], 'floors': result['floors']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
