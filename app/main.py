import os
import uvicorn
import json
from fastapi import FastAPI, Request, Form
from app.message_handler import parse_nested_form, process_request_data
from app.kommo_service.validate_stage_kommo import validate_stage_kommo
from app.kommo_service.add_message import add_message

app = FastAPI()

# Ruta webhook
@app.post("/add_message")
async def webhook(request: Request):
    try:
        form = await request.form()
        data = parse_nested_form(form)

        # Imprimir detalles completos del request
        print("\n🚀 DETALLES COMPLETOS DEL REQUEST 🚀")
        
        # Método y URL
        print("\n📡 Básicos:")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Base URL: {request.base_url}")
        print(f"Path: {request.url.path}")
        print(f"Query Params: {dict(request.query_params)}")

        # Headers
        print("\n📋 Headers:")
        for name, value in request.headers.items():
            print(f"{name}: {value}")

        # Cookies
        print("\n🍪 Cookies:")
        for key, value in request.cookies.items():
            print(f"{key}: {value}")

        # Client
        print("\n🌐 Client Info:")
        print(f"Client Host: {request.client.host}")
        print(f"Client Port: {request.client.port}")

        # Form Data
        print("\n📦 Form Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        print("\n🔚 FIN DETALLES REQUEST\n")

        msg = data["message"]["add"][0]
        lead_id = int(msg["entity_id"])

        try:
            is_valid = validate_stage_kommo(lead_id)
            if not is_valid:
                return {"status": "error", "message": "Lead no está en la etapa o pipeline permitidos."}
        except Exception as e:
            return {"status": "error", "message": f"Error validando etapa Kommo: {e}"}

        processed = await process_request_data(data)
        
        add_message_result = add_message(processed["lead_id"], processed["text"])
        if add_message_result["status"] == "error":
            return add_message_result
        else:
            print(f"Mensaje agregado: {processed['text']}")

        print(f"Mensaje agregado correctamente al lead {lead_id}")

        return {"status": "ok"}

    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)