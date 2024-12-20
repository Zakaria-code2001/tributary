# import dependencies
import json
import redis as redis
from flask import Flask, request
from loguru import logger

# define constants
HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

app = Flask(__name__)


@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200


@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) collect request --- {json.dumps(payload)} (*)")

    current_engine_temperature = payload.get("engine_temperature")
    logger.info(f"The current engine temperature is: {current_engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.rpush(DATA_KEY, current_engine_temperature)

    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    engine_temperature_values = [float(temp) for temp in engine_temperature_values]

    total = 0
    number_of_temp = len(engine_temperature_values)
    for temp in engine_temperature_values:
        total += temp

    if number_of_temp > 0:
        average = total / number_of_temp
    else:
        average = 0

    logger.info(f"The average of temperatures is: {average}")

    return {"success": True}, 200