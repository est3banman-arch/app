import os
import json
import uuid
from datetime import datetime
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# ⚠️ ¡OJO AQUÍ! He dejado los valores por defecto de tu compañero, 
# pero tendrás que poner los de la base de datos de la UVa.
DB_CONFIG = {
    "host": "gpu2itap.uva.es",
    "user": "root",
    "password": "eiarob_SID", 
    "database": "eiarob_db_nuevo",
}

BT_CATALOG = {
    "BT_move_dest_speak": {
        "topic": "planner/input/movement_media/BT_move_dest_speak",
        "required": ["sender", "receiver", "location", "speech", "volume"],
    },
    "BT_ChatGPT": {
        "topic": "planner/input/movement_media/BT_ChatGPT",
        "required": ["sender", "receiver", "location", "speech", "volume"],
        "optional": ["user"],
    },
    "BT_despertar": {
        "topic": "planner/input/movement_media/BT_despertar",
        "required": ["sender", "receiver", "location", "volume"],
    },
}

ALLOWED_STATES = {"activo", "deshabilitado", "eliminado"}
ALLOWED_MODES = {"single", "restart", "queued", "parallel"}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def parse_json_field(value, default):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)

def estado_to_activo(estado):
    return 1 if estado == "activo" else 0

def normalize_hora(hora):
    if not hora:
        raise ValueError("La hora es obligatoria")
    partes = hora.split(":")
    if len(partes) == 2:
        hora = f"{hora}:00"
    datetime.strptime(hora, "%H:%M:%S")
    return hora

def build_trigger(data):
    trigger = data.get("trigger", {})
    tipo = trigger.get("tipo", "time")
    
    if tipo == "time":
        hora = normalize_hora(trigger.get("hora"))
        trigger_config = {"trigger": "time", "at": hora}
        dias = trigger.get("dias") or []
        condiciones = []
        if dias:
            condiciones.append({
                "condition": "time",
                "weekday": dias,
            })
        return "time", trigger_config, condiciones
        
    if tipo == "time_pattern":
        minutes = trigger.get("minutes")
        if not minutes:
            raise ValueError("time_pattern requiere minutes")
        return "time_pattern", {"trigger": "time_pattern", "minutes": minutes}, []
        
    if tipo == "state":
        entity_id = trigger.get("entity_id")
        to = trigger.get("to")
        if not entity_id:
            raise ValueError("state requiere entity_id")
        config = {
            "trigger": "state",
            "entity_id": entity_id,
        }
        if to is not None:
            config["to"] = to
        return "state", config, []
        
    raise ValueError(f"Trigger no soportado: {tipo}")

def build_payload_and_topic(data):
    accion = data.get("accion", {})
    tipo = accion.get("tipo")
    
    if tipo not in BT_CATALOG:
        raise ValueError(f"Accion no soportada: {tipo}")
        
    catalog_entry = BT_CATALOG[tipo]
    payload = {}
    
    for field in catalog_entry["required"]:
        if field not in accion or accion[field] in (None, ""):
            raise ValueError(f"Falta el campo obligatorio: {field}")
        payload[field] = accion[field]
        
    for field in catalog_entry.get("optional", []):
        if field in accion and accion[field] not in (None, ""):
            payload[field] = accion[field]
            
    payload.pop("idAccion", None)
    payload.pop("idPlanProgramado", None)
    
    return catalog_entry["topic"], payload

def validate_base(data, creating=True):
    vivienda_id = data.get("viviendaId")
    nombre = data.get("nombre")
    estado = data.get("estado", "activo")
    mode = data.get("mode", "single")
    
    if not vivienda_id:
        raise ValueError("viviendaId es obligatorio")
    if not nombre:
        raise ValueError("nombre es obligatorio")
    if estado not in ALLOWED_STATES:
        raise ValueError(f"estado no valido: {estado}")
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode no valido: {mode}")
        
    return vivienda_id, nombre, estado, mode

def row_to_plan(row):
    return {
        "idPlanProgramado": row["idPlanProgramado"],
        "viviendaId": row["viviendaId"],
        "nombre": row["nombre"],
        "activo": bool(row["activo"]),
        "estado": row["estado"],
        "triggerTipo": row["triggerTipo"],
        "triggerConfigJson": parse_json_field(row["triggerConfigJson"], {}),
        "condicionesJson": parse_json_field(row["condicionesJson"], []),
        "btTopic": row["btTopic"],
        "payloadJson": parse_json_field(row["payloadJson"], {}),
        "payloadTemplate": row["payloadTemplate"],
        "automationIdHA": row["automationIdHA"],
        "mode": row["mode"],
        "creadoEn": str(row["creadoEn"]) if row["creadoEn"] else None,
        "actualizadoEn": str(row["actualizadoEn"]) if row["actualizadoEn"] else None,
        "actualizadoPor": row["actualizadoPor"],
        "origen": row["origen"],
    }

@app.get("/back_NUC/planes-programados")
def listar_planes():
    vivienda_id = request.args.get("viviendaId", type=int)
    estado = request.args.get("estado")
    
    if not vivienda_id:
        return jsonify({"error": "viviendaId es obligatorio"}), 400
        
    where = ["viviendaId = %s"]
    params = [vivienda_id]
    
    if estado:
        where.append("estado = %s")
        params.append(estado)
        
    sql = f"""
        SELECT * FROM t_PlanesProgramados 
        WHERE {" AND ".join(where)} 
        ORDER BY estado, nombre, idPlanProgramado
    """
    
    cn = get_db()
    cur = cn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    cn.close()
    
    return jsonify({"planes": [row_to_plan(row) for row in rows]})

