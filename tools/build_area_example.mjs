// Instructor authoring only. Students run area_extract.py and import its UTF-8 CSV.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const lab=path.resolve(here,'../area-lab');
const out=path.join(lab,'example-output');
const data=JSON.parse(await fs.readFile(path.join(out,'areas.json'),'utf8'));
const dimensions=JSON.parse(await fs.readFile(path.join(lab,'source-dimensions.json'),'utf8'));
const wb=Workbook.create();
const summary=wb.worksheets.add('Area review');
const objects=wb.worksheets.add('IFC objects');
const unit=wb.worksheets.add('Unit slabs');
const dimension=wb.worksheets.add('Source dimensions');
const navy='#243852',muted='#58677B',light='#EDF1F5',amber='#FFF0CC',ink='#172B44';
function base(s,lastRow,lastCol){s.showGridLines=false;s.getRange(`A1:${lastCol}${lastRow}`).format.font={name:'Malgun Gothic',size:11,color:ink};s.getRange(`A1:${lastCol}${lastRow}`).format.rowHeight=27;s.getRange(`A1:${lastCol}${lastRow}`).format.verticalAlignment='center';}
function header(s,range){const r=s.getRange(range);r.format.fill=navy;r.format.font={name:'Malgun Gothic',size:11,bold:true,color:'#FFFFFF'};r.format.rowHeight=39;r.format.wrapText=true;}
function widths(s,obj){for(const [c,w]of Object.entries(obj))s.getRange(`${c}:${c}`).format.columnWidth=w;}
base(summary,27,'G');widths(summary,{A:3,B:24,C:22,D:23,E:22,F:20,G:43});
summary.getRange('B2').values=[['IFC area review']];summary.getRange('B2').format.font={name:'Malgun Gothic',size:17,bold:true,color:navy};summary.getRange('B3').values=[['One unit + one floor. Saved geometry, read only.']];summary.getRange('B3').format.font.color=muted;
summary.getRange('B5:G5').values=[['IFC file','Floor XY union\n(m²)','Registered unit slabs\n(m²)','Outside unit slabs\n(m²)','Spaces with geometry','Area boundary']];header(summary,'B5:G5');
summary.getRange('B6:G7').values=data.floors.map((r,i)=>[r.inputfile,r.floor_xy_union_m2,r.registered_unit_count?r.registered_unit_sum_m2:'n.a.',r.registered_unit_count?r.outside_registered_unit_m2:'n.a.',`${data.sources[i].represented_spaces} / ${data.sources[i].space_count}`,i===0?'Standalone unit slabs':'14 registered unit slabs + other floor']);
summary.getRange('C6:E7').setNumberFormat('#,##0.000000');summary.getRange('B6:G7').format.rowHeight=40;
summary.getRange('B9:G9').values=[['Separate observations','Area (m²)','Count','Source','Method','Meaning']];header(summary,'B9:G9');
const slabLast=6+data.rows.length;
summary.getRange('B10:G12').values=[['25B room spaces',null,5,'25B.ifc','Space profile sum','Different boundary from slab union'],['A32-05 room spaces','n.a.',14,'A32-05.ifc','No representation','Missing area, not zero'],['A32-05 landings',data.floors[1].landing_xy_union_m2,4,'A32-05.ifc','Separate XY union','Excluded from ordinary floor union']];
summary.getRange('C10').formulas=[[`=SUMIFS('IFC objects'!$F$7:$F$${slabLast},'IFC objects'!$A$7:$A$${slabLast},"25B.ifc",'IFC objects'!$C$7:$C$${slabLast},"IfcSpace")`]];
summary.getRange('C10:C12').setNumberFormat('#,##0.000000');
summary.getRange('B14').values=[['Different boundaries: do not add the rows together.']];summary.getRange('B14:G14').format.fill=amber;summary.getRange('B14:G14').format.rowHeight=33;
summary.getRange('B16').values=[['Space projection']];summary.getRange('C16').values=[['Placed IfcSpace profile. Some spaces are identifiers without geometry.']];
summary.getRange('B17').values=[['Slab projection']];summary.getRange('C17').values=[['Union of ordinary slab profiles per storey. No bbox or display-mesh substitution.']];
summary.getRange('B18').values=[['Source dimensions']];summary.getRange('C18').values=[['A32 25-type drawing worksheet is separate from standalone 25B and IFC geometry.']];
summary.getRange('B19').values=[['Legal areas']];summary.getRange('C19').values=[['Exclusive / common / gross statutory boundaries are not certified here.']];
summary.getRange('B21').values=[['A32 unit sum from detail']];summary.getRange('C21').formulas=[['=SUM(\'Unit slabs\'!F7:F20)']];summary.getRange('C21').setNumberFormat('#,##0.000000');
summary.getRange('B22').values=[['Reconciliation (m²)']];summary.getRange('C22').formulas=[['=C7-D7-E7']];summary.getRange('C22').setNumberFormat('0.000000');summary.getRange('D22').values=[['Expected 0 within 0.0000001 m²']];
summary.getRange('B24').values=[['Count occurrences']];summary.getRange('C24').values=[['56 slabs + 19 spaces. Type definitions excluded.']];
summary.getRange('B25').values=[['Read-only check']];summary.getRange('C25').values=[['Both SHA256 values unchanged before / after extraction.']];
summary.getRange('B26').values=[['IFC source records']];summary.getRange('C26').values=[['Full hashes and filenames are in IFC objects and areas.json.']];
summary.tabColor=navy;

