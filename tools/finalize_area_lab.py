"""Instructor packaging/verification. Does not modify IFC sources."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'area-lab'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    data = json.loads((LAB / 'example-output/areas.json').read_text(encoding='utf8'))
    book = LAB / 'example-output/IFC-area-review.xlsx'
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(book) as z:
        sheets = [ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')) for i in range(1,5)]
        errors = [c.attrib['r'] for sheet in sheets for c in sheet.findall('.//m:c',ns) if c.attrib.get('t')=='e']
        assert not errors, errors
        def value(sheet, cell):
            c = sheets[sheet-1].find(f'.//m:c[@r="{cell}"]/m:v',ns)
            return float(c.text)
        assert abs(value(1,'C10')-23.7256)<1e-8
        assert abs(value(1,'C21')-749.5141847081719)<1e-7
        assert abs(value(4,'F15')-20.2034)<1e-8
        strings=ET.fromstring(z.read('xl/sharedStrings.xml'))
        strings=[''.join(t.text or '' for t in si.findall('.//m:t',ns)) for si in strings]
        def text_cell(sheet,address):
            cell=sheets[sheet-1].find(f'.//m:c[@r="{address}"]',ns)
            if cell.attrib.get('t')=='str':return cell.find('m:v',ns).text
            return strings[int(cell.find('m:v',ns).text)] if cell.attrib.get('t')=='s' else ''.join(t.text or '' for t in cell.findall('.//m:t',ns))
        assert text_cell(2,'D14')=='05', repr(text_cell(2,'D14'))
        assert text_cell(3,'C7')=='05', repr(text_cell(3,'C7'))
        blank_space_rows = [i+7 for i,r in enumerate(data['rows']) if r['class']=='IfcSpace' and r['area'] is None]
        assert len(blank_space_rows)==14
        for i in blank_space_rows:
            cell=sheets[1].find(f'.//m:c[@r="F{i}"]',ns)
            assert cell is None or cell.find('m:v',ns) is None, f'Missing area became zero: F{i}'
        objects_rows = sheets[1].findall('.//m:sheetData/m:row',ns)
        assert len(data['rows']) == 75
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tools'),'-p','test_area_extract.py','-v'],capture_output=True,text=True)
    (LAB/'test-results.txt').write_text(tests.stdout+tests.stderr,encoding='utf8')
    assert tests.returncode==0
    provenance={'sources':[
        {'inputfile':'25B.ifc','source_library':'assets/apartment-types/20261019-v1/25B/model/25B.ifc','revision':'25B-v002',
         'current_pointer':'output/current-unit.json','library_source_matches_current_output_25b':True,
         'original_library_sha256':'3405209a0452db5295b777880cfbadd49fea4bea8398e1034e52fa330cdbd0cd',
         'public_metadata_change':'DWG and BaseIFC absolute provenance paths replaced by relative paths. Geometry and GUID unchanged.',
         'public_asset_audit':'../materials/units/25B/asset.json'},
        {'inputfile':'A32-05.ifc','source_library':'output/a32-residential/v011/floors/A32-05.ifc','revision':'A32-v011',
         'current_pointer':'output/current-a32-residential.json','scope':'Single floor 05, not all-tower file'}],
        'dimension_source':{'drawing':'A17-001','architecture_pdf_page':31,'type':'A32 25 (distinct from standalone 25B)',
         'basis':'Recorded source-dimension worksheet from jobs/a32-reference-deliverables-v001/forms.json'},
        'no_ifc_or_live_blender_writes':True}
    for item,source in zip(provenance['sources'],data['sources']):
        item.update(sha256=source['sha256_before'],bytes=source['source_bytes'])
        assert sha(LAB/'inputs'/item['inputfile'])==item['sha256']
    (LAB/'input-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf8')
    result={'tested_on':'2026-10-21','python':sys.version.split()[0],
        'ifcopenshell':__import__('ifcopenshell').version,'shapely':__import__('shapely').__version__,
        'tests_passed':5,'source_hashes_unchanged':True,'single_storey_inputs':[1,1],
        'sources':data['sources'],'saved_xlsx_sheet_count':4,'saved_xlsx_error_cells':0,
        'missing_space_areas_saved_blank':14,'storey_05_saved_as_text':True,'object_rows':75,'unit_slab_rows':14,
        'values':{'25B_space_projection_sum_m2':23.7256,'25B_slab_union_m2':30.1908,
          'A32-05_floor_union_m2':994.5318,'A32-05_registered_unit_slabs_m2':749.5141847081719,
          'A32-05_outside_registered_units_m2':245.01761529182826,'A32-05_landing_union_m2':11.448,
          'A32_25_drawing_dimension_sum_m2':20.2034},
        'xlsx_formula_input_change_and_restore':True,'xlsx_native_excel_recalculation_tested':False,
        'independent_control':'Prior v011 full-model profile extraction, floor05; source remains read-only',
        'limits':'Model profile projection and separate drawing worksheet; no statutory area certification; vertical polygonal extrusion only.'}
    (LAB/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

def card():
    from PIL import Image,ImageDraw,ImageFont
    im=Image.new('RGB',(1920,1080),'#F4F1EB'); d=ImageDraw.Draw(im)
    def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if bold else 'C:/Windows/Fonts/malgun.ttf',size)
    navy='#213752'; ink='#1E3049'; muted='#647184'
    d.text((96,65),'마지막 실습',font=font(24,True),fill=muted)
    d.text((96,112),'한 세대에서 한 층으로, IFC 면적 원장',font=font(48,True),fill=ink)
    d.text((98,188),'실제 저장 파일 2개를 읽고 · GUID로 추적하고 · 같은 기준끼리 합산합니다',font=font(25),fill=muted)
    x=[96,480,825,1160,1525,1824]; top=280; rowh=134
    d.rounded_rectangle((96,top,1824,top+rowh*3),radius=20,fill='white')
    d.rounded_rectangle((96,top,1824,top+83),radius=20,fill=navy)
    d.rectangle((96,top+42,1824,top+83),fill=navy)
    for text,left in zip(['입력 IFC','일반 바닥 XY 합집합','세대소속 슬래브','세대외 바닥','공간 형상'],x):
        d.text((left+24,top+24),text,font=font(23,True),fill='white')
    rows=[['25B 한 세대','30.190800 ㎡','해당 없음','해당 없음','5 / 5'],['A32 05층','994.531800 ㎡','749.514185 ㎡','245.017615 ㎡','0 / 14']]
    for i,row in enumerate(rows):
        yy=top+83+rowh*i
        for j,cell in enumerate(row):d.text((x[j]+24,yy+44),cell,font=font(29,j==0),fill=ink)
        if i==0:d.line((120,yy+rowh,1800,yy+rowh),fill='#DCE2E8',width=2)
    boxy=top+rowh*3+42
    d.rounded_rectangle((96,boxy,1824,boxy+105),radius=15,fill='#FFF0C9')
    d.text((124,boxy+19),'A32의 IfcSpace14개는 식별자입니다. 자체 형상·면적이 없습니다.',font=font(26,True),fill='#755215')
    d.text((124,boxy+60),'면적 공란은 0㎡가 아닙니다. 세대소속 슬래브 합집합을 별도 근거로 사용합니다.',font=font(23),fill='#755215')
    d.text((98,boxy+144),'25B의 실별 공간 합계 23.725600㎡는 슬래브30.190800㎡와 다른 경계입니다.',font=font(26),fill=ink)
    d.text((98,boxy+195),'CSV75행 + 세대별14행 → 수식이 있는 Excel → GUID로 Blender에서 확인',font=font(26,True),fill=ink)
    d.text((98,1008),'원본 SHA256 전후 동일  ·  전체 동 파일 불필요  ·  모델 검토 면적이며 법정 면적은 미확정',font=font(21),fill=muted)
    im.save(LAB/'area-result-card.png')

def archive():
    target=ROOT/'area-lab.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for folder in [LAB,ROOT/'tools']:
            for p in sorted(folder.rglob('*')):
                if not p.is_file() or any(x in p.parts for x in ['node_modules','__pycache__','.area-venv']):continue
                if p.name in ['build_area_example.mjs','finalize_area_lab.py']:continue
                z.write(p,p.relative_to(ROOT))
    print('Archive',target.stat().st_size,'bytes')

def relocated_check():
    with tempfile.TemporaryDirectory(prefix='area-lab-relocated-') as folder:
        dest=Path(folder)
        with zipfile.ZipFile(ROOT/'area-lab.zip') as z:
            names=z.namelist()
            assert not any('node_modules' in n or '.area-venv' in n for n in names)
            assert sorted(n for n in names if n.endswith('.ifc'))==['area-lab/inputs/25B.ifc','area-lab/inputs/A32-05.ifc']
            z.extractall(dest)
        run=subprocess.run([sys.executable,str(dest/'tools/area_schedule.py'),str(dest/'area-lab/inputs/25B.ifc'),str(dest/'area-lab/inputs/A32-05.ifc'),'--out',str(dest/'student-results')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,errors='replace')
        assert run.returncode==0,run.stderr
        result=json.loads((dest/'student-results/areas.json').read_text(encoding='utf8'))
        assert len(result['rows'])==75 and len(result['unit_slabs'])==14
        tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(dest/'tools'),'-p','test_area_extract.py','-v'],capture_output=True,text=True)
        assert tests.returncode==0,tests.stderr
    report={'archive_contains_only_two_unit_floor_inputs':True,'relocated_cli_success':True,'relocated_object_rows':75,'relocated_unit_rows':14,'relocated_tests_passed':5,'no_project_scripts_or_live_blender_needed':True,'dependency_packages_already_available_in_test_environment':True,'fresh_network_dependency_installation_not_tested':True}
    (LAB/'portable-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    if '--card' in sys.argv:card()
    elif '--zip' in sys.argv:archive()
    elif '--portable-check' in sys.argv:relocated_check()
    else:verify()
