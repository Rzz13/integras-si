const axios = require("axios");
const { HttpsProxyAgent } = require("https-proxy-agent");
require("dotenv").config();

const PROXY_CONFIG = {
  host: process.env.PROXY_HOST,
  port: process.env.PROXY_PORT,
  username: process.env.PROXY_USERNAME,
  password: process.env.PROXY_PASSWORD,
};

const TARGET_URL =
  "https://britain-wan-vacation-calculations.trycloudflare.com/students";
const TOTAL_REQUESTS = 500;
const USE_PROXY = true;

let axiosConfig = {
  headers: {
    "Content-Type": "application/xml",
  },
  timeout: 10000,
};

if (USE_PROXY) {
  const auth = `${PROXY_CONFIG.username}:${PROXY_CONFIG.password}`;
  const proxyUrl = `http://${auth}@${PROXY_CONFIG.host}:${PROXY_CONFIG.port}`;
  const agent = new HttpsProxyAgent(proxyUrl);

  axiosConfig.httpAgent = agent;
  axiosConfig.httpsAgent = agent;
}

async function sendPostRequest(index) {
  const nim = 2415355000 + index;
  const xmlPayload =
    `<StudentRequest>` +
    `<NIM>${nim}</NIM>` +
    `<Nama>LoadTester_${index}</Nama>` +
    `<Jurusan>Teknik Komputer</Jurusan>` +
    `<Status>ACTIVE</Status>` +
    `</StudentRequest>`;

  try {
    const response = await axios.post(TARGET_URL, xmlPayload, axiosConfig);
    return { success: true, status: response.status, id: index };
  } catch (error) {
    return {
      success: false,
      status: error.response ? error.response.status : error.code,
      message: error.message,
      id: index,
    };
  }
}

async function runConcurrencyTest() {
  console.log(`==================================================`);
  console.log(`MEMULAI STRESS TEST: ${TOTAL_REQUESTS} REQUEST POST SIMULTAN`);
  console.log(`Target  : ${TARGET_URL}`);
  console.log(
    `Proxy   : ${USE_PROXY ? `${PROXY_CONFIG.host}:${PROXY_CONFIG.port}` : "Disabled"}`,
  );
  console.log(`==================================================\n`);

  const startTime = Date.now();

  const requestPromises = [];
  for (let i = 1; i <= TOTAL_REQUESTS; i++) {
    requestPromises.push(sendPostRequest(i));
  }

  const results = await Promise.all(requestPromises);

  const endTime = Date.now();
  const duration = (endTime - startTime) / 1000;

  // Evaluasi Hasil
  const successCount = results.filter((r) => r.success).length;
  const failCount = results.filter((r) => !r.success).length;

  console.log(`\n==================================================`);
  console.log(`RINGKASAN HASIL TEST`);
  console.log(`==================================================`);
  console.log(`Total Request   : ${TOTAL_REQUESTS}`);
  console.log(`Berhasil        : ${successCount}`);
  console.log(`Gagal           : ${failCount}`);
  console.log(`Waktu Eksekusi  : ${duration.toFixed(2)} detik`);
  console.log(`==================================================`);
}

runConcurrencyTest();
