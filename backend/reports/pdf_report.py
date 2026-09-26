from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from html import escape

def generate_pdf_report(query, response, output_path, trace=None):
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    styles=getSampleStyleSheet(); small=ParagraphStyle('small',parent=styles['BodyText'],fontSize=8,textColor=colors.grey)
    ev=response.evidence
    story=[Paragraph('SatQuery AI — Analysis Report',styles['Title']),Paragraph(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),small),Spacer(1,12),Paragraph('Query',styles['Heading2']),Paragraph(escape(query),styles['BodyText']),Spacer(1,10),Paragraph('Answer',styles['Heading2']),Paragraph(escape(response.answer_text),styles['BodyText']),Spacer(1,10),Paragraph('Execution evidence',styles['Heading2'])]
    rows=[['Task',getattr(ev.task,'value',str(ev.task))],['Model(s)',escape(ev.model_used)],['Modalities',', '.join(getattr(m,'value',str(m)) for m in ev.modality_used)],['Confidence',f'{ev.confidence.band}'+(f' ({ev.confidence.value:.3f})' if ev.confidence.value is not None else '')],['Basis',escape(ev.confidence.basis)]]
    for k,v in ev.stats.items(): rows.append([escape(k.replace('_',' ')),f'{v:.4f}'])
    if ev.change_map: rows += [['Changed pixels',str(ev.change_map.changed_area_px)],['Changed area %',f'{ev.change_map.changed_area_pct:.4f}'],['Change mean confidence',f'{ev.change_map.mean_confidence:.4f}']]
    t=Table(rows,colWidths=[1.9*72,4.5*72]); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.lightgrey),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story += [t,Spacer(1,10)]
    if ev.detections:
        story += [Paragraph('Grounded detections',styles['Heading2']),Table([['Label','Score','Box']]+[[escape(d.label),f'{d.score:.3f}',', '.join(f'{x:.1f}' for x in d.box_px)] for d in ev.detections],colWidths=[2.0*72,1.0*72,3.4*72])]
    if ev.warnings:
        story += [Spacer(1,10),Paragraph('Warnings',styles['Heading2'])]+[Paragraph('• '+escape(w),styles['BodyText']) for w in ev.warnings]
    if trace:
        story += [Spacer(1,10),Paragraph('Auditable execution trace',styles['Heading2'])]
        for step in trace.get('steps',[]): story.append(Paragraph(escape(str(step)),small))
    Path(output_path).parent.mkdir(parents=True,exist_ok=True); SimpleDocTemplate(output_path,pagesize=LETTER).build(story); return output_path
