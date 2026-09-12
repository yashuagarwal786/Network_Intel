"""Deterministic fictional records; never imports real personal data."""
import json
from pathlib import Path

def generate():
    nodes = [
        ('p1','Arjun Mehta','Person',160,210),('p2','Neel Rao','Person',730,200),
        ('alias','A. Mehta','Alias',140,60),('ph1','SIM • 0142','Phone',340,150),
        ('ph2','SIM • 0287','Phone',550,150),('a1','Account • 4102','Account',320,330),
        ('a2','Account • 8821','Account',560,330),('v1','DEMO-VH-07','Vehicle',730,390),
        ('loc','Rivergate depot','Location',760,540),('org','Mira Logistics','Organization',470,510)]
    entities=[dict(id=i,label=l,type=t,x=x,y=y,description=f'Fictional {t.lower()} record in Operation Trinetra.') for i,l,t,x,y in nodes]
    evidence=[]; edges=[]
    def add(eid,kind,file,locator,time,excerpt,source,target,relation,status='recorded'):
        evidence.append(dict(id=eid,kind=kind,file=file,locator=locator,timestamp=time,excerpt=excerpt,synthetic=True))
        edges.append(dict(id='r'+eid[1:],source=source,target=target,type=relation,status=status,evidence_ids=[eid],timestamp=time))
    add('E001','Report','field-report-01.txt','paragraph 3','2026-08-14T08:00:00+05:30','The interview log lists Arjun Mehta with demonstration SIM 0142. Identity has not been independently verified.','p1','ph1','listed phone')
    add('E002','Report','field-report-02.txt','paragraph 2','2026-08-14T08:15:00+05:30','The contact sheet lists Neel Rao with demonstration SIM 0287.','p2','ph2','listed phone')
    add('E003','Transaction','account-register.csv','row 2 · account_holder','2026-08-14T09:00:00+05:30','DEMO account 4102 holder: Arjun Mehta.','p1','a1','account holder')
    add('E004','Transaction','account-register.csv','row 3 · account_holder','2026-08-14T09:00:00+05:30','DEMO account 8821 holder: Neel Rao.','p2','a2','account holder')
    for n,minute in enumerate([10,18,26]):
        add(f'E00{5+n}','CDR','cdr-20260815.csv',f'row {n+2} · caller, callee, start','2026-08-15T21:'+str(minute)+':00+05:30',f'SIM 0142 → SIM 0287; 21:{minute} IST; duration {80+n*20} seconds. Call content is unavailable.','ph1','ph2','call')
    add('E008','Transaction','transfers-20260815.csv','row 2 · sender, receiver, amount, time','2026-08-15T21:42:00+05:30','DEMO account 4102 → DEMO account 8821; INR 48,000; 21:42 IST; purpose unspecified.','a1','a2','transfer')
    add('E009','Vehicle','vehicle-register.csv','row 2 · keeper','2026-08-14T10:00:00+05:30','DEMO-VH-07 registered keeper: Neel Rao. Keeper is not necessarily the driver.','p2','v1','registered keeper')
    add('E010','Vehicle','vehicle-observations.csv','row 2 · vehicle, location, time','2026-08-15T22:05:00+05:30','DEMO-VH-07 logged at Rivergate depot at 22:05 IST. Occupants unknown.','v1','loc','observed at')
    add('E011','Report','site-register.txt','paragraph 1','2026-08-14T11:00:00+05:30','Mira Logistics is listed as tenant of Rivergate depot.','org','loc','listed tenant')
    add('E012','Report','delivery-note.txt','paragraph 4','2026-08-15T17:00:00+05:30','A. Mehta appears as delivery contact for Mira Logistics. No unique identifier supplied.','alias','org','delivery contact')
    # A candidate is explicitly inferred; review never silently merges entities.
    evidence.append(dict(id='E013',kind='Report',file='delivery-note.txt',locator='paragraph 4 · contact name',timestamp='2026-08-15T17:00:00+05:30',excerpt='Contact name: A. Mehta. This initial and surname could match multiple people.',synthetic=True))
    edges.append(dict(id='r13',source='alias',target='p1',type='possible alias',status='inferred',evidence_ids=['E001','E013'],timestamp='2026-08-15T17:00:00+05:30'))
    return dict(case=dict(id='trinetra',name='Operation Trinetra',reference='TRN / 2026 / 018',synthetic=True),entities=entities,evidence=evidence,edges=edges,aliases=[dict(id='alias-01',left='alias',right='p1',evidence_ids=['E001','E013'],reason='Same surname and compatible first initial. No shared unique identifier; insufficient evidence to merge.')])

if __name__=='__main__':
    Path(__file__).with_name('data').joinpath('trinetra.json').write_text(json.dumps(generate(),indent=2),encoding='utf-8')
