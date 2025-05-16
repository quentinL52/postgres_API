import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
from fastapi import FastAPI, Depends

PG_URL = os.getenv('PG_URL')

def get_engine():
    if not PG_URL:
        raise ValueError("L'URL de la base de données (PG_URL) n'est pas définie dans l'environnement.")
    engine = create_engine(PG_URL)
    return engine

def get_db_connection(engine=Depends(get_engine)):
    with engine.connect() as connection:
        yield connection

def load_job_offer(connection):
    query_offre = text('SELECT entreprise, poste, description_poste, id FROM "ML_offres_data"')
    resultats = connection.execute(query_offre).fetchall()
    offres = []
    for row in resultats:
        entreprise, poste, description, id = row
        offres.append({
            "entreprise": entreprise,
            "poste": poste,
            "description": description,
            "id": id
        })
    return offres

def get_job_offer_by_id(connection, offre_id: str):
    query = text('SELECT entreprise, poste, description_poste, id FROM "ML_offres_data"WHERE id = :id')
    result = connection.execute(query, {"id": offre_id}).fetchone()
    if result:
        entreprise, poste, description, id = result
        return {
            "entreprise": entreprise,
            "poste": poste,
            "description": description,
            "id": id
        }
    return None

app = FastAPI()

@app.get("/offre-emploi")
async def read_job_offer(connection = Depends(get_db_connection)):
    offres = load_job_offer(connection)
    if offres:
        return offres
    return {"message": "Aucune offre d'emploi trouvée."}

@app.get("/offre-emploi/{offre_id}")
async def read_job_offer_by_id(offre_id: str, connection = Depends(get_db_connection)):
    offre = get_job_offer_by_id(connection, offre_id)
    if offre:
        return offre
    return {"message": f"Aucune offre trouvée avec l'id {offre_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)