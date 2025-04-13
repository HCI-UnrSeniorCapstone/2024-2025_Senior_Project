/**
 * Debug helper to track API calls and report connectivity issues
 */
import axios from 'axios';

// Check direct connectivity to server
export const testDirectConnection = async (url) => {
  try {
    console.log(`Testing direct connection to ${url}...`);
    const response = await axios.get(`${url}/ping`, { timeout: 5000 });
    console.log('Direct connection test successful:', response.data);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('Direct connection test failed:', error.message);
    return { success: false, error: error.message };
  }
};

// Check proxy connection
export const testProxyConnection = async () => {
  try {
    console.log('Testing proxy connection to /api/analytics/health...');
    const response = await axios.get('/api/analytics/health', { timeout: 5000 });
    console.log('Proxy connection test successful:', response.data);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('Proxy connection test failed:', error.message);
    return { success: false, error: error.message };
  }
};

// Modify an existing API call to use proxy instead
export const convertToProxyUrl = (url) => {
  // If URL is already a proxy URL (starts with /api), return it as is
  if (url.startsWith('/api')) {
    return url;
  }
  
  try {
    // Extract the path from the full URL 
    // Example: http://100.82.85.28:5004/get_study_data/1 -> /get_study_data/1
    const urlObj = new URL(url);
    return `/api${urlObj.pathname}${urlObj.search}`;
  } catch (error) {
    console.error('Failed to convert URL to proxy format:', error);
    return url;
  }
};

// Make a request with modified URL for diagnostics
export const tryBothUrls = async (originalUrl) => {
  const results = {};
  
  // Try direct URL first
  try {
    console.log(`Trying direct URL: ${originalUrl}`);
    const directResponse = await axios.get(originalUrl, { timeout: 8000 });
    results.direct = { success: true, data: directResponse.data };
  } catch (error) {
    results.direct = { success: false, error: error.message };
    console.error(`Direct URL failed: ${error.message}`);
  }
  
  // Try proxy URL
  const proxyUrl = convertToProxyUrl(originalUrl);
  try {
    console.log(`Trying proxy URL: ${proxyUrl}`);
    const proxyResponse = await axios.get(proxyUrl, { timeout: 8000 });
    results.proxy = { success: true, data: proxyResponse.data };
  } catch (error) {
    results.proxy = { success: false, error: error.message };
    console.error(`Proxy URL failed: ${error.message}`);
  }
  
  return results;
};

/**
 * Helper that creates an enhanced axios instance for debugging
 */
export const createDebugAxios = () => {
  const instance = axios.create({
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
  
  // Add debug logging to all requests
  instance.interceptors.request.use(config => {
    console.log(`DEBUG - Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  });
  
  // Add debug logging to all responses
  instance.interceptors.response.use(
    response => {
      console.log(`DEBUG - Response: ${response.status} ${response.config.url}`);
      return response;
    },
    error => {
      console.error(`DEBUG - Error: ${error.message}`, error.config?.url);
      return Promise.reject(error);
    }
  );
  
  return instance;
};

export default {
  testDirectConnection,
  testProxyConnection,
  convertToProxyUrl,
  tryBothUrls,
  createDebugAxios
};