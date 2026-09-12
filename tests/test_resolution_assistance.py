from copy import deepcopy
from backend.demo_repository import DemoRepository
from backend.resolution import candidates,proposals


def person(repo,source_id,new_id,label):
    repo.entities[new_id]=repo.entities[source_id].model_copy(update={'id':new_id,'label':label,'display_label':label,'identifier':label,'evidence_ids':['E-SUB-01']})


def relation(repo,source_id,new_id,person_id,target_id):
    repo.relationships[new_id]=repo.relationships[source_id].model_copy(update={'id':new_id,'source':person_id,'target':target_id,'evidence_ids':['E-SUB-01']})


def test_abbreviated_names_are_suggested_but_not_auto_merged():
    repo=deepcopy(DemoRepository())
    person(repo,'rahul','imran-full','Imran Sheikh')
    person(repo,'vikram','imran-short','Imran S.')
    pair=next((a,b) for a,b in candidates(repo) if {a.id,b.id}=={'imran-full','imran-short'})
    proposal=next(p for p in proposals(repo).values() if {p.left_entity_id,p.right_entity_id}=={'imran-full','imran-short'})
    assert pair and proposal.recommendation=='REVIEW'
    assert proposal.strong_identifier_matches==[]
    assert 'no strong identifier' in proposal.match_reason


def test_two_exact_identifiers_create_strong_suggestion_not_merge():
    repo=deepcopy(DemoRepository())
    person(repo,'rahul','imran-full','Imran Sheikh')
    person(repo,'vikram','imran-initial','I. Sheikh')
    relation(repo,'R01','R-IM-P1','imran-full','P101')
    relation(repo,'R01','R-IM-P2','imran-initial','P101')
    relation(repo,'R04','R-IM-A1','imran-full','A17')
    relation(repo,'R04','R-IM-A2','imran-initial','A17')
    proposal=next(p for p in proposals(repo).values() if {p.left_entity_id,p.right_entity_id}=={'imran-full','imran-initial'})
    assert proposal.recommendation=='YES'
    assert {'Phone','Account'}<=set(proposal.strong_identifier_matches)
    assert 'same phone' in proposal.match_reason and 'same account' in proposal.match_reason
    assert len(repo.entities)==44  # Suggestions never mutate the graph.
