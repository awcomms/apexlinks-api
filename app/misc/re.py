import json
from app.models import Txt

def re(data, txt, arg):
    txts = data(arg)
    if txts:
        if not isinstance(txts, list):
            try:
                txts = json.loads(txts)
            except:
                return {'error': f'let query body parameter `{arg}` be a JSON array'} ,400 #TODO-error
            if not isinstance(txts, list):
                return {'error': f'let query body parameter `{arg}` be a JSON array'}, 400
        for idx, txt_id in enumerate(txts):
            try:
                txt_id = int(txt_id)
            except:
                return {'error': f'let item at index {idx} in query body parameter `{arg}` be an integer'}, 400
            r_txt = Txt.query.get(txt_id)
            if not r_txt:
                return {'error': f'txt {txt_id} not found'}, 404
            res = getattr(txt, arg)(r_txt)
            if res:
                return {'error': f'txt {txt.id} already a reply to txt {txt_id}'}, 400
