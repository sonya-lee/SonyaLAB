from app.core.config import settings
from app.modules.paper_explorer.models import PaperLibraryPatch, PaperLibraryUpsert
from app.modules.paper_explorer.service import persist_search_results, patch_library, upsert_library

def paper():
    return {"provider":"crossref","external_id":"10.1/test","doi":"10.1/test","title":"Test paper","abstract":"Abstract","authors":["A Author"],"journal":"Journal","year":2026,"url":"https://doi.org/10.1/test","citation_count":3,"metadata_sources":{"bibliographic":"crossref"},"ranking_components":{"total":.8}}

def test_duplicate_doi_and_library_workflow(db):
    results=[paper()]; assert persist_search_results(db,results)==(1,0); assert persist_search_results(db,[paper()])==(0,1)
    item=upsert_library(db,PaperLibraryUpsert(paper_id=results[0]["id"],favorite=True,tags=["반도체"],note="읽기"),settings.single_user_id)
    changed=patch_library(db,item["id"],PaperLibraryPatch(favorite=False,reading_status="read",tags=["표면"]),settings.single_user_id)
    assert not changed["favorite"] and changed["reading_status"]=="read" and changed["tags_json"]==["표면"]

def test_library_item_can_be_removed_without_deleting_paper(db):
    from app.db.models import PaperLibraryItemRecord, PaperRecord
    results=[paper()]; persist_search_results(db,results)
    item=upsert_library(db,PaperLibraryUpsert(paper_id=results[0]["id"]),settings.single_user_id)
    record=db.get(PaperLibraryItemRecord,item["id"]); db.delete(record); db.commit()
    assert db.get(PaperLibraryItemRecord,item["id"]) is None
    assert db.get(PaperRecord,results[0]["id"]) is not None
