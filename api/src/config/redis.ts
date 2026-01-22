import Redis from "ioredis";
import logger from "../utils/logger";

const { REDIS_URL } = process.env;

if (!REDIS_URL) {
  throw new Error("REDIS_URL is not defined");
}

const redis = new Redis(REDIS_URL, {
  maxRetriesPerRequest: null,
});

redis.on("connect", () => {
  logger.info("✅ Redis connected");
});

redis.on("error", (err) => {
  logger.error(`❌ Redis error ${err}`);
});

export default redis;
