#En aquest arxiu definirem la API que s'encargará de rebre les sol.licituds i procesarlas amb la IA que implementarem més endevant

#Abans de tot, farem servir les llibreries de FastAPI que es una manera fácil i sentzilla de poder crearla
from fastapi import FastAPI
import base64
from pydantic import BaseModel

#Definim l'objecte app qie será el nucli de la nostra API
app = FastAPI()
class MissatgeXifrat(BaseModel):
    missatge: str
#Definim una ruta HTTP GET en la URL "/mensaje", significa que quan algú vulgui accedir a aquesta URL, s'executará la funció de sota
@app.get("/mensaje")
def obtener_mensaje():
    #Definim la següent funció que s'encarregará d'obtindre la solicitud GET a /mensaje, retorna un diccionari amb una clau 'resposta' i un missatje amb valor
    #FastAPI la convirteix automaticament aquest diccionari en format JSON
    return{"resposta":"La api funciona correctamente"}     #Retornem el missatge de que s'ha pogut entrar correctament
@app.get("/missatgeParametres")
def obtenir_missatge_parametres(nom: str, password: int):

    return {"resposta": f"Benvigut {nom}, tens aquesta password: {password}."}  #Retornem un missatge personalitzat amb els paràmetres rebuts
#Per poder fer servir la API en cuestió fem servir "uvicorn fastAPIserver:app --reload" i s'obrirá en local
@app.post("/xifrat")
async def rebre_missatge(dades: MissatgeXifrat):
    try:
        missatge_bytes = base64.b64decode(dades.missatge.encode("utf-8"))
        missatge_desxifrat = missatge_bytes.decode("utf-8")
    except Exception as e:
        return {"error": "No s'ha pogut desxifrar el missatge", "detall":
        str(e)}

    return {
            "estat": "rebut",
            "missatge original": missatge_desxifrat
        }    


