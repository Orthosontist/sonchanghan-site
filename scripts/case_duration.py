"""Use the author's treatment record, never the dates printed on photos."""
import html

def label(data):
    months=data.get('duration_months')
    if months is None:return '원문 미기재'
    if isinstance(months,bool) or not isinstance(months,int) or months<0:
        raise ValueError('Treatment duration must be a non-negative integer or null')
    years,remainder=divmod(months,12)
    parts=([f'{years}년'] if years else [])+([f'{remainder}개월'] if remainder or not years else [])
    return ('약 ' if data.get('duration_approximate') else '')+' '.join(parts)

def markup(data):
    if data.get('category')!='case':return ''
    note=data.get('duration_note') or ''
    return '<div class="case-duration"><span>치료 기간</span><strong>'+html.escape(label(data))+'</strong>'+('<small>'+html.escape(note)+'</small>' if note else '')+'</div>'