@app.post("/back_NUC/planes-programados")
def crear_plan():
    try:
        data = request.get_json(force=True)
        vivienda_id, nombre, estado, mode = validate_base(data)
        trigger_tipo, trigger_config, condiciones = build_trigger(data)
        bt_topic, payload = build_payload_and_topic(data)
        actualizado_por = data.get("actualizadoPor")
        activo = estado_to_activo(estado)
        automation_tmp = f"sorocare_pending_{uuid.uuid4().hex[:12]}"
        
        cn = get_db()
        cur = cn.cursor()
        
        insert_sql = """
            INSERT INTO t_PlanesProgramados (
                viviendaId, nombre, activo, estado, triggerTipo,
                triggerConfigJson, condicionesJson, btTopic, payloadJson,
                payloadTemplate, automationIdHA, mode, actualizadoPor, origen
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'web')
        """
        
        cur.execute(insert_sql, (
            vivienda_id,
            nombre,
            activo,
            estado,
            trigger_tipo,
            json.dumps(trigger_config, ensure_ascii=False),
            json.dumps(condiciones, ensure_ascii=False),
            bt_topic,
            json.dumps(payload, ensure_ascii=False),
            None,
            automation_tmp,
            mode,
            actualizado_por,
        ))
        
        plan_id = cur.lastrowid
        automation_id = f"sorocare_plan_{plan_id}"
        
        cur.execute(
            """
            UPDATE t_PlanesProgramados 
            SET automationIdHA = %s 
            WHERE idPlanProgramado = %s
            """,
            (automation_id, plan_id),
        )
        
        cn.commit()
        cur.close()
        cn.close()
        
        return jsonify({
            "idPlanProgramado": plan_id,
            "automationIdHA": automation_id,
            "status": "created",
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {e}"}), 500

@app.put("/back_NUC/planes-programados/<int:plan_id>")
def editar_plan(plan_id):
    try:
        data = request.get_json(force=True)
        vivienda_id, nombre, estado, mode = validate_base(data, creating=False)
        trigger_tipo, trigger_config, condiciones = build_trigger(data)
        bt_topic, payload = build_payload_and_topic(data)
        actualizado_por = data.get("actualizadoPor")
        activo = estado_to_activo(estado)
        
        cn = get_db()
        cur = cn.cursor()
        
        cur.execute(
            """
            UPDATE t_PlanesProgramados
            SET 
                viviendaId = %s,
                nombre = %s,
                activo = %s,
                estado = %s,
                triggerTipo = %s,
                triggerConfigJson = %s,
                condicionesJson = %s,
                btTopic = %s,
                payloadJson = %s,
                payloadTemplate = NULL,
                mode = %s,
                actualizadoPor = %s,
                origen = 'web'
            WHERE idPlanProgramado = %s
            """,
            (
                vivienda_id,
                nombre,
                activo,
                estado,
                trigger_tipo,
                json.dumps(trigger_config, ensure_ascii=False),
                json.dumps(condiciones, ensure_ascii=False),
                bt_topic,
                json.dumps(payload, ensure_ascii=False),
                mode,
                actualizado_por,
                plan_id,
            ),
        )
        
        cn.commit()
        updated = cur.rowcount
        cur.close()
        cn.close()
        
        if updated == 0:
            return jsonify({"error": "Plan no encontrado"}), 404
            
        return jsonify({"idPlanProgramado": plan_id, "status": "updated"})
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {e}"}), 500

@app.patch("/back_NUC/planes-programados/<int:plan_id>/estado")
def cambiar_estado(plan_id):
    try:
        data = request.get_json(force=True)
        estado = data.get("estado")
        actualizado_por = data.get("actualizadoPor")
        
        if estado not in ALLOWED_STATES:
            return jsonify({"error": f"estado no valido: {estado}"}), 400
            
        activo = estado_to_activo(estado)
        
        cn = get_db()
        cur = cn.cursor()
        
        cur.execute(
            """
            UPDATE t_PlanesProgramados
            SET activo = %s,
                estado = %s,
                actualizadoPor = %s
            WHERE idPlanProgramado = %s
            """,
            (activo, estado, actualizado_por, plan_id),
        )
        
        cn.commit()
        updated = cur.rowcount
        cur.close()
        cn.close()
        
        if updated == 0:
            return jsonify({"error": "Plan no encontrado"}), 404
            
        return jsonify({
            "idPlanProgramado": plan_id,
            "estado": estado,
            "activo": bool(activo),
        })
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {e}"}), 500

@app.delete("/back_NUC/planes-programados/<int:plan_id>")
def eliminar_plan(plan_id):
    cn = get_db()
    cur = cn.cursor()
    
    cur.execute(
        """
        UPDATE t_PlanesProgramados
        SET activo = 0,
            estado = 'eliminado'
        WHERE idPlanProgramado = %s
        """,
        (plan_id,),
    )
    
    cn.commit()
    updated = cur.rowcount
    cur.close()
    cn.close()
    
    if updated == 0:
        return jsonify({"error": "Plan no encontrado"}), 404
        
    return jsonify({"idPlanProgramado": plan_id, "estado": "eliminado"})

@app.get("/back_NUC/planes-programados/catalogos")
def catalogos():
    return jsonify({
        "acciones": [
            {
                "tipo": key,
                "btTopic": value["topic"],
                "required": value["required"],
                "optional": value.get("optional", []),
            }
            for key, value in BT_CATALOG.items()
        ],
        "modes": sorted(ALLOWED_MODES),
        "estados": sorted(ALLOWED_STATES),
        "triggers": ["time", "time_pattern", "state"],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
