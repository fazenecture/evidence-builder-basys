import { Pool } from "pg";
import { format, buildWhereFromQuery, transformer } from "sqlutils/pg";
import logger from "../utils/logger";

const {
  DB_HOST,
  DB_PASSWORD,
  DB_PORT = 5432,
  DB_USERNAME,
  DB_NAME,
} = process.env;

const isDev = process.env.NODE_ENV === "development";

const pool = new Pool({
  user: DB_USERNAME,
  password: DB_PASSWORD,
  host: DB_HOST,
  port: parseInt(String(DB_PORT), 10),
  database: DB_NAME,
  ssl: process?.env?.DB_SSL === "true" ? { rejectUnauthorized: false } : undefined,
  options: `-c search_path=core,phi,public`,
});

const wrapClient = (client) => ({
  query: async (text: string, params?: any[]) => {
    const start = Date.now();
    text = text.replace(/\n/g, "");
    if (isDev) console.log("to be executed query", { text });
    const res = await client.query(text, params);
    const duration = Date.now() - start;
    if (isDev) {
      logger.info(
        `executed query ${JSON.stringify({ text, duration, rows: res.rowCount })}`,
      );
    }
    return res;
  },
  release: () => client.release(),
  format,
  buildWhereFromQuery,
  transformer,
});

export default {
  async query(text: string, params?: any[]) {
    const start = Date.now();
    text = text.replace(/\n/g, "");
    if (isDev) console.log("to be executed query", { text });
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    if (isDev) {
      logger.info(
        `executed query ${JSON.stringify({ text, duration, rows: res.rowCount })}`,
      );
    }
    return res;
  },

  async getClient() {
    const client = await pool.connect();
    return wrapClient(client);
  },

  format,
  buildWhereFromQuery,
  transformer,
};