const fields=['inputfile','GUID','class','storey','basis','area','unit','limitations','name','classification','type_GUID','source_sha256'];
base(objects,slabLast,'L');widths(objects,{A:19,B:31,C:15,D:27,E:42,F:17,G:9,H:85,I:46,J:16,K:31,L:68});
objects.getRange('A2').values=[['IFC object observations']];objects.getRange('A3').values=[['One occurrence per row. Blank area means missing geometry. Do not sum slab and space classes together.']];objects.getRange('A5').values=[['Source: 25B library 20261019-v1 (25B-v002) and A32 v011 single floor 05. Full provenance in areas.json.']];
objects.getRange('A6:L6').values=[fields];objects.getRange(`A7:L${slabLast}`).values=data.rows.map(r=>fields.map(k=>r[k]??null));header(objects,'A6:L6');objects.getRange(`F7:F${slabLast}`).setNumberFormat('#,##0.000000');objects.getRange(`D7:D${slabLast}`).setNumberFormat('@');objects.freezePanes.freezeRows(6);objects.freezePanes.freezeColumns(2);
const t=objects.tables.add(`A6:L${slabLast}`,true,'ObjectAreas');t.showFilterButton=true;objects.getRange(`A7:L${slabLast}`).format.fill='#FFFFFF';

const uFields=['inputfile','GUID','storey','name','basis','area','unit','slab_occurrences','type_code','limitations'];
base(unit,22,'J');widths(unit,{A:19,B:31,C:12,D:27,E:44,F:19,G:9,H:19,I:13,J:90});unit.getRange('A2').values=[['Registered unit slab unions']];unit.getRange('A3').values=[['A32-05 spaces identify units but have no own geometry. Each union uses its contained ordinary slabs.']];unit.getRange('A6:J6').values=[uFields];unit.getRange('A7:J20').values=data.unit_slabs.map(r=>uFields.map(k=>r[k]??null));header(unit,'A6:J6');unit.getRange('F7:F20').setNumberFormat('#,##0.000000');unit.getRange('C7:C20').setNumberFormat('@');unit.freezePanes.freezeRows(6);unit.getRange('E22').values=[['Sum (m²)']];unit.getRange('F22').formulas=[['=SUM(F7:F20)']];unit.getRange('F22').setNumberFormat('#,##0.000000');

base(dimension,22,'H');widths(dimension,{A:3,B:18,C:16,D:17,E:17,F:20,G:25,H:45});
dimension.getRange('B2').values=[['A32 25-type source dimensions']];dimension.getRange('B3').values=[['Drawing A17-001, architecture PDF page 31. This is not standalone 25B.']];dimension.getRange('B4').values=[['Manual drawing dimension worksheet; separate from IFC-space and slab measurements.']];
dimension.getRange('B6:H6').values=[['Room','Zone','Width (m)','Height (m)','Area (m²)','Basis','Limitation']];header(dimension,'B6:H6');
dimension.getRange('B7:H13').values=dimensions.net_zones.map(z=>[z.room,z.zone,z.w,z.h,null,'Drawing dimensions','Printed dimension boundary; not IFC measurement']);
dimension.getRange('F7:F13').formulas=dimensions.net_zones.map((z,i)=>[`=D${i+7}*E${i+7}`]);dimension.getRange('D7:F15').setNumberFormat('0.000000');dimension.getRange('D7:E13').format.fill=amber;
dimension.getRange('E15').values=[['Sum (m²)']];dimension.getRange('F15').formulas=[['=SUM(F7:F13)']];dimension.getRange('B17').values=[['Dimension cells are editable. Area cells recalculate with width × height.']];dimension.getRange('B18').values=[['Do not compare A32 25-type directly to standalone 25B; type names do not supply areas.']];dimension.getRange('B20').values=[['Source PDF SHA256']];dimension.getRange('C20').values=[[dimensions.pdf_sha256]];
wb.recalculate();
const expected=23.7256;
if(Math.abs(summary.getRange('C10').values[0][0]-expected)>1e-8)throw Error('Space sum formula does not match source');
if(Math.abs(summary.getRange('C21').values[0][0]-data.floors[1].registered_unit_sum_m2)>1e-7)throw Error('Unit formula mismatch');
const originalWidth=dimension.getRange('D7').values[0][0],originalTotal=dimension.getRange('F15').values[0][0];
dimension.getRange('D7').values=[[originalWidth+1]];wb.recalculate();
if(Math.abs(dimension.getRange('F15').values[0][0]-originalTotal-dimensions.net_zones[0].h)>1e-8)throw Error('Dimension edit failed');
dimension.getRange('D7').values=[[originalWidth]];wb.recalculate();
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'area lab error scan'});
await fs.writeFile(path.join(out,'workbook-error-scan.ndjson'),err.ndjson);
await fs.writeFile(path.join(out,'workbook-inspection.ndjson'),(await wb.inspect({kind:'table',range:'Area review!B5:G12',include:'values,formulas',tableMaxRows:8,tableMaxCols:6})).ndjson);
for(const [s,range,name]of [[summary,'B2:G26','area-summary'],[objects,'A6:G15','object-table'],[unit,'A6:I12','unit-table'],[dimension,'B2:H18','dimension-table']]){
 const blob=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(path.join(out,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await(await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'IFC-area-review.xlsx'));
await fs.writeFile(path.join(out,'workbook-verification.json'),JSON.stringify({formula_space_sum_m2:summary.getRange('C10').values[0][0],formula_unit_sum_m2:summary.getRange('C21').values[0][0],drawing_dimension_sum_m2:dimension.getRange('F15').values[0][0],dimension_input_change_and_restore:true,ifc_sources_unchanged:data.sources.every(s=>s.sha256_before===s.sha256_after),native_excel_recalculation_tested:false},null,2));
console.log(JSON.stringify({output:'IFC-area-review.xlsx',space_m2:summary.getRange('C10').values[0][0],unit_slabs_m2:summary.getRange('C21').values[0][0],drawing_m2:dimension.getRange('F15').values[0][0]}));

