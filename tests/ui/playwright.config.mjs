import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'.',testMatch:'*.spec.mjs',workers:1,use:{baseURL:process.env.ROLEOS_UI_URL||'http://127.0.0.1:8090/',headless:true},reporter:'list'});
