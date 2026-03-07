import axios from 'axios';

const mlApi = axios.create({
  baseURL: '/ml',
  headers: { 'Content-Type': 'application/json' },
});

export default mlApi;
